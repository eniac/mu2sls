
##
## This is the main wrapper method that wraps an object to enforce correctness guarantees.
##
## It does the following:
##  1. Checks all the methods and fields of an object
##  2. Wrap all methods in Beldi transactions to ensure that they are atomic
##  3. Serialize (or wrap) all fields and replace their accesses using Beldi
##
## Questions/TODOs:
##  1. Do we need to wrap the complete structure recursively? 
##     I think this might involve correctness issues if we don't.
##     Can we stop at an arbitrary level (and then conservatively serialize at the end)?
##  2. It is pretty naive asking Beldi everytime we want to get/set a field
##

def wrap_terminal(object, beldi):
    beldi.begin_tx()

    ## Use that to find the methods of an object. Then we can wrap them (either dynamically, or statically)
    ## with beldi get, set and transactions.
    object_methods = [method_name for method_name in dir(object)
                    if callable(getattr(object, method_name))]
    print(object_methods)

    beldi.end_tx()
