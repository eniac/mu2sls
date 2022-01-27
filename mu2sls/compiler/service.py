## This is a class that describes the state of an object.
##
## TODO: Figure out what the correct structure is for this class
##
## TODO: This class also probably needs to contain the initialization functions for all the fields.
##       These initialization ASTs need to be deterministic and pure.
import ast

from compiler.ast_utils import *

class ServiceState:
    def __init__(self):
        self.persistent_fields = {}
        self.temporary_fields = {}
        self.clients = {}
    
    def __repr__(self):
        ret_list = ["Service State:"]
        ret_list.append("|-- Persistent: " + str(self.persistent_fields))
        ret_list.append("|-- Temporary: " + str(self.temporary_fields))
        ret_list.append("|-- Clients: " + str(self.clients))
        return "\n".join(ret_list)

    ## TODO: Do we need an initialization function for persistent field??
    def add_persistent_field(self, name, init_ast):
        self.persistent_fields[name] = init_ast

    ## TODO: Instead of finding clients through this awkward clientFactory convention,
    ##       find them simply using syncInvoke and the name of the class.
    ##
    ##       The source spec doesn't need to know anything about the client object.
    ##
    ## TODO: Remove this method as it is now obsolete
    def add_client(self, field_name, init_ast):
        ## The call function name should be client factory
        assert(call_func_name(init_ast) == 'clientFactory')

        ## There should be only one arg, containing a name
        args_asts = call_func_args(init_ast)
        assert(len(args_asts) == 1)

        client_name = expr_constant_value(args_asts[0])

        self.clients[field_name] = (init_ast, client_name)

    ## Instead of declaring the clients up fornt, we can just run a simple analysis
    ## and find all invocations to them in the code.
    def add_client_from_invoke(self, client_name):
        field_name = f'{client_name}_client'
        ## TODO: It should be fine not having an AST right?
        self.clients[field_name] = (None, client_name)


    ## This function determines what kind of field that is (based on the type annotation)    
    def add_field(self, name, init_ast, type):
        ## TODO: Make that more robust
        if(type.startswith('Persistent')):
            self.add_persistent_field(name, init_ast)
        ## TODO: Maybe have different client types?
        elif(type == 'Client'):
            self.add_client(name, init_ast)
        else:
            print("Error: Field:", name, "has no type in comments!!")
            assert(False)

    ## This returns a dictionary of the client class names to fields
    def get_clients_class_name_to_fields(self):
        ret = {}
        for field_name, item in self.clients.items():
            _ast, class_name = item
            ret[class_name] = field_name
        return ret


class Service:
    def __init__(self, state: ServiceState, methods, service_ast: ast.ClassDef):
        self.state = state
        self.methods = methods
        self.service_ast = service_ast

        ## TODO: Lift these assumptions
        assert(len(service_ast.keywords) == 0)
    
    def name(self):
        return self.service_ast.name
    
    def bases(self):
        return self.service_ast.bases

    def keywords(self):
        assert(len(self.service_ast.keywords) == 0)
        return self.service_ast.keywords

    ## Maybe we need to remove the service decorator
    def decorator_list(self):
        return self.service_ast.decorator_list

    def __repr__(self):
        out = "Service: " + self.name() + '\n'
        out += self.state.__repr__() + '\n'
        out += 'Service Methods:\n'
        for method in self.methods:
            # print("Method: " + method)
            # out += ast.dump(method) + '\n'
            ## TODO: Doesn't print kwargs etc
            arg_names = ", ".join([arg.arg for arg in (method.args.posonlyargs + method.args.args)])
            out += f'|-- {method.name}({arg_names}) \n'
        return out
    