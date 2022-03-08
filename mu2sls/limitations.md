## Limitations

### Implementation

#### High Priority

These limitations are higher priority and will need to be fixed before the deadline:

- Transactions can fail and therefore we need to catch these failures with exception handling in the user-code.

#### Low Priority

These limitations here are lower priority, and therefore might not be fixed soon

- Asynchronous invocations are not really asynchronous at the moment
- Transactions that are in one another (for example one in caller and one in callee), won't work properly now (the intenral BeginTx and CommitTx should not do anything).
