import importlib
import logging
import os
import sys

from compiler import compiler

def test_compiler_list_service():
    logging.basicConfig(level=logging.DEBUG)
    test_source_file = "tests/source_specs/list-service.py"
    out_dir = "target"
    out_file = os.path.join(out_dir, "test_list.py")


    ## Create the out directory if it doesn't exist
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    compiler.compile_single_method_service_module(test_source_file, out_file)

    ## Add the output dir to the system path
    sys.path.append(out_dir)

    ## The documentation claims that it is necessary if importing a dynamically generated file
    importlib.invalidate_caches()

    test_module = importlib.import_module("test_list")

    ## These are included in the test_code_object
    service = test_module.Service()
    service.test()
