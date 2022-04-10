import logging
import os

from runtime.beldi.beldi import get_shard_key

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

enable_custom_dict = os.getenv('ENABLE_CUSTOM_DICT')
if enable_custom_dict is None:
    print("ENABLE_CUSTOM_DICT wasn't set in the environment")
    ENABLE_CUSTOM_DICT = False
elif enable_custom_dict == "True":
    ENABLE_CUSTOM_DICT = True
else:
    ENABLE_CUSTOM_DICT = False
print("Custom Dict:", ENABLE_CUSTOM_DICT)


class Wrapper(object):
    pass


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
class WrapperTerminal(Wrapper):
    """
    Object wrapper class.
    This a wrapper for objects. It is initialiesed with the object to wrap
    and then proxies the unhandled getattribute methods to it.
    Other classes are to inherit from it.

    Taken from: https://code.activestate.com/recipes/577555-object-wrapper-class/
    """

    ## TODO: Figure out if `beldi` is a shared or a Beldi client per object.
    def __init__(self, obj_key, init_val, store):
        """
        Wrapper constructor.
        @param obj_key: the key of the object to wrap the accesses to
        @param init_val: the initial value for the object (if it doesn't exist in Beldi)
        """

        ## Save the key    
        self._wrapper_obj_key = obj_key

        ## TODO: Since Python is not lazy, the init_val is always evaluated and we might want to avoid that if it is a performance bottleneck.

        ## Initialize the collection if it doesn't already exist in Beldi
        initialize_key(store, self._wrapper_obj_key, init_val)

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

    ## Common method for wrapping all builtin_methods
    def _wrapper_builtin_method(self, func_name, *args, **kwargs):
        logging.debug(func_name)
        print("Method called:", func_name)
        store = self._wrapper_store
        object_key = self._wrapper_obj_key
        return wrap_method_call(store, object_key, func_name, *args, **kwargs)

    ## TODO: Do we need to reimplement all default functions?
    def __repr__(self) -> str:
        func_name = "__repr__"
        return self._wrapper_builtin_method(func_name)

    def __int__(self) -> int:
        func_name = "__int__"
        return self._wrapper_builtin_method(func_name)

    def __iter__(self):
        func_name = "__iter__"
        return self._wrapper_builtin_method(func_name)

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
        if (WrapperTerminal.is_wrapper_attr(attr)):
            # this object has it (for example, Beldi)
            return self.__dict__[attr]

        ## In this case the attribute is part of the original object and therefore we need to access it through Beldi.
        store = self._wrapper_store

        ## Get the object from Beldi. This should never fail
        ##
        ## TODO: If we actually want to support getting and setting fields, we need to
        ##       replace that with a proper transactional read since `eos` doesn't
        ##       play well together with transaction reads. 
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
        if (callable(ret_attribute)):
            ret_attribute = self._wrap_callable(attr)

        return ret_attribute

    ## Wraps a callable by delaying the get until it is actually called
    def _wrap_callable(self, attr_name):
        logging.debug("Attr name: " + attr_name)

        ## This function is returned instead of the callable.
        ## When called, it retrieves the callable object from Beldi and calls it.
        def wrapper(*args, **kwargs):
            store = self._wrapper_store
            object_key = self._wrapper_obj_key
            return wrap_method_call(store, object_key, attr_name, *args, **kwargs)

        return wrapper

    def __setattr__(self, attr: str, val) -> None:
        logging.debug("Set: " + attr)
        ## If it is a wrapper specific method
        if (WrapperTerminal.is_wrapper_attr(attr)):
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
        if (hasattr(obj, attr)):
            assert (not callable(getattr(obj, attr)))

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
        if (WrapperTerminal.is_wrapper_attr(attr)):
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

    def __add__(self, *args, **kwargs):
        func_name = "__add__"
        logging.debug(func_name)
        if (not hasattr(self._wrapper_init_value, func_name)):
            raise TypeError()

        store = self._wrapper_store
        object_key = self._wrapper_obj_key
        return wrap_method_call(store, object_key, func_name, *args, **kwargs)

    def __eq__(self, *args, **kwargs):
        func_name = "__eq__"
        logging.debug(func_name)
        if (not hasattr(self._wrapper_init_value, func_name)):
            raise TypeError()

        store = self._wrapper_store
        object_key = self._wrapper_obj_key
        return wrap_method_call(store, object_key, func_name, *args, **kwargs)

    def __contains__(self, *args, **kwargs):
        func_name = "__contains__"
        logging.debug(func_name)
        return self._wrapper_builtin_method(func_name, *args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        func_name = "__getitem__"
        logging.debug(func_name)
        return self._wrapper_builtin_method(func_name, *args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        func_name = "__setitem__"
        logging.debug(func_name)
        return self._wrapper_builtin_method(func_name, *args, **kwargs)


##
## TODO: Doesn't support iteration and access of all keys at the moment
##
## TODO:
## 1. Debug on Cloudlab
## 2. Add a flag to run this with and without the custom dictionary
##
class WrapperDict(Wrapper):
    ## The current implementation doesn't support proper retrievals of all keys,
    ##   just a retrieval of each key separately.
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
        ##
        ## TODO: Check if we do have a request id here
        # val = store.read_until_success(self._wrapper_obj_key)
        initialize_key(store, self._wrapper_obj_key, init_val)

        ## Store beldi client for later use
        self._wrapper_store = store

        ## Keep the init_value around, to use it to check the dir for special methods and so on.
        self._wrapper_init_value = init_val

        # print("Key given:", obj_key, ", init_val:", init_val)
        ## Initialize all items of the dictionary separately
        for key, val in init_val.items():
            initialize_key(store, self.get_key_key(key), val)

    ## Get the key name (for the store) of a specific key (dict)
    def get_key_key(self, key):
        return f'{self._wrapper_obj_key}-{key}'

    ##
    ## Dict methods
    ##
    def __contains__(self, key):
        val = self.__getitem__core(key)
        ret = (not (val_doesnt_exist(val)))
        return ret

    def __getitem__(self, key):
        val = self.__getitem__core(key)
        if val_doesnt_exist(val):
            raise KeyError(key)
        return val

    def __getitem__core(self, key):
        store_key = self.get_key_key(key)
        in_txn = self._wrapper_store.in_txn()

        if in_txn:
            return self._wrapper_store.read_throw(store_key)
        else:
            return self._wrapper_store.tpl_check_read(store_key)

    def __setitem__(self, key, val):
        store_key = self.get_key_key(key)
        in_txn = self._wrapper_store.in_txn()

        if in_txn:
            self._wrapper_store.write_throw(store_key, val)
        else:
            self._wrapper_store.tpl_check_write(store_key, val)

    def keys(self):
        return self._wrapper_store.tpl_check_scan(self._wrapper_obj_key)[0]

    def values(self):
        return self._wrapper_store.tpl_check_scan(self._wrapper_obj_key)[1]

    ## Get with a possible default
    def get(self, key, default=None):
        if default is None:
            return self.__getitem__(key)
        else:
            val = self.__getitem__core(key)
            if val_doesnt_exist(val):
                return default
            else:
                return val

    def pop(self, key, default=None):
        store_key = self.get_key_key(key)
        in_txn = self._wrapper_store.in_txn()

        if in_txn:
            val = self._wrapper_store.read_throw(store_key)
            write_success = self._wrapper_store.write(store_key, "")
            assert write_success
        else:
            val = self._wrapper_store.tpl_check_pop(store_key)

        if val_doesnt_exist(val):
            if default is None:
                raise KeyError(key)
            else:
                val = default
        return val


## This checks if a return value shows non-existence
## Currently this is done with None
def val_doesnt_exist(val):
    return val is None


def wrap_terminal(object_key, object_init_val, store):
    ## TODO: Currently this determines the type using the initial value,
    ##       but it could also use the type.
    if ENABLE_CUSTOM_DICT and isinstance(object_init_val, dict):
        print("Custom dictionary")
        # print("Dictionary type:", object_init_val)
        wrapped_object = WrapperDict(object_key, object_init_val, store)
    else:
        print("Default dictionary")
        ## The general wrapping that adds the object behind a key
        wrapped_object = wrap_default(object_key, object_init_val, store)

    return wrapped_object


def wrap_default(object_key, object_init_val, store):
    wrapped_object = WrapperTerminal(object_key, object_init_val, store)

    return wrapped_object


# This function determines whether to call a version of read that will always succeed,
# or whether to call one that might fail (depending on whether we are already in a transaction)
# or not.
def begin_tx_and_read(store, key: str):
    ## If we are already in a transaction, it means that an update might abort, and so we don't need to repeat it until it succeeds
    if store.in_txn():
        ## If this read fails, we throw an exception, to be caught in an above layer
        return store.read_throw(key)
    else:
        return store.read_until_success(key)


def begin_tx_and_write(store, key: str, val):
    ## If we are already in a transaction, it means that an update might abort, and so we don't need to repeat it until it succeeds
    if store.in_txn():
        ## If this write fails, we throw an exception, to be caught in an above layer
        return store.write_throw(key, val)
    else:
        return store.write_until_success(key, val)


## Initializes the key in the store
def initialize_key(store, key, val):
    store.eos_set_if_not_exists(key, val)


## This is the core function that wraps method calls to remote objects
def wrap_method_call(store, object_key, attr_name, *args, **kwargs):
    # print("Wrapping method:", attr_name)
    ## Check if the store was already in a transaction,
    ##   if so, we don't commit!
    ##
    ## TODO: To solve this properly, we need to add a counter that checks how
    ##       many transactions in are we.
    prior_in_txn = store.in_txn()
    # print("In txn:", prior_in_txn)

    if ENABLE_CUSTOM_DICT:
        object_key = get_shard_key(f"{object_key}-{attr_name}")

    ## Begin the transaction and read
    obj = begin_tx_and_read(store, object_key)
    # print("Obj is:", obj)

    ## Call the method
    callable_attr = getattr(obj, attr_name)
    assert (callable(callable_attr))

    # print("Calling method:", attr_name, "with_args:", args, kwargs)

    ret = callable_attr(*args, **kwargs)
    # print("Ret:", ret)
    # print("New obj:", obj)

    ## I assume that by calling the method like above the object does get updated.

    ## Update the object in Beldi
    ##
    ## Note: This should always succeed since the lock was acquired for the read.
    write_success = store.write(object_key, obj)
    assert write_success

    ## Commit only if we were not in a transaction already.
    if not prior_in_txn:
        ## This should always succeed
        store.CommitTx()
    return ret
