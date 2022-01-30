import logging
logger = logging.getLogger(__name__)

from compiler import globals
from compiler.ast_utils import *
from compiler.service import Service

import ast

from uncompyle6.main import decompile

STORE_FIELD_NAME = "store"
STORE_INIT_ENV_METHOD = "init_env"
# TODO: Fix that:
# STORE_INIT_ENV_INVOCATION = f'{STORE_FIELD_NAME}.{STORE_INIT_ENV_METHOD}(self.__class__.__name__)'
STORE_INIT_ENV_INVOCATION = f'{STORE_FIELD_NAME}.{STORE_INIT_ENV_METHOD}'

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

    ## Modify Invocations to have the correct target (self.client instead of class name)
    new_methods = []
    for method in service.methods:
        invocationModifier = ChangeInvokeTarget(service.state.get_clients_class_name_to_fields())
        new_method = invocationModifier.visit(method)
        new_methods.append(new_method)
        new_methods.append(method)

    body = assignments + [init_method] + [init_clients_method] + new_methods
    
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
        elif (self.sls_backend == 'knative'):
            import_stmts.append(make_import_from('runtime.knative.invoke', '*'))

            ## TODO: We might not need these two
            import_stmts.append(make_import_from('runtime', 'store_stub'))
            import_stmts.append(ast.Import(names=[ast.alias(name='json')]))
        else:
            ## We haven't implemented a backend for non local deployments yet
            raise NotImplementedError()
        node.body = import_stmts + node.body

        self.modules += 1
        return node


## This class adds the necessary imports to the final module
class ChangeInvokeTarget(ast.NodeTransformer):
    def __init__(self, clients):
        ## Clients is a dictionary from class names to field names
        self.clients_class_to_field = clients

    def visit_Call(self, node: ast.Call):
        # print(ast.dump(ast.parse('SyncInvoke("Client", "Call", args, args2)')))

        ## First visit all children
        self.generic_visit(node)

        try:
            if call_func_name(node) in globals.INVOKE_FUNCTION_NAMES:
                ## The first argument is the name of another service class
                args = call_func_args(node)
                first_arg_value = expr_constant_value(args[0])
                field_name = self.clients_class_to_field[first_arg_value]

                ## Change the first argument to call the client
                new_args = args[:] 
                new_args[0] = make_self_field_access(field_name)
                node.args = new_args
            return node
        except:
            return node

class AddFlask(ast.NodeTransformer):
    def __init__(self, service_name, method_names):
        self.modules = 0
        self.service_name = service_name
        self.method_names = method_names

    ## TODO: At the moment this only works for a single module that is at the top level
    def visit_Module(self, node: ast.Module):
        ## TODO: Do we need this assumption that there is only one module?
        assert(self.modules == 0)

        import_stmts = []
        import_stmts.append(make_import_from('flask', 'Flask'))
        import_stmts.append(make_import_from('flask', 'request'))
        flask_init = ast.Assign(targets=[ast.Name(id='app', ctx=ast.Store())],
                                value=ast.Call(func=ast.Name(id='Flask', ctx=ast.Load()), args=[ast.Name(id='__name__', ctx=ast.Load())], keywords=[]))
        instance_init = ast.Assign(targets=[ast.Name(id='instance', ctx=ast.Store())],
                                   value=ast.Call(func=ast.Name(id=self.service_name, ctx=ast.Load()),
                                                  args=[ast.Call(func=ast.Attribute(value=ast.Name(id='store_stub', ctx=ast.Load()), attr='Store', ctx=ast.Load()), args=[], keywords=[])],
                                                  keywords=[]))
        flask_routes = []
        for method in self.method_names:
            body = ast.parse(f"return json.dumps((instance.{method})(**request.args.to_dict()))").body
            route = ast.FunctionDef(name=method, args=ast.arguments(posonlyargs=[], args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
                        body=body,
                        decorator_list=[ast.Call(func=ast.Attribute(value=ast.Name(id='app', ctx=ast.Load()), attr='route', ctx=ast.Load()), args=[ast.Constant(value=f'/{method}', kind=None)], keywords=[ast.keyword(arg='methods', value=ast.List(elts=[ast.Constant(value='GET', kind=None), ast.Constant(value='POST', kind=None)], ctx=ast.Load()))])],
                    )
            flask_routes.append(route)
        main_func = ast.parse("if __name__ == '__main__':\n    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))")
        node.body = import_stmts + [flask_init] + node.body + [instance_init] + flask_routes + [main_func.body[0]]
        # node.body = import_stmts + node.body + [instance_init] + [main_func.body[0]]

        self.modules += 1
        return node