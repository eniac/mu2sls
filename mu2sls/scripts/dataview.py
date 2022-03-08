import fdb
from pprint import pprint

fdb.api_version(630)
db = fdb.open()
pprint(db[fdb.tuple.range(("data",))])
