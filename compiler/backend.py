import logging
logger = logging.getLogger(__name__)

from compiler import globals
from compiler.ast_utils import *
from compiler.service import Service

import ast

from uncompyle6.main import decompile

STORE_FIELD_NAME = "logger"
STORE_INIT_ENV_METHOD = "init_env"
STORE_INIT_ENV_INVOCATION = f'{STORE_FIELD_NAME}.{STORE_INIT_ENV_METHOD}(self.__class__.__name__)'

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

##
## Wrapper Terminals and thew source persistent objects can not be copied by reference,
## all of their accesses happen through their interface.
##
## TODO: We need to make sure that passing of another terminal
##       does not override this terminal except in case of initialization.
##
## WARNING: WrapperTerminals cannot return their value if they are not called with a method.
##
##          Therefore, the very simple xample of
##            x = persistent_field
##          doesn't work since we don't know dynamically dwhether the persistent field is going
##          ro be used to then access one of its methods or simply to pass its value.
##
## TODO: Investigate whether we can solve this problem and support simple assignments.
def construct_descriptor_ast(field_name: str):
    descriptor_module_ast = ast.parse("class " + descriptor_class_name(field_name) + ":" """
        def __get__(self, obj, objtype=None):
            # logging.info('Accessing collection')
            # print('Accessing: """ + field_name+ """')
            # print(objtype)
            value = obj._wrapper_""" + field_name + """
            # print(value)
            # print(type(value))
            return value

        def __set__(self, obj, value):
            # logging.info('Setting collection')
            if(isinstance(value, wrappers.Wrapper)):
                # logging.info('Collection initialized')
                # print('Collection initialized')
                obj._wrapper_""" + field_name + """ = value
            else:
                # print('Writing to: """ + field_name+ """')
                # print(value)
                # print(type(value))
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
                                              make_self_field_access(STORE_FIELD_NAME)],
                                            #   ast.Name(id=STORE_FIELD_NAME, ctx=ast.Load())],
                                        keywords=[]))

    return [assgn1, assgn2, assgn3]

def construct_init_method_ast(persistent_objects):
    body = []

    ## First initialize Beldi's environment
    beldi_ass_module_ast = ast.parse(STORE_INIT_ENV_INVOCATION)
    beldi_ass_ast = extract_single_stmt_from_module(beldi_ass_module_ast)
    body.append(beldi_ass_ast)

    ## Keep the logger in a local field
    assgn_logger = make_field_assign(STORE_FIELD_NAME, make_var_expr(STORE_FIELD_NAME))
    body.append(assgn_logger)

    ## Then initialize all the objects
    # for per_obj_name, per_obj_init_ast in persistent_objects.items():
    #     body += construct_init_method_persistent_object_ast(per_obj_name, per_obj_init_ast)

    ## Create the function
    function_ast = ast.FunctionDef(name='__init__', 
                                   args=ast.arguments(posonlyargs=[], 
                                                      args=[make_arg('self'),
                                                            make_arg(STORE_FIELD_NAME)],
                                                      vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), 
                                   body=body, 
                                   decorator_list=[], returns=None, type_comment=None)
    return function_ast

def construct_object_init_ast(persistent_objects):
    body = []
    ## Then initialize all the objects
    for per_obj_name, per_obj_init_ast in persistent_objects.items():
        body += construct_init_method_persistent_object_ast(per_obj_name, per_obj_init_ast)
    
    if len(body) == 0:
        body = [ast.Pass()]
        
    ## Create the function
    function_ast = ast.FunctionDef(name='__init_per_objects__', 
                                   args=ast.arguments(posonlyargs=[], 
                                                      args=[make_arg('self')],
                                                      vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]), 
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

    ## Creates a method that initializes persistent objects
    ##
    ## It needs to be called after init to have a request identifier
    object_init_method = construct_object_init_ast(persistent_objects)

    ## Instead of making these methods that are always the same,
    ## we simply inherit them from a superclass.
    compiled_service_base_class = make_var_expr('CompiledService')

    ## Modify Invocations and transactions to have the correct target (self.client instead of class name)
    new_methods = []
    for method in service.methods:
        invocationModifier = ChangeInvokeTarget(service.state.get_clients_class_name_to_fields())
        new_method = invocationModifier.visit(method)
        new_methods.append(new_method)

    body = assignments + [init_method, object_init_method] + new_methods
    
    new_class = ast.ClassDef(name=service.name(),
                             bases= [compiled_service_base_class] + service.bases(),
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
        import_stmts.append(make_import_from('runtime.compiled_service', 'CompiledService'))

        ## It might make sense to also have this be a separate module that is imported 
        ##   from the deployment script and not actually being done in the backend.
        ##
        ## Now we have mixed responsibility of choosing a runtime library to import in the compiler.
        ##
        ## But the compiler should probably create code that is agnostic to the
        ##   invocation library. Similarly to how it is agnostic to the store.
        if (self.sls_backend == 'knative'):
            ## TODO: Do this import in the BeldiLogger object
            # import_stmts.append(make_import_from('runtime.knative.invoke', '*'))
            import_stmts.append(make_import_from(globals.WEB_FRAMEWORK.lower(), globals.WEB_FRAMEWORK))
            import_stmts.append(make_import_from(globals.WEB_FRAMEWORK.lower(), 'request'))
            import_stmts.append(make_import_from('runtime.beldi', 'logger'))
            import_stmts.append(ast.Import(names=[ast.alias(name='json')]))
        
        node.body = import_stmts + node.body

        self.modules += 1
        return node


## This class changes invocations to go through logger
class ChangeInvokeTarget(ast.NodeTransformer):
    def __init__(self, clients):
        ## Clients is a dictionary from class names to field names
        self.clients_class_to_field = clients

    def visit_Call(self, node: ast.Call):
        # print(ast.dump(ast.parse('SyncInvoke("Client", "Call", args, args2)')))

        ## First visit all children
        self.generic_visit(node)

        try:
            func_name = call_func_name(node)
            if func_name in globals.INVOKE_LIB_FUNCTION_NAMES + globals.TXN_FUNCTION_NAMES:
                node.func = make_field_access(['self', STORE_FIELD_NAME, func_name])
            return node
        except:
            return node

## TODO: Investigate ways to do that without generating Python AST. 
##       Maybe by having a Flask/Quart file that imports the module and programmatically sets the routes?
class AddFlask(ast.NodeTransformer):
    def __init__(self, service_name, method_names, clients):
        self.modules = 0
        self.service_name = service_name
        self.method_names = method_names
        self.clients_class_to_field = clients

    ## TODO: At the moment this only works for a single module that is at the top level
    def visit_Module(self, node: ast.Module):
        ## TODO: Do we need this assumption that there is only one module?
        assert(self.modules == 0)
        flask_init = make_var_assign('app', ast.Call(func=ast.Name(id=globals.WEB_FRAMEWORK, ctx=ast.Load()), 
                                                     args=[ast.Name(id='__name__', ctx=ast.Load())], keywords=[]))
        instance_init = make_var_assign('instance',
                                        ast.Call(func=ast.Name(id=self.service_name, ctx=ast.Load()),
                                                 args=[ast.Call(func=ast.Attribute(value=ast.Name(id='logger', ctx=ast.Load()), attr=globals.BELDI_LOGGER_CLASS_NAME, ctx=ast.Load()), args=[], keywords=[])],
                                                 keywords=[]))

        ## We use the client list of the service to make an identity dictionary.
        ##
        ## Note however, that if not all services are in knative, then we need different types of clients.
        client_list_constant = make_constant_list(sorted(list(self.clients_class_to_field.keys())))
        client_list_assign = make_var_assign('client_list', client_list_constant)
        clients_init = ast.parse("instance.init_clients({ k: k for k in client_list })").body

        ## TODO: Investigate whether this can be moved out
        ##       by reinitializing the environment per request,
        ##       and have a read-only instance initialized once at the start.
        ##
        ## The initialization of the instance and its clients
        pre_body = [instance_init, client_list_assign] + clients_init

        flask_routes = []
        for method in self.method_names:
            ## TODO: Do we actually need to have json.dumps here? This would require all our outputs to be json (which might need some modifying on the app side).
            ##
            ## TODO: Make all method arguments be keyword ones, so that we can get rid of the extra `args`
            ##       and just pass a dictionary with arguments and their values.
            ##
            ## We are using `get_json` instead of params since it is more robust to send data
            ## using the data http field rather than the url parameters.
            ## 
            ## Older way:
            ## body = ast.parse(f"return json.dumps((instance.{method})(*request.args.to_dict()['args']))").body            
            ## Old way
            ## body = ast.parse(f"instance.set_env(request)\nreturn json.dumps((instance.{method})(*request.get_json()['args']))").body
            
            body = ast.parse(f"return await instance.apply_request('{method}', request)").body
            route = ast.AsyncFunctionDef(name=method, args=ast.arguments(posonlyargs=[], args=[], vararg=None, kwonlyargs=[], kw_defaults=[], kwarg=None, defaults=[]),
                            body=(pre_body + body),
                            decorator_list=[ast.Call(func=ast.Attribute(value=ast.Name(id='app', ctx=ast.Load()), attr='route', ctx=ast.Load()), args=[ast.Constant(value=f'/{method}', kind=None)], keywords=[ast.keyword(arg='methods', value=ast.List(elts=[ast.Constant(value='GET', kind=None), ast.Constant(value='POST', kind=None)], ctx=ast.Load()))])],
                        )
            flask_routes.append(route)

        ## TODO: Probably useless and can be deleted
        main_func = ast.parse("if __name__ == '__main__':\n    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))")
        node.body = [flask_init] + node.body + flask_routes + [main_func.body[0]]

        self.modules += 1
        return node