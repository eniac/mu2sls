import importlib
import logging
import os
import sys

from compiler import compiler

from runtime.local import logger

def compile_import_module(source_file, out):
    logging.basicConfig(level=logging.DEBUG)
    out_dir = "target"
    out_file = os.path.join(out_dir, out + ".py")


    ## Create the out directory if it doesn't exist
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    compiler.compile_single_method_service_module(source_file, out_file)

    ## Add the output dir to the system path
    sys.path.append(out_dir)

    ## The documentation claims that it is necessary if importing a dynamically generated file
    importlib.invalidate_caches()

    test_module = importlib.import_module(out)

    return test_module

def test_compiler_list_service():
    test_source_file = "tests/source_specs/list-service.py"
    test_out = "test_list"
    test_module = compile_import_module(test_source_file, test_out)

    ## These are included in the test_code_object
    store = logger.LocalLogger()
    store.init_env()
    service = test_module.Service(store)
    service.__init_per_objects__()

    service.test()

def test_compiler_url_shortener_service():
    test_source_file = "tests/source_specs/url_shortener.py"
    test_out = "test_url_shortener"
    test_module = compile_import_module(test_source_file, test_out)


    ## These are included in the test_code_object
    store = logger.LocalLogger()
    store.init_env()
    service = test_module.UrlShortener(store)
    service.__init_per_objects__()

    url1 = "url1"
    ret1 = service.ShortenUrls(url1)
    assert(ret1[0] == "NotFound")

    url2 = "url2"
    ret2 = service.ShortenUrls(url2)
    assert(ret2[0] == "NotFound")

    ret3 = service.ShortenUrls(url1)
    assert(ret3[0] == "Found")
    assert(ret1[1] == ret3[1])

