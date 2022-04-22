
##
## This contains utility code for sending requests and responses
## that have to do with transactions.
##

## A response sent to a caller when the current transaction needs to be aborted
def abort_response() -> str:
    return "ABORT"

def is_abort_response(resp: str):
    return resp == "ABORT"