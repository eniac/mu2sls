import ast

test_source_file = "type-annotations-experiment-test.py"

with open(test_source_file) as f:
    test_source = f.read()

test_ast = ast.parse(test_source,
                     filename=test_source_file,
                     type_comments=True)

# print(ast.dump(test_ast))

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
class FieldFinder(ast.NodeVisitor):
    ## This function finds the __init__ and then searches for all field initializations in it.
    def visit_FunctionDef(self, node: ast.FunctionDef):
        if(node.name == '__init__'):
            print("Function init:", node.name)
            print(ast.dump(node))

        ## We don't actually want to visit the children so we don't need the following
        # self.generic_visit(node)





all_services = find_services(test_ast)

for service in all_services:
    # print(ast.dump(service))

    ## TODO: Find init
    field_finder = FieldFinder()
    field_finder.visit(service)


## High level Q: Is it possible to perform all changes dynamically? That is, instead of
##               compiling the AST, simply decorating the class and making sure that it implements
##               methods that give us this information? For example, if it implements a static method that
##               gives us the fields names, as well as whether they are persistent or not.