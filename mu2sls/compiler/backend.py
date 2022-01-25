import logging
logger = logging.getLogger(__name__)

from compiler.ast_utils import *
from compiler.service import Service

import ast

from uncompyle6.main import decompile

STORE_FIELD_NAME = "store"
STORE_INIT_ENV_METHOD = "init_env"
STORE_INIT_ENV_INVOCATION = f'{STORE_FIELD_NAME}.{STORE_INIT_ENV_METHOD}()'

CLIENTS_ARG_NAME = 'clients'

## TODO: Check ast.unparse in python 3.9
##
## This function takes an AST and saves python_source code in the out_file
def ast_to_source(ast_node, out_file):
    ## TODO: Do we need the filename
    ##
    ## TODO: This is very wasteful, we should not need to first compile to bytecode before deparsing.
    code_object = compile(ast_node, filename="<ast>", mode="exec")

    ## TODO: Do we actually need the bytecode version?
    ##       By default uncompyle should use the interpreter version.
    ##
    ## TODO: It seems that uncompyle does not produce comments in the code,
    ##       meaning that they are lost.
    bytecode_version=None
    with open(out_file, "w") as out_f:
        decompiled_code = decompile(bytecode_version,
                                    code_object,
                                    out=out_f)
    
    ## TODO: I am not sure what this object is and whether we need it
    return decompiled_code

## TODO: Make that more principled. What is the most principled way to generate this code?
def extract_single_stmt_from_module(module_ast: ast.Module):
    assert(len(module_ast.body) == 1)
    return module_ast.body[0]

def descriptor_class_name(field_name: str) -> str:
    return "Wrapper" + field_name

def field_store_key_name(field_name: str) -> str:
    return "test-" + field_name

def construct_descriptor_ast(field_name: str):
    descriptor_module_ast = ast.parse("class " + descriptor_class_name(field_name) + ":" """
        def __get__(self, obj, objtype=None):
            # logging.info('Accessing collection')
            value = obj._wrapper_""" + field_name + """
            return value

        def __set__(self, obj, value):
            # logging.info('Setting collection')
            if(isinstance(value, wrappers.WrapperTerminal)):
                # logging.info('Collection initialized')
                obj._wrapper_""" + field_name + """ = value
            else:
                obj._wrapper_""" + field_name + """._wrapper_set(value)""")
    return extract_single_stmt_from_module(descriptor_module_ast)

def descriptor_init_value_ast(field_name: str):
    init_val_ast = ast.Call(func=ast.Name(id=descriptor_class_name(field_name),
                                          ctx=ast.Load()),
                            args=[],
                            keywords=[])
    return init_val_ast

def persistent_object_target_init_ast(persistent_object_name, _persistent_object_init_ast):
    value = descriptor_init_value_ast(persistent_object_name)
    assign_node = ast.Assign(targets=[ast.Name(id=persistent_object_name, ctx=ast.Store())],
                             value=value)
    return assign_node

def construct_init_method_persistent_object_ast(per_obj_name: str, per_obj_init_ast: ast.AST):
    beldi_key_var_name = per_obj_name + '_key'
    init_val_var_name = per_obj_name + "_init_val"

    # collection_key = "test-collection"
    assgn1 = make_var_assign(beldi_key_var_name, 
                             ast.Constant(value=field_store_key_name(per_obj_name), kind=None))
    
    # collection_init_val = []
    assgn2 = make_var_assign(init_val_var_name, per_obj_init_ast)
    
    # self.collection = wrappers.wrap_terminal(collection_key, collection_init_val, self.beldi)
    assgn3 = make_field_assign(per_obj_name,
                               ast.Call(func=ast.Attribute(value=ast.Name(id='wrappers', ctx=ast.Load()), attr='wrap_terminal', ctx=ast.Load()), 
                                        args=[ast.Name(id=beldi_key_var_name, ctx=ast.Load()), 
                                              ast.Name(id=init_val_var_name, ctx=ast.Load()),
                                              ast.Name(id=STORE_FIELD_NAME, ctx=ast.Load())],
                                        keywords=[]))

    return [assgn1, assgn2, assgn3]

def construct_init_method_ast(persistent_objects):
    body = []

    # First initialize Beldi's environment
    beldi_ass_module_ast = ast.parse(STORE_INIT_ENV_INVOCATION)
    beldi_ass_ast = extract_single_stmt_from_module(beldi_ass_module_ast)
    body.append(beldi_ass_ast)

    ## Then initialize all the objects
    for per_obj_name, per_obj_init_ast in persistent_objects.items():
        body += construct_init_method_persistent_object_ast(per_obj_name, per_obj_init_ast)

    ## Create the function
    function_ast = ast.FunctionDef(name='__init__', 
                                   args=ast.arguments(posonlyargs=[], 
                                                      args=[make_arg('self'),
                                                            make_arg('store')],
                                                      vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), 
                                   body=body, 
                                   decorator_list=[], returns=None, type_comment=None)
    return function_ast

def construct_init_clients_method_ast(clients):
    body = []

    ## Initialize the clients
    for field_name, client in clients.items():
        _init_ast, client_name = client

        ## Assign the client based on the clients dictionary
        assignment = make_field_assign(field_name, make_constant_subscript(CLIENTS_ARG_NAME, client_name))
        body.append(assignment)
    else:
        ## If there are no clients, make an empty function
        body.append(ast.Pass())

    ## Create the function
    function_ast = ast.FunctionDef(name='init_clients', 
                                   args=ast.arguments(posonlyargs=[], 
                                                      args=[make_arg('self'),
                                                            make_arg(CLIENTS_ARG_NAME)],
                                                      vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, 
                                                      defaults=[make_empty_dict()]), 
                                   body=body, 
                                   decorator_list=[], returns=None, type_comment=None)
    return function_ast

## TODO: Not sure if this should be a method of Service or a function here
def service_to_ast(service: Service):
    logger.info(str(service))

    ## TODO: For now only work for persistent fields and thrift
    persistent_objects = service.state.persistent_fields
    assignments = []
    for per_obj_name, per_obj_init_ast in persistent_objects.items():
        
        ## Create the descriptor for the field to wrap its accesses
        descriptor_ast = construct_descriptor_ast(per_obj_name)

        ## Create the assignment
        target_ast = persistent_object_target_init_ast(per_obj_name, per_obj_init_ast)
        assignments += [descriptor_ast, target_ast]

    ## TODO: Do something about thrift

    ## Creates an init function that initializes beldi and all the objects
    ##
    ## TODO: This should take some form of configuration to use beldi or not
    init_method = construct_init_method_ast(persistent_objects)

    ## Create the method that initializes clients
    init_clients_method = construct_init_clients_method_ast(service.state.clients)

    body = assignments + [init_method] + [init_clients_method] + service.methods
    
    new_class = ast.ClassDef(name=service.name(),
                             bases=service.bases(),
                             keywords=service.keywords(),
                             body=body,
                             decorator_list=service.decorator_list())
    
    # print(ast.dump(new_class))  
    fixed_lines_class = ast.fix_missing_locations(new_class)
    return fixed_lines_class


## This class adds the necessary imports to the final module
class AddImports(ast.NodeTransformer):
    def __init__(self, sls_backend):
        self.modules = 0
        self.sls_backend = sls_backend

    ## TODO: At the moment this only works for a single module that is at the top level
    def visit_Module(self, node: ast.Module):
        ## TODO: Do we need this assumption that there is only one module?
        assert(self.modules == 0)

        import_stmts = []
        import_stmts.append(make_import_from('runtime', 'wrappers'))

        ## It might make sense to also have this be a separate module that is imported 
        ##   from the deployment script and not actually being done in the backend.
        ##
        ## Now we have mixed responsibility of choosing a runtime library to import in the compiler.
        ##
        ## But the compiler should probably create code that is agnostic to the
        ##   invocation library. Similarly to how it is agnostic to the store.
        if (self.sls_backend == 'local'):
            import_stmts.append(make_import_from('runtime.local.invoke', '*'))
        else:
            ## We haven't implemented a backend for non local deployments yet
            raise NotImplementedError()
        node.body = import_stmts + node.body

        self.modules += 1
        return node