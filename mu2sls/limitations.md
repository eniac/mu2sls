## Limitations

### Implementation

#### High Priority

These limitations are higher priority and will need to be fixed before the deadline:

- Transactions can fail and therefore we need to catch these failures with exception handling in the user-code.

#### Low Priority

These limitations here are lower priority, and therefore might not be fixed soon

- Currently, the implementation only supports method calls to update fields. Anything else, won't work.
  + For example, accessing fields with `__getattr__` uses an `eos` read which doesn't play well with transactions.
  + There is no fundamental problem with implementing those, it is simply engineering overhead.
  + To fix this, investigate all locations of `eos_*` in `wrappers.py`.
- Local AsyncInvoke is not actually asynchronous
- Transactions that are in one another (for example one in caller and one in callee), won't work properly now (the intenral BeginTx and CommitTx should not do anything).
