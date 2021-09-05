import ast
import logging
import os


from compiler import compiler

## This might be needed for the decompiler
PYTHON_VERSION="3.8"
logging.basicConfig(level=logging.WARNING)
# logging.basicConfig(level=logging.DEBUG)

## TODO: These should be given as inputs
# test_source_file = "type-annotations-experiment-test.py"
test_source_file = "tests/source_specs/list-service.py"
out_dir = "target"
out_file = os.path.join(out_dir, "test.py")


## Create the out directory if it doesn't exist
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

compiler.compile_service_module(test_source_file, out_file)

## High level Q: Is it possible to perform all changes dynamically? That is, instead of
##               compiling the AST, simply decorating the class and making sure that it implements
##               methods that give us this information? For example, if it implements a static method that
##               gives us the fields names, as well as whether they are persistent or not.
