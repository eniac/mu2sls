import fdb.tuple

from runtime.common import *

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