class TransactionException(Exception):
    """Exception raised when a transaction aborts.
       It needs to be caught by the user (when in a transaction)
         or by the compiler (when in the callee of a transaction).

       TODO: We need to be carefull to rethrow it, if caught in an internal
             transaction level.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message="Transaction aborted"):
        self.message = message
        super().__init__(self.message)