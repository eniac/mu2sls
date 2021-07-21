
from runtime import serde

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


## Wrap terminal is the simplest wrapper. It: 
##  1. Serializes the whole object
##  2. Stores it to Beldi
##  3. Wraps all its methods to:
##      a. Perform a beldi transaction
##      b. Get the object from Beldi
##      c. Apply the method
##      d. Set the object to Beldi
##      e. Close the transaction
##
## Q: What about the fields (non callable attributes)?
##
## TODO: Look at __getattr__ 
## TODO: Investigate slots and descriptors
class WrapperTerminal(object):
    '''
    Object wrapper class.
    This a wrapper for objects. It is initialiesed with the object to wrap
    and then proxies the unhandled getattribute methods to it.
    Other classes are to inherit from it.
    
    Taken from: https://code.activestate.com/recipes/577555-object-wrapper-class/
    '''
    ## TODO: Figure out if `beldi` is a shared or a Beldi client per object.
    def __init__(self, obj, beldi):
        '''
        Wrapper constructor.
        @param obj: object to wrap
        '''
        ## Serialize the whole object
        serialized_obj = serde.serialize(obj)

        ## TODO: How to correctly get a key. Use the class name? Maybe the object hash?
        ## TODO: `id()` is not correct since different objects might have the same
        self._wrapper_obj_key = id(obj)

        beldi.set(self._wrapper_obj_key, serialized_obj)

        ## Store beldi client for later use
        self._wrapper_beldi = beldi

    ## This function returns whether an attribute is wrapper specific 
    ## (and not of the internal object). At the moment this is done simply
    ## by checking whether it starts with _wrapper.
    ##
    ## TODO: Make this more efficient for christ's sake
    @staticmethod
    def is_wrapper_attr(attr_name: str) -> bool:
        return attr_name.startswith("_wrapper_")


    ## This method overrides the original object's getattr,
    ## making sure that attributes are accessed through Beldi.
    ##
    ## An attribute can be a method (callable) or a field (non-callable).
    ##
    ## If it is a method, we actually need to 
    def __getattr__(self, attr):
        # see if this object has attr
        # NOTE do not use hasattr, it goes into
        # infinite recursion
        if attr in self.__dict__:
            # this object has it (for example, Beldi)
            return self.__dict__[attr]
        
        
        ## In this case the attribute is part of the original object and therefore we need to access it through Beldi.
        beldi = self._wrapper_beldi

        ## Get the object from Beldi. This should never fail
        serialized_obj = beldi.get(self._wrapper_obj_key)

        ## Deserialize the object
        obj = serde.deserialize(serialized_obj)

        ## Get the attribute of the object
        ret_attribute = getattr(obj, attr)

        ## If it is callable, we need to delay its retrieval until it is actually called.
        ##
        ## Q: Do we have any special assumptions about that?
        ##
        ## TODO: Optimize this to only wrap methods at the start, 
        ##       and not do it every getattr. This requires an assumption
        ##       that no user method is modified by user code.
        ##       
        ## Note: The optimization assumption (no modification of callable)
        ##       can actually be checked at runtime, so we should check it. 
        if(callable(ret_attribute)):
            ret_attribute = self._wrap_callable(ret_attribute, attr)

        return ret_attribute

    ## Wraps a callable by delaying the get until it is actually called
    def _wrap_callable(self, _callable, attr_name):
    
        ## This function is returned instead of the callable.
        ## When called, it retrieves the callable object from Beldi and calls it.
        ##
        ## The actual _callable is dropped.
        ## TODO: Is that fine? 
        def wrapper(*args, **kwargs):
            beldi = self._wrapper_beldi

            ## TODO: Do we actually need the transaction here?
            ##
            ## I think we do because we perform a `get` and `set`
            beldi.begin_tx()

            ## Get the object and deserialize it
            serialized_obj = beldi.get(self._wrapper_obj_key)
            obj = serde.deserialize(serialized_obj)

            ## Call the method
            callable_attr = getattr(obj, attr_name)
            assert(callable(callable_attr))
            ret = callable_attr(*args, **kwargs)

            ## I assume that by calling the method like above the object does get updated.
            
            ## Update the object in Beldi
            new_serialized_obj = serde.serialize(obj)
            beldi.set(self._wrapper_obj_key, new_serialized_obj)

            beldi.end_tx()
            return ret

        return wrapper

    ## TODO: Implement __setattr__
    def __setattr__(self, attr: str, val) -> None:
        ## If it is a wrapper specific method
        if(attr in self.__dict__ 
           or WrapperTerminal.is_wrapper_attr(attr)):
            self.__dict__[attr] = val
            return
            # return setattr(self, attr, val)

        ## TODO: Implement it for the wrapped object
        print("Attr name:", attr)
        raise NotImplementedError

    ## TODO: Implement __delattr__
    def __delattr__(self, attr: str) -> None:
        ## If it is a wrapper specific method
        if(attr in self.__dict__
           or WrapperTerminal.is_wrapper_attr(attr)):
            del self.__dict__[attr]
            return
            # return delattr(self, attr)

        ## TODO: Implement it for the wrapped object
        raise NotImplementedError
        

def wrap_terminal(object, beldi):
    wrapped_object = WrapperTerminal(object, beldi)
    return wrapped_object

    ## Old code:
    # ## Use that to find the methods of an object. Then we can wrap them (either dynamically, or statically)
    # ## with beldi get, set and transactions.
    # object_methods = [method_name for method_name in dir(object)
    #                 if callable(getattr(object, method_name))]
    
    # print("Object Methods:", object_methods)

    # object_fields = [field_name for field_name in dir(object)
    #                  if not callable(getattr(object, field_name))]
    # print("Object Fields:", object_fields)
