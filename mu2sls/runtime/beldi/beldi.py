import fdb.tuple

from runtime.beldi.common import *

## Note that the current API accepts anything that can be serialized 
##   by `json.dumps` as values.

def base_read(env: Env, key: str):
    return deserialize(env.db.get(fdb.tuple.pack(("data", env.table, key))))


def base_write(env: Env, key: str, value):
    env.db[fdb.tuple.pack(("data", env.table, key))] = serialize(value)


@fdb.transactional
def _eos_read(tr, env: Env, key: str):
    v1 = tr.get(fdb.tuple.pack(("data", env.table, key)))
    v2 = tr.get(fdb.tuple.pack(("log", env.table, env.instance_id, env.step)))
    if not v2.present():
        tr[fdb.tuple.pack(("log", env.table, env.instance_id, env.step))] = v1 if v1.present() else b''
        env.step += 1
        return None if not v1.present() else deserialize(v1)
    else:
        env.step += 1
        return deserialize(v2)


def eos_read(env: Env, key: str):
    return _eos_read(env.db, env, key)


@fdb.transactional
def _local_eos_read(tr, env: Env, key: str):
    v1 = tr.get(fdb.tuple.pack(("local", env.table, env.txn_id, key)))
    v2 = tr.get(fdb.tuple.pack(("log", env.table, env.instance_id, env.step)))
    if not v2.present():
        tr[fdb.tuple.pack(("log", env.table, env.instance_id, env.step))] = v1 if v1.present() else b''
        env.step += 1
        return None if not v1.present() else deserialize(v1)
    else:
        env.step += 1
        return deserialize(v2)


def local_eos_read(env: Env, key: str):
    return _local_eos_read(env.db, env, key)


## This is an auxiliary method that simply calls `eos_read` to check if a key exists
def eos_contains(env: Env, key: str):
    ret = eos_read(env, key)
    return not (ret is None or ret == b'')


@fdb.transactional
def _eos_write(tr, env: Env, key: str, value):
    v2 = tr.get(fdb.tuple.pack(("log", env.table, env.instance_id, env.step)))
    if not v2.present():
        tr[fdb.tuple.pack(("data", env.table, key))] = serialize(value)
        tr[fdb.tuple.pack(("log", env.table, env.instance_id, env.step))] = b''
    env.step += 1


def eos_write(env: Env, key: str, value):
    return _eos_write(env.db, env, key, value)


@fdb.transactional
def _local_eos_write(tr, env: Env, key: str, value):
    v2 = tr.get(fdb.tuple.pack(("log", env.table, env.instance_id, env.step)))
    if not v2.present():
        tr[fdb.tuple.pack(("local", env.table, env.txn_id, key))] = serialize(value)
        tr[fdb.tuple.pack(("log", env.table, env.instance_id, env.step))] = b''
    env.step += 1


def local_eos_write(env: Env, key: str, value):
    return _local_eos_write(env.db, env, key, value)


@fdb.transactional
def eos_cond_write(tr, env: Env, table: str, key: str, value, name: str, var: str) -> bool:
    v2 = tr.get(fdb.tuple.pack(("log", table, env.instance_id, env.step)))
    if v2.present():
        env.step += 1
        return deserialize(v2)
    v1 = tr.get(fdb.tuple.pack(("data", table, key)))
    v = deserialize(v1)
    if v[name] == var:
        tr[fdb.tuple.pack(("data", table, key))] = value
        tr[fdb.tuple.pack(("log", table, env.instance_id, env.step))] = serialize(True)
        env.step += 1
        return True
    else:
        tr[fdb.tuple.pack(("log", table, env.instance_id, env.step))] = serialize(False)
        env.step += 1
        return False


@fdb.transactional
def _lock(tr, env: Env, key: str):
    assert env.txn_id is not None
    v2 = tr.get(fdb.tuple.pack(("log", env.table, env.instance_id, env.step)))
    if v2.present():
        env.step += 1
        return deserialize(v2)
    vlock = tr.get(fdb.tuple.pack(("lock", env.table, key)))
    if vlock.present():
        vl = deserialize(vlock)
        if vl == env.txn_id:
            tr[fdb.tuple.pack(("log", env.table, env.instance_id, env.step))] = serialize(True)
            env.step += 1
            return True
        else:
            tr[fdb.tuple.pack(("log", env.table, env.instance_id, env.step))] = serialize(False)
            env.step += 1
            return False
    else:
        tr[fdb.tuple.pack(("lock", env.table, key))] = serialize(env.txn_id)
        tr[fdb.tuple.pack(("log", env.table, env.instance_id, env.step))] = serialize(True)
        env.step += 1
        return True


def lock(env: Env, key: str):
    return _lock(env.db, env, key)


@fdb.transactional
def _unlock(tr, env: Env, key: str):
    assert env.txn_id is not None
    v2 = tr.get(fdb.tuple.pack(("log", env.table, env.instance_id, env.step)))
    if v2.present():
        env.step += 1
        return deserialize(v2)
    vlock = tr.get(fdb.tuple.pack(("lock", env.table, key)))
    assert vlock.present()
    vl = deserialize(vlock)
    assert vl == env.txn_id
    del tr[fdb.tuple.pack(("lock", env.table, key))]
    tr[fdb.tuple.pack(("log", env.table, env.instance_id, env.step))] = b''
    env.step += 1


def unlock(env: Env, key: str):
    return _unlock(env.db, env, key)


def tpl_read(env: Env, key: str):
    if lock(env, key):
        v = local_eos_read(env, key)
        return True, v
    else:
        return False, None


def tpl_write(env: Env, key: str, value):
    if lock(env, key):
        local_eos_write(env, key, value)
        return True
    else:
        return False


def begin_txn(env: Env):
    env.txn_id = env.instance_id
    env.instruction = "EXECUTE"
    local_eos_write(env, "callee", [])


def commit_txn(env: Env):
    local = env.db[fdb.tuple.range(("local", env.table, env.txn_id))]
    for k, v in local:
        k = fdb.tuple.unpack(k)[-1]
        v = deserialize(v)
        eos_write(env, k, v)
        unlock(env, k)
    del env.db[fdb.tuple.range(("local", env.table, env.txn_id))]


def abort_txn(env: Env):
    local = env.db[fdb.tuple.range(("local", env.table, env.txn_id))]
    for k, _ in local:
        k = fdb.tuple.unpack(k)[-1]
        unlock(env, k)
    del env.db[fdb.tuple.range(("local", env.table, env.txn_id))]


def tpl_commit(env: Env):
    commit_txn(env)
    env.txn_id = None
    env.instruction = None


def tpl_abort(env: Env):
    abort_txn(env)
    env.txn_id = None
    env.instruction = None


@fdb.transactional
def log_invoke(tr, env: Env) -> str:
    v2 = tr.get(fdb.tuple.pack(("log", env.table, env.instance_id, env.step)))
    if v2.present():
        env.step += 1
        return deserialize(v2)
    new_id = str(uuid4())
    tr[fdb.tuple.pack(("log", env.table, env.instance_id, env.step))] = serialize(new_id)
    return new_id