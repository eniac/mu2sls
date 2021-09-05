import ast
import logging

from compiler.service import Service, ServiceState

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
    
    @staticmethod
    def is_service_class_with_name(node, service_name: str):
        if ServiceClassFinder.is_service_class(node):
            # print(ast.dump(node))
            return node.name == service_name
    
    ## Override the FunctionDef visitor
    def visit_ClassDef(self, node):
        # print(node.name)
        # print(node.decorator_list)
        if(ServiceClassFinder.is_service_class(node)):
            logging.debug("Service: " + node.name)
            self.services.append(node)

        ## Necessary to visit all the children 
        self.generic_visit(node)

## This class replaces a service in a module with the compiled service
class ServiceClassReplacer(ast.NodeTransformer):
    def __init__(self, service_name: str, compiled_service_ast: ast.AST):
        self.service_name = service_name
        self.compiled_service_ast = compiled_service_ast
    
    ## TODO: At the moment this only works for a single service that is at the top level
    def visit_ClassDef(self, node: ast.ClassDef):
        # print(node.name)
        # print(node.decorator_list)
        if(ServiceClassFinder.is_service_class_with_name(node, self.service_name)):
            logging.debug("Service: " + node.name)
            return self.compiled_service_ast

        ## Necessary to visit all the children 
        return node

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
        init_ast = node.value
        logging.debug("Init AST: " + ast.dump(init_ast))
        self.service_state.add_field(field_name, init_ast, node.type_comment)


def find_service_state(service_ast):
    ## TODO: Also find init
    field_finder = StateFinder()
    field_finder.visit(service_ast)
    service_state = field_finder.service_state
    return service_state

## A class that finds all the methods of a service object
##
## Assumption: __init__ does not contain any useful code
class MethodFinder(ast.NodeVisitor):
    def __init__(self):
        ## Contains the state of a service, namely its persistent and non-persistent fields,
        ## as well as its thrift clients (which are also non-persistent fields).
        self.methods = []

    ## This function finds the __init__ and then searches for all field initializations in it.
    def visit_FunctionDef(self, node: ast.FunctionDef):
        ## ASSUMPTION: __init__ doesn't contain any useful code except for objects
        if(node.name != '__init__'):
            logging.debug("Function init: " + node.name)
            self.methods.append(node)

def find_methods(service_ast):
    finder = MethodFinder()
    finder.visit(service_ast)
    methods = finder.methods
    return methods


def parse_service(service_raw):
    service_state = find_service_state(service_raw)
    methods = find_methods(service_raw)
    return Service(state=service_state, 
                   methods=methods,
                   service_ast=service_raw)

def parse_services(ast_node):
    all_services_raw = find_services(ast_node)
    all_services = [parse_service(service) for service in all_services_raw]
    return all_services

