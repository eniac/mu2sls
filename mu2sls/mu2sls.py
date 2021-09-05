#!/usr/bin/env python3
import logging
import os

from compiler import compiler

def main():
    logging.basicConfig(level=logging.DEBUG)
    test_source_file = "tests/source_specs/list-service.py"
    out_dir = "target"
    out_file = os.path.join(out_dir, "popo.py")


    ## Create the out directory if it doesn't exist
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    compiler.compile_service_module(test_source_file, out_file)

if __name__ == "__main__":
    main()