import logging

from runtime.transaction_exception import TransactionException

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
    def __init__(self, obj_key, init_val, store):
        '''
        Wrapper constructor.
        @param obj_key: the key of the object to wrap the accesses to
        @param init_val: the initial value for the object (if it doesn't exist in Beldi)
        '''

        ## Save the key    
        self._wrapper_obj_key = obj_key

        ## TODO: Since Python is not lazy, the init_val is always evaluated and we might want to avoid that if it is a performance bottleneck.

        ## Initialize the collection if it doesn't already exist in Beldi
        ## Potentially alternative way of doing it (though, we don't have a request id maybe here.)
        # val = store.read_until_success(self._wrapper_obj_key)
        if(not store.contains(self._wrapper_obj_key)):
            print("Store doesn't contain key:", self._wrapper_obj_key)
            ## NOTE: We need to use set_if_not_exists to ensure atomicity
            store.set_if_not_exists(self._wrapper_obj_key, init_val)
    
        ## Store beldi client for later use
        self._wrapper_store = store

        ## Keep the init_value around, to use it to check the dir for special methods and so on.
        self._wrapper_init_value = init_val

    ## This function returns whether an attribute is wrapper specific 
    ## (and not of the internal object). At the moment this is done simply
    ## by checking whether it starts with _wrapper.
    ##
    ## TODO: Make this more efficient for christ's sake
    @staticmethod
    def is_wrapper_attr(attr_name: str) -> bool:
        return attr_name.startswith("_wrapper_")

    ## Replaces the value of the wrapped object (useful for assignments)
    def _wrapper_set(self, new_value):
        store = self._wrapper_store
        ## Save the object
        store.eos_write(self._wrapper_obj_key, new_value)
    
    def _wrapper_get(self):
        store = self._wrapper_store
        ## Return the value of the object
        return store.eos_read(self._wrapper_obj_key)


    ## TODO: Do we need to reimplement all default functions?
    def __repr__(self) -> str:
        logging.debug("__repr__")
        store = self._wrapper_store

        ## Get the object from Beldi. This should never fail
        obj = store.eos_read(self._wrapper_obj_key)

        return obj.__repr__()

    def __int__(self) -> int:
        logging.debug("__int__")
        store = self._wrapper_store

        ## Get the object from Beldi. This should never fail
        obj = store.eos_read(self._wrapper_obj_key)

        return obj.__int__()

    ## This method overrides the original object's getattr,
    ## making sure that attributes are accessed through Beldi.
    ##
    ## An attribute can be a method (callable) or a field (non-callable).
    ##
    ## If it is a method, we actually need to 
    def __getattr__(self, attr):
        logging.debug("Get: " + attr)
        # see if this object has attr
        # NOTE do not use hasattr, it goes into
        # infinite recursion
        if(WrapperTerminal.is_wrapper_attr(attr)):
            # this object has it (for example, Beldi)
            return self.__dict__[attr]
        
        
        ## In this case the attribute is part of the original object and therefore we need to access it through Beldi.
        store = self._wrapper_store

        ## Get the object from Beldi. This should never fail
        obj = store.eos_read(self._wrapper_obj_key)

        ## Get the attribute of the object
        ##
        ## Note: This is only used to determine if it is a callable. After that it is dropped.
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
            ret_attribute = self._wrap_callable(attr)

        return ret_attribute

    ## Wraps a callable by delaying the get until it is actually called
    def _wrap_callable(self, attr_name):
        logging.debug("Attr name: " + attr_name)
    
        ## This function is returned instead of the callable.
        ## When called, it retrieves the callable object from Beldi and calls it.
        def wrapper(*args, **kwargs):
            store = self._wrapper_store

            ## Begin the transaction and read
            obj = begin_tx_and_read(store, self._wrapper_obj_key)

            ## Call the method
            callable_attr = getattr(obj, attr_name)
            assert(callable(callable_attr))
            ret = callable_attr(*args, **kwargs)

            ## I assume that by calling the method like above the object does get updated.
            
            ## Update the object in Beldi
            ##
            ## Note: This should always succeed since the lock was acquired for the read.
            write_success = store.write(self._wrapper_obj_key, obj)
            assert write_success

            ## This should always succeed
            store.CommitTx()
            return ret

        return wrapper

    def __setattr__(self, attr: str, val) -> None:
        logging.debug("Set: " + attr)
        ## If it is a wrapper specific method
        if(WrapperTerminal.is_wrapper_attr(attr)):
            self.__dict__[attr] = val
            return
            # return setattr(self, attr, val)

        ## In this case the attribute is part of the original object and therefore we need to access it through Beldi.
        store = self._wrapper_store

        store.BeginTx()

        ## TODO: Can we optimize away this get and deserialize?
        ##
        ## Get the object from Beldi. This should never fail
        obj = store.eos_read(self._wrapper_obj_key)
        
        ## This should never happen if the attribute is callable, i.e., a method should
        ## never be replaced.
        ##
        ## This will allow us an optimization that only does the method wrapping once.
        if(hasattr(obj, attr)):
            assert(not callable(getattr(obj, attr)))

        ## Get the attribute of the object
        ret = setattr(obj, attr, val)

        ## Resave the object
        store.eos_write(self._wrapper_obj_key, obj)

        store.CommitTx()

        return ret

    ## TODO: Implement __delattr__
    def __delattr__(self, attr: str) -> None:
        logging.debug("Del: " + attr)
        ## If it is a wrapper specific method
        if(WrapperTerminal.is_wrapper_attr(attr)):
            del self.__dict__[attr]
            return

        ## TODO: Implement it for the wrapped object
        raise NotImplementedError
    
    ########################################################
    ##
    ## Wrapper handling of Special Methods
    ##
    ########################################################

    ## TODO: Abstract away common code.

    def __add__(self, other):
        logging.debug("__add__: " + str(other))
        if (not hasattr(self._wrapper_init_value, '__add__')):
            raise TypeError()
        
        ## In this case the special method is part of the original object and therefore we need to access it through Beldi.
        store = self._wrapper_store

        store.BeginTx()

        ## Get the object from Beldi. This should never fail
        obj = store.eos_read(self._wrapper_obj_key)

        ## Get the attribute of the object
        ret_value = obj.__add__(other)

        store.eos_write(self._wrapper_obj_key, obj)

        store.CommitTx()

        return ret_value
        
    def __eq__(self, other):
        logging.debug("__eq__: " + str(other))
        if (not hasattr(self._wrapper_init_value, '__eq__')):
            raise TypeError()
        
        ## In this case the special method is part of the original object and therefore we need to access it through Beldi.
        store = self._wrapper_store

        store.BeginTx()

        ## Get the object from Beldi. This should never fail
        obj = store.eos_read(self._wrapper_obj_key)

        ## Get the attribute of the object
        ret_value = obj.__eq__(other)

        store.eos_write(self._wrapper_obj_key, obj)

        store.CommitTx()

        return ret_value

## TODO: Rename this to Object Client/Interface since it doesn't actually wrap
def wrap_terminal(object_key, object_init_val, store):
    wrapped_object = WrapperTerminal(object_key, object_init_val, store)
    return wrapped_object

## This function determines whether to call a version of read that will always succeed,
## or whether to call one that might fail (depending on whether we are already in a transaction)
## or not.
def begin_tx_and_read(store, key: str):
    ## If we are already in a transaction, it means that an update might abort, and so we don't need to repeat it until it succeeds
    if store.in_txn():
        ## If this read fails, we throw an exception, to be caught in an above layer
        return store.read_throw(key)
    else:
        return store.read_until_success(key)

