import fdb
import json
import os
import tempfile
from uuid import uuid4

fdb.api_version(630)

## TODO: Add a test that runs media with local deployment + Beldi store on FDB

def connect():
    """
    Open a connection to FDB
    """
    data = os.getenv('FDB_CLUSTER_DATA')
    print("FDB_CLUSTER_DATA=", data)
    if data is None:
        print("FDB_CLUSTER_DATA environment variable is not set!")
        exit(1)
    ## TODO: Remove tempfile
    _fdb_cluster_fid, fdb_clust_file_path = tempfile.mkstemp(dir=".", text=True)

    with open(fdb_clust_file_path, "w") as f:
        f.write(data)

    db = fdb.open(fdb_clust_file_path)
    return db

def connect_using_local_file():
    fdb_clust_file_path = os.getenv('FDB_CLUSTER_FILE')
    print("FDB_CLUSTER_FILE=", fdb_clust_file_path)
    if fdb_clust_file_path is None:
        print("FDB_CLUSTER_FILE environment variable is not set!")
        exit(1)
    return connect_fdb_using_file(fdb_clust_file_path)

def connect_fdb_using_file(fdb_clust_file_path):
    db = fdb.open(fdb_clust_file_path)
    return db

def get_load_balancer_ip():
    """
    Find the cluster IP for calling other functions
    """
    ip = os.getenv('LOAD_BALANCER_IP')
    print("LOAD_BALANCER_IP=", ip)
    if ip is None:
        print("LOAD_BALANCER_IP environment variable is not set!")
        exit(1)
    return ip

## TODO: Move those to a different file that deals with connection and configuration.
##       Also, clean up!
class Env:
    def __init__(self, table):
        self.instance_id = str(uuid4())
        self.table = table
        self.step = 1
        self.db = connect()
        self.load_balancer_ip = get_load_balancer_ip()

class LocalBeldiEnv:
    def __init__(self, table):
        self.instance_id = str(uuid4())
        self.table = table
        self.step = 1
        self.db = connect_using_local_file()
        # self.load_balancer_ip = get_load_balancer_ip()

def serialize(item):
    return json.dumps(item).encode()


def deserialize(bitem: bytes):
    return json.loads(bitem.decode())