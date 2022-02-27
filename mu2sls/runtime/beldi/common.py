import fdb
import os
import tempfile
from uuid import uuid4

fdb.api_version(630)

## TODO: Add a test that runs media with local deployment + Beldi store on FDB

def connect():
    """
    Open a connection to FDB. First tries to do it with a local file,
    and if that fails, tries with a remote file.
    """
    fdb_clust_file_path = os.getenv('FDB_CLUSTER_FILE')
    print("FDB_CLUSTER_FILE=", fdb_clust_file_path)
    if not fdb_clust_file_path is None:
        return connect_fdb_using_file(fdb_clust_file_path)

    ## If the FILE didn't work, then just try with data
    data = os.getenv('FDB_CLUSTER_DATA')
    print("FDB_CLUSTER_DATA=", data)
    if data is None:
        print("FDB_CLUSTER_DATA environment variable is not set!")
        exit(1)
    ## TODO: Remove tempfile
    _fdb_cluster_fid, fdb_clust_file_path = tempfile.mkstemp(dir=".", text=True)

    with open(fdb_clust_file_path, "w") as f:
        f.write(data)

    return fdb.open(fdb_clust_file_path)

def connect_using_local_file():
    fdb_clust_file_path = os.getenv('FDB_CLUSTER_FILE')
    print("FDB_CLUSTER_FILE=", fdb_clust_file_path)
    if fdb_clust_file_path is None:
        print("FDB_CLUSTER_FILE environment variable is not set!")
        exit(1)
    return connect_fdb_using_file(fdb_clust_file_path)

def connect_fdb_using_file(fdb_clust_file_path):
    return fdb.open(fdb_clust_file_path)

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

##
## This file contains all possible environments that are used by our compiler
##
## The environment, is like a context object, that contains necessary information
## for the deployment, like
##   - Connection Info for the database and other services
##   - A request_id that uniquely identifies each request
##   - 
##

##
## This is the knative distributed environment
##
class Env:
    def __init__(self, table):
        ## TODO: Make it possible to get an instance_id from the caller
        
        ## TODO: Rename instance_id to request_id
        self.instance_id = str(uuid4())

        ## The name of the table for that particular function
        self.table = table

        ## A step number that is used to index through the log and
        ## to differentiate between different calls.
        self.step = 1

        ## A connection to the database
        self.db = connect()

        ## No need for load_balancer_ip in Beldi Env
        self.load_balancer_ip = get_load_balancer_ip()
