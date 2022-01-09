## This is a class that describes the state of an object.
##
## TODO: Figure out what the correct structure is for this class
##
## TODO: This class also probably needs to contain the initialization functions for all the fields.
##       These initialization ASTs need to be deterministic and pure.
import ast

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

    ## TODO: What other fields do we need here? Maybe the actual client name?
    def add_client(self, name, init_ast):
        self.clients[name] = init_ast

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

    ## TODO: Add method arguments!
    def __repr__(self):
        out = "Service: " + self.name() + '\n'
        out += self.state.__repr__() + '\n'
        out += 'Service Methods:\n'
        for method in self.methods:
            # print("Method: " + method)
            # out += ast.dump(method) + '\n'
            out += '|-- ' + method.name + '\n'
        return out
    