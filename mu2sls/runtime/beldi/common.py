import json
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
    def __init__(self, table, req_id=None):
        
        ## The identifier of the request that we are currently handling
        self.req_id = req_id

        ## A step number that is used to index through the log and
        ## to differentiate between different calls.
        self.step = 1

        ## A number that identifies how many calls (invocations)
        ## we have done to other services to be able to generate
        ## new request identifiers for them.
        self.number_of_calls = 0

        ##
        ## Transaction state
        ##

        ## Transaction id contains the identifier of a transaction,
        ## that is passed across callees and is used to own keys in the store.
        self.txn_id = None

        ## The mode that we are in, could be either:
        ## - "EXECUTE"
        ## - "COMMIT"
        ## - "ABORT"
        self.instruction = None

        ## The level of nested transaction (used to avoid commiting early)
        ##
        ## For example, if we have:
        ## ```
        ##   begin_txn
        ##   begin_txn
        ##   ...
        ##   commit_txn
        ##   commit_txn
        ## ```
        ##
        ## We only want to commit the outer layer.
        ## Note that this can happen either: 
        ##  - because a user has written a transaction in both the caller and the callee
        ##  - Because of the automatic compilation of "updates" to use transactions (can be solved)
        ##  - if the user accidentally added nested transactions in the same service
        ##
        ## Then begin_txn should increase this value instead of starting a new transaction
        ##   if we are already in a transaction.
        ##
        ## Commit should reduce this if it is not the last one (only the outer commit works).
        ##
        ## Abort should immediately abort, and later aborts and commits should be ignored.
        ##
        ## TODO: Implement this and check if it is correct.

        ## TODO: The following steps should just happen once per instantiation
        ##       and not once per request.
        ##
        ##       Maybe we can achieve that, by having a reinit_env function that 
        ##       simply updates.

        ## The name of the table for that particular function
        self.table = table

        ## A connection to the database
        self.db = connect()

        ## No need for load_balancer_ip in Beldi Env
        self.load_balancer_ip = get_load_balancer_ip()

    def __repr__(self):
        return f'Env(table: {self.table}, db: {self.db}, lb-ip: {self.load_balancer_ip}, reqid: {self.req_id}, step: {self.step}, #calls: {self.number_of_calls}, txn-id: {self.txn_id}, txn-mode: {self.instruction})'

    def increase_calls(self):
        self.number_of_calls += 1
    
    def in_txn_commit_or_abort(self):
        return (self.instruction in ["COMMIT", "ABORT"])

    def in_txn(self):
        return (self.instruction is not None)

    ##
    ## Two complementary methods that inject and extract metadata into calls
    ##

    ## Creates a dictionary with the request metadata
    def inject_request_metadata(self) -> dict:
        metadata_dict = {}

        
        ## Get the request_id and the step_number from the environment
        ##   and use them to create a new request id for the call to the callee.
        ##
        ## TODO: @Haoran: is that OK? This corresponds to the formalization.
        metadata_dict['req_id'] = f'{self.req_id}-{self.number_of_calls}'

        ## If we are in a transaction
        if self.txn_id is not None:
            assert self.instruction is not None
            metadata_dict['txn_id'] = self.txn_id
            metadata_dict['instruction'] = self.instruction
        
        print("Created metadata:", metadata_dict)
        return metadata_dict

    ## Modifies env to include the metadata from the request
    def extract_request_metadata(self, json_dict: dict):
        print("Extracting metadata from:", json_dict)

        ## The request should always have a request_id
        self.req_id = json_dict['req_id']

        if 'txn_id' in json_dict:
            self.txn_id = json_dict['txn_id']
            self.instruction = json_dict['instruction']
