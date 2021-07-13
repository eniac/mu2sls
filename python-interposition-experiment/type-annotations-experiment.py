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

        ## Necessary 
        self.generic_visit(node)

field_finder = ServiceClassFinder()
field_finder.visit(test_ast)

all_services = field_finder.services
for service in all_services:
    print(ast.dump(service))