import ast
import logging


import frontend

logging.basicConfig(level=logging.WARNING)
# logging.basicConfig(level=logging.DEBUG)

test_source_file = "type-annotations-experiment-test.py"

with open(test_source_file) as f:
    test_source = f.read()

test_ast = ast.parse(test_source,
                     filename=test_source_file,
                     type_comments=True)

# print(ast.dump(test_ast))


## Parse the AST to acquire the services and their states.
service_states = frontend.parse_services(test_ast)
for service_state in service_states:
    print("Service State:", service_state)

## TODO: Start with a rudimentary backend that simply prints back the code, making sure that initializations happens in the beginning.
##
## Q: Do we need anything else in the header?
##
## Q: As shown below in more detail. Let's not make the transformation yet, since it is unclear whether we want to do it at load-time
##    or at compile time.

## TODO: Make a trivial extension where accesses to the persistent fields go through getters and setters. Test it.

## High level Q: Is it possible to perform all changes dynamically? That is, instead of
##               compiling the AST, simply decorating the class and making sure that it implements
##               methods that give us this information? For example, if it implements a static method that
##               gives us the fields names, as well as whether they are persistent or not.