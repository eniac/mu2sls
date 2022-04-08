import logging
import time

import fdb.tuple
from runtime.beldi.common import *
from runtime.serde import serialize, deserialize

## TODO: Add config variables here that:
##   - enables/disables beldi logging 
##     + kk: can we refactor log checking/saving in their own functions? I think so
##     
##   - toggles transactions 
##     + Maybe easy to do that: probably toggles locking

toggle_logging = True
toggle_txn = True

# def check_log(...):
#     if toggle_logging:
#         ...
#     else:
#         return False

# def write_log(...):
#     if toggle_logging:
#         ...
#     else:
#         return "OK"

## Note that the current API accepts anything that can be serialized 
##   by `json.dumps` as values.

def base_read(env: Env, key: str):
    res = env.db.get(fdb.tuple.pack(("data", env.table, key)))
    return None if res is None else deserialize(res)


def base_write(env: Env, key: str, value):
    env.db[fdb.tuple.pack(("data", env.table, key))] = serialize(value)

def _eos_read(tr, env: Env, key: str):
    # print("env.req_id", env.req_id)
    # print("env.step", env.step)
    data_k = fdb.tuple.pack(("data", env.table, key))
    log_k = fdb.tuple.pack(("log", env.table, env.req_id, env.step))
    ## TODO: Isn't this an unneccessary get here? If v2 exists then 
    ##       we paid for DB access with no reason.
    v1 = tr[data_k]
    v2 = tr[log_k]
    if not v2.present():
        # print("Log not present")
        tr[log_k] = v1 if v1.present() else serialize(None)
        env.step += 1
        return None if not v1.present() else deserialize(v1)
    else:
        # print("Log present")
        env.step += 1
        return deserialize(v2)


@log_timer("read")
def eos_read(env: Env, key: str):
    return fdb.transactional(_eos_read)(env.db, env, key)


def _eos_write(tr, env: Env, key: str, value):
    data_k = fdb.tuple.pack(("data", env.table, key))
    log_k = fdb.tuple.pack(("log", env.table, env.req_id, env.step))
    v2 = tr[log_k]
    if not v2.present():
        tr[data_k] = serialize(value)
        tr[log_k] = b''  # value is never read
    env.step += 1


@log_timer("write")
def eos_write(env: Env, key: str, value):
    return fdb.transactional(_eos_write)(env.db, env, key, value)


def _eos_contains(tr, env: Env, key: str):
    res = _eos_read(tr, env, key)
    # print("Key:", key, "read returned:", res)
    return res is not None


@log_timer("contain")
def eos_contains(env: Env, key: str):
    return fdb.transactional(_eos_contains)(env.db, env, key)


def _eos_set_if_not_exist(tr, env: Env, key: str, value):
    if not _eos_contains(tr, env, key):
        print("Initializing key:", key)
        _eos_write(tr, env, key, value)


@log_timer("set_if_not_exist")
def eos_set_if_not_exist(env: Env, key: str, value):
    fdb.transactional(_eos_set_if_not_exist)(env.db, env, key, value)


def _scan_dict(tr, env: Env, dict_name: str):
    log_k = fdb.tuple.pack(("log", env.table, env.req_id, env.step))
    prefix = fdb.tuple.pack(("data", env.table, f"{dict_name}-"))[:-1]  # tuple has trailing null byte
    v2 = tr[log_k]
    if not v2.present():
        env.step += 1
        res = tr.get_range_startswith(prefix)
        keys = []
        values = []
        for k, v in res:
            key = fdb.tuple.unpack(k)[-1]
            key = key.split("-")[-1]
            keys.append(key)
            values.append(deserialize(v))
        tr[log_k] = serialize((keys, values))
        return keys, values
    else:
        env.step += 1
        return deserialize(v2)


def scan_dict(env: Env, dict_name: str):
    return fdb.transactional(_scan_dict)(env.db, env, dict_name)


def _local_eos_read(tr, env: Env, key: str):
    local_k = fdb.tuple.pack(("local", env.table, env.txn_id, key))
    log_k = fdb.tuple.pack(("log", env.table, env.req_id, env.step))
    v1 = tr[local_k]
    v2 = tr[log_k]
    if not v2.present():
        tr[log_k] = v1 if v1.present() else serialize(None)
        env.step += 1
        return None if not v1.present() else deserialize(v1)
    else:
        env.step += 1
        return deserialize(v2)


def local_eos_read(env: Env, key: str):
    return fdb.transactional(_local_eos_read)(env.db, env, key)


def _local_eos_write(tr, env: Env, key: str, value):
    local_k = fdb.tuple.pack(("local", env.table, env.txn_id, key))
    log_k = fdb.tuple.pack(("log", env.table, env.req_id, env.step))
    v2 = tr[log_k]
    if not v2.present():
        tr[local_k] = serialize(value)
        tr[log_k] = b''  # value is never read
    env.step += 1


@log_timer("local_write")
def local_eos_write(env: Env, key: str, value):
    fdb.transactional(_local_eos_write)(env.db, env, key, value)


def _lock(tr, env: Env, key: str):
    log_k = fdb.tuple.pack(("log", env.table, env.req_id, env.step))
    lock_k = fdb.tuple.pack(("lock", env.table, key))
    assert env.txn_id is not None
    v2 = tr[log_k]
    if v2.present():
        env.step += 1
        return deserialize(v2)
    vlock = tr[lock_k]
    owner = deserialize(vlock) if vlock.present() else None
    if owner is not None:
        if owner == env.txn_id:
            tr[log_k] = serialize(True)
            env.step += 1
            return True
        else:
            tr[log_k] = serialize(False)
            env.step += 1
            return False
    else:
        tr[lock_k] = serialize(env.txn_id)
        tr[log_k] = serialize(True)
        env.step += 1
        return True


# @log_timer("lock")
# def lock(env: Env, key: str):
#     res = fdb.transactional(_lock)(env.db, env, key)
#     print("Lock for key:", key, "returned:", res)
#     return res


def _unlock(tr, env: Env, key: str):
    log_k = fdb.tuple.pack(("log", env.table, env.req_id, env.step))
    lock_k = fdb.tuple.pack(("lock", env.table, key))
    assert env.txn_id is not None
    v2 = tr[log_k]
    if v2.present():
        env.step += 1
        return
    vlock = tr[lock_k]
    owner = deserialize(vlock) if vlock.present() else None
    assert owner == env.txn_id, "unlock for key: {} with txn_id: {} but owner is: {}".format(key, env.txn_id, owner)
    tr[lock_k] = serialize(None)  # leave None instead of deleting
    tr[log_k] = b''
    env.step += 1


# @log_timer("unlock")
# def unlock(env: Env, key: str):
#     fdb.transactional(_unlock)(env.db, env, key)


def _add_lock(tr, env: Env, key: str):
    locks = _local_eos_read(tr, env, "locks")
    if locks is None:
        locks = []
    if key not in locks:
        locks.append(key)
        _local_eos_write(tr, env, "locks", locks)


def _tpl_read(tr, env: Env, key: str):
    if _lock(tr, env, key):
        _add_lock(tr, env, key)
        v = _local_eos_read(tr, env, key)
        # print("tpl_read for key:", key)
        # print("|-- local returned:", v)
        if v is not None:
            return True, v
        else:
            v = _eos_read(tr, env, key)
            # print("|-- eos returned:", v)
            return True, v
    else:
        return False, None


@log_timer("tpl_read")
def tpl_read(env: Env, key: str):
    return fdb.transactional(_tpl_read)(env.db, env, key)


# readonly until success
def _check_read(tr, env: Env, key: str):
    assert not env.in_txn()
    log_k = fdb.tuple.pack(("log", env.table, env.req_id, env.step))
    v2 = tr[log_k]
    if v2.present():
        env.step += 1
        return True, deserialize(v2)
    lock_k = fdb.tuple.pack(("lock", env.table, key))
    data_k = fdb.tuple.pack(("data", env.table, key))
    vlock = tr[lock_k]
    owner = deserialize(vlock) if vlock.present() else None
    if owner is not None:
        return False, None
    else:
        v1 = tr[data_k]
        tr[log_k] = v1 if v1.present() else serialize(None)
        env.step += 1
        return True, None if not v1.present() else deserialize(v1)


def check_read(env: Env, key: str):
    return fdb.transactional(_check_read)(env.db, env, key)


@log_timer("tpl_check_read")
def tpl_check_read(env: Env, key: str):
    counter = 0
    while True:
        ok, val = check_read(env, key)
        if ok:
            if counter > 0:
                logging.error("Counter:", counter)
            return val
        # time.sleep(0.005)
        counter += 1


# readonly until success
def _check_write(tr, env: Env, key: str, value):
    assert not env.in_txn()
    log_k = fdb.tuple.pack(("log", env.table, env.req_id, env.step))
    v2 = tr[log_k]
    if v2.present():
        env.step += 1
        return True
    lock_k = fdb.tuple.pack(("lock", env.table, key))
    data_k = fdb.tuple.pack(("data", env.table, key))
    vlock = tr[lock_k]
    owner = deserialize(vlock) if vlock.present() else None
    if owner is not None:
        return False
    else:
        tr[data_k] = serialize(value)
        tr[log_k] = b''  # value is never read
        env.step += 1
        return True


def check_write(env: Env, key: str, value):
    return fdb.transactional(_check_write)(env.db, env, key, value)


@log_timer("tpl_check_write")
def tpl_check_write(env: Env, key: str, value):
    counter = 0
    while True:
        ok = check_write(env, key, value)
        if ok:
            if counter > 0:
                logging.error("Counter:", counter)
            return
        # time.sleep(0.005)
        counter += 1


def _check_pop(tr, env: Env, key: str):
    assert not env.in_txn()
    log_k = fdb.tuple.pack(("log", env.table, env.req_id, env.step))
    v2 = tr[log_k]
    if v2.present():
        env.step += 1
        return True, deserialize(v2)
    lock_k = fdb.tuple.pack(("lock", env.table, key))
    data_k = fdb.tuple.pack(("data", env.table, key))
    vlock = tr[lock_k]
    owner = deserialize(vlock) if vlock.present() else None
    if owner is not None:
        return False, None
    else:
        v1 = tr[data_k]
        del tr[data_k]
        tr[log_k] = v1 if v1.present() else serialize(None)
        env.step += 1
        return True, None if not v1.present() else deserialize(v1)


def check_pop(env: Env, key: str):
    return fdb.transactional(_check_pop)(env.db, env, key)


@log_timer("tpl_check_pop")
def tpl_check_pop(env: Env, key: str):
    counter = 0
    while True:
        ok, val = check_pop(env, key)
        if ok:
            if counter > 0:
                logging.error("Counter:", counter)
            return val
        # time.sleep(0.005)
        counter += 1


@log_timer("tpl_contains")
def tpl_contains(env: Env, key: str):
    ok, val = _tpl_read(env.db, env, key)
    return ok, val is not None


def _tpl_write(tr, env: Env, key: str, value):
    if _lock(tr, env, key):
        _add_lock(tr, env, key)
        _local_eos_write(tr, env, key, value)
        return True
    else:
        return False


@log_timer("tpl_write")
def tpl_write(env: Env, key: str, value):
    return fdb.transactional(_tpl_write)(env.db, env, key, value)


def begin_tx(env: Env):
    assert env.txn_id is None
    env.txn_id = env.req_id
    env.instruction = "EXECUTE"


def _get_callees(tr, env: Env):
    callees = _local_eos_read(tr, env, "callee")
    return [] if callees is None else callees


def get_callees(env: Env):
    return fdb.transactional(_get_callees)(env.db, env)


def _commit_tx(tr, env: Env):
    local_k = fdb.tuple.range(("local", env.table, env.txn_id))
    local = tr[local_k]
    callees = []
    locks = []
    for k, v in local:
        k = fdb.tuple.unpack(k)[-1]
        if k == "callee":
            callees = deserialize(v)
            continue
        if k == "locks":
            locks = deserialize(v)
            continue
        v = deserialize(v)
        # print("Writing key:", k, "value:", v)
        _eos_write(tr, env, k, v)
    for k in locks:
        _unlock(tr, env, k)
    del tr[local_k]
    return callees


@log_timer("commit_tx_return_callees")
def commit_tx(env: Env):
    return fdb.transactional(_commit_tx)(env.db, env)


def _abort_tx(tr, env: Env):
    local_k = fdb.tuple.range(("local", env.table, env.txn_id))
    local = tr[local_k]
    callees = []
    locks = []
    for k, v in local:
        k = fdb.tuple.unpack(k)[-1]
        if k == "callee":
            callees = deserialize(v)
            continue
        if k == "locks":
            locks = deserialize(v)
            continue
    for k in locks:
        _unlock(tr, env, k)
    del tr[local_k]
    return callees


@log_timer("abort_tx_return_callees")
def abort_tx(env: Env):
    return fdb.transactional(_abort_tx)(env.db, env)


def _log_invoke(tr, env: Env):
    log_k = fdb.tuple.pack(("log", env.table, env.req_id, env.step))
    v2 = tr[log_k]
    if v2.present():
        env.step += 1
    else:
        tr[log_k] = b''
        env.step += 1


@log_timer("log_invoke")
def log_invoke(env: Env):
    fdb.transactional(_log_invoke)(env.db, env)


def _add_callee(tr, env: Env, client: str, method: str):
    callees = _local_eos_read(tr, env, "callee")
    if callees is None:
        callees = []
    callees.append((client, method))
    _local_eos_write(tr, env, "callee", callees)


def add_callee(env: Env, client: str, method: str):
    fdb.transactional(_add_callee)(env.db, env, client, method)
