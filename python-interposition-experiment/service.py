## This is a class that describes the state of an object.
##
## TODO: Figure out what the correct structure is for this class
##
## TODO: This class also probably needs to contain the initialization functions for all the fields.
##       These initialization ASTs need to be deterministic and pure.
class ServiceState:
    def __init__(self):
        self.persistent_fields = {}
        self.temporary_fields = {}
        self.thrift_clients = {}
    
    def __str__(self):
        ret_list = ["Service State:"]
        ret_list.append("|-- Persistent: " + str(self.persistent_fields))
        ret_list.append("|-- Temporary: " + str(self.temporary_fields))
        ret_list.append("|-- Thrift Clients: " + str(self.thrift_clients))
        return "\n".join(ret_list)

    ## TODO: Do we need an initialization function for persistent field??
    def add_persistent_field(self, name, init_ast):
        self.persistent_fields[name] = init_ast

    ## TODO: What other fields do we need here? Maybe the actual client name?
    def add_thrift_client(self, name, init_ast):
        self.thrift_clients[name] = init_ast

    ## This function determines what kind of field that is (based on the type annotation)    
    def add_field(self, name, init_ast, type):
        ## TODO: Make that more robust
        if(type.startswith('Persistent')):
            self.add_persistent_field(name, init_ast)
        elif(type == 'ThriftClient'):
            self.add_thrift_client(name, init_ast)
        else:
            assert(False)
