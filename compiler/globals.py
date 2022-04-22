
## The names of all invocation functions
INVOKE_FUNCTION_NAMES = ['SyncInvoke', 'AsyncInvoke']
INVOKE_LIB_FUNCTION_NAMES = INVOKE_FUNCTION_NAMES + ['Wait', 'WaitAll']

TXN_FUNCTION_NAMES = ['BeginTx', 'CommitTx', 'AbortTx', 'AbortTxNoExc']

BELDI_LOGGER_CLASS_NAME = 'BeldiLogger'

# WEB_FRAMEWORK = 'Flask'
WEB_FRAMEWORK = 'Quart'