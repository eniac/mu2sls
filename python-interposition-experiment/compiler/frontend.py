import ast
import logging

from compiler.service import ServiceState

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


def find_service_state(service_ast):
    ## TODO: Also find init
    field_finder = StateFinder()
    field_finder.visit(service_ast)
    service_state = field_finder.service_state
    return service_state

def parse_services(ast_node):
    all_services = find_services(ast_node)
    all_service_states = [find_service_state(service) for service in all_services]
    return all_service_states

