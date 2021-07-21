import ast
import logging
import os


from compiler import frontend, backend
from runtime import beldi_stub, wrappers

## This might be needed for the decompiler
PYTHON_VERSION="3.8"
logging.basicConfig(level=logging.WARNING)
# logging.basicConfig(level=logging.DEBUG)

## TODO: These should be given as inputs
test_source_file = "type-annotations-experiment-test.py"
out_dir = "target"
out_file = os.path.join(out_dir, "test.py")


## Create the out directory if it doesn't exist
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

## Read the input file and parse it
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


## I don't think we need this object.
_decompiled = backend.ast_to_source(test_ast, out_file)


## Initialize a beldi_stub instance
beldi = beldi_stub.Beldi()
collection = []

wrappers.wrap_terminal(collection, beldi)



## TODO: Start with a rudimentary backend that simply prints back the code, making sure that initializations happens in the beginning.

## TODO: Make a trivial extension where accesses to the persistent fields go through getters and setters. Test it.

## TODO: Package these things in a normal library

## High level Q: Is it possible to perform all changes dynamically? That is, instead of
##               compiling the AST, simply decorating the class and making sure that it implements
##               methods that give us this information? For example, if it implements a static method that
##               gives us the fields names, as well as whether they are persistent or not.