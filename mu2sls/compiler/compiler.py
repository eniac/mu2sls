import ast

from compiler import frontend, backend

## This function compiles a python module containing the definition of a service
def compile_single_method_service_module(in_file: str, out_file: str, sls_backend: str='openfaas'):
     ## Read the input file and parse it
    with open(in_file) as f:
        test_source = f.read()

    test_ast = ast.parse(test_source,
                        filename=in_file,
                        type_comments=True)


    ## Parse the AST to acquire the services and their states.
    services = frontend.parse_services(test_ast)

    assert(len(services) == 1)
    service = services[0]

    ## TODO: Create a method that compiles a multiple method service, each to a different serverless function handler
    # assert(len(service.methods) == 1)

    target_service_ast = backend.service_to_ast(service)

    ## Replace the service in the original module ast
    replacer = frontend.ServiceClassReplacer(service.name(), target_service_ast)
    replaced_ast = replacer.visit(test_ast)

    # Add imports
    import_adder = backend.AddImports()
    final_ast = import_adder.visit(test_ast)

    ## TODO: Potentially extend this
    assert(sls_backend == 'openfaas')

    ## TODO: Add the handler function for a single method
    ##       For now (without thrift), the handler should look a little like this.
    ##
    ## def handle(req):
    ##     service = Service()
    ##     ret = service.method(req)
    ##     return ret

    fixed_lines_final_ast = ast.fix_missing_locations(final_ast)

    _decompiled = backend.ast_to_source(fixed_lines_final_ast, out_file)
