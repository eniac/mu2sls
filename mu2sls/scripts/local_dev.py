##
## This module contains utility functions to locally load and test services
##

import importlib
from runtime import store_stub

def import_compiled(compiled_module_name):
    return importlib.import_module(compiled_module_name)

def init_local_store():
    return store_stub.Store()

