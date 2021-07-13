import ast
import logging

logging.basicConfig(level=logging.WARNING)
# logging.basicConfig(level=logging.DEBUG)

test_source_file = "type-annotations-experiment-test.py"

with open(test_source_file) as f:
    test_source = f.read()

test_ast = ast.parse(test_source,
                     filename=test_source_file,
                     type_comments=True)

# print(ast.dump(test_ast))

## TODO: Maybe move all the static methods to an ast_util file

class ServiceClassFinder(ast.NodeVisitor):
    def __init__(self):
        self.services = []

    ## TODO: Make this test more proper
    @staticmethod
    def _is_service_decorator(decorator):
        ## Should be equal to the following
        ##
        ## Q: Do we need to assert the ctx too?
        # Attribute(value=Name(id='decorators', ctx=Load()), attr='service', ctx=Load())])
        cond = (isinstance(decorator, ast.Attribute)
                and isinstance(decorator.value, ast.Name)
                and decorator.value.id == 'decorators'
                and decorator.attr == 'service')
        return cond

    ## TODO: It would be good to define a test that ensures that a class is a well-formed service,
    ##       checking our assumptions.
    @staticmethod
    def is_service_class(node):
        decorators = node.decorator_list
        return any([ServiceClassFinder._is_service_decorator(decorator) 
                    for decorator in decorators])
    
    ## Override the FunctionDef visitor
    def visit_ClassDef(self, node):
        # print(node.name)
        # print(node.decorator_list)
        if(ServiceClassFinder.is_service_class(node)):
            print("Service:", node.name)
            self.services.append(node)

        ## Necessary to visit all the children 
        self.generic_visit(node)

## Find all service definitions in the source file.
##
## Q: Do we want to assume there is just one of them?
##
## This function abstracts that away (acts like a front-end) and can therefore change
## depending on how we decide to implement the annotations.
def find_services(ast_node):
    service_finder = ServiceClassFinder()
    service_finder.visit(ast_node)
    return service_finder.services


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

## A class that finds all the fields of a service object and separates them into persistent and not persistent.
##
## Assumption: All fields are initialized when calling __init__
class StateFinder(ast.NodeVisitor):
    def __init__(self):
        ## Contains the state of a service, namely its persistent and non-persistent fields,
        ## as well as its thrift clients (which are also non-persistent fields).
        self.service_state = ServiceState()
        self.in_init = False

    @staticmethod
    def is_self_name(node):
        ## TODO: What about ctx?
        # Name(id='self', ctx=Load())
        cond = (isinstance(node, ast.Name)
                and node.id == 'self')
        return cond

    ## This function finds the __init__ and then searches for all field initializations in it.
    def visit_FunctionDef(self, node: ast.FunctionDef):
        if(node.name == '__init__'):
            ## We don't expect function definitions in __init__
            assert(not self.in_init)
            logging.debug("Function init: " + node.name)
            # print(ast.dump(node))

            self.in_init = True
            ## TODO: Assert that __init__ only takes self as an argument

            ## TODO: Populate service fields
            ## We only need to visit the children in the __init__ function
            self.generic_visit(node)

    ## Is there any other statement node that we want to follow?
    def visit_Assign(self, node: ast.Assign):
        ## We don't expect any assignments outside of __init__
        assert(self.in_init)

        # print(ast.dump(node))

        ## TODO: Relax the following assumptions accordingly

        ## Only a single target (lval)
        assert(len(node.targets) == 1)
        target = node.targets[0]
        ## The lval needs to be an attribute access to self
        assert(isinstance(target, ast.Attribute))
        assert(StateFinder.is_self_name(target.value))
        field_name = target.attr
        logging.debug("Field name: " + field_name)
        init_ast = target.value
        logging.debug("Init AST: " + ast.dump(init_ast))
        self.service_state.add_field(field_name, init_ast, node.type_comment)


all_services = find_services(test_ast)

for service in all_services:
    # print(ast.dump(service))

    ## TODO: Find init
    field_finder = StateFinder()
    field_finder.visit(service)
    service_state = field_finder.service_state
    print("Service State:", service_state)


## High level Q: Is it possible to perform all changes dynamically? That is, instead of
##               compiling the AST, simply decorating the class and making sure that it implements
##               methods that give us this information? For example, if it implements a static method that
##               gives us the fields names, as well as whether they are persistent or not.