import fdb

def main():
    fdb.api_version(630)
    db = fdb.open()
    del db[fdb.tuple.range(("data",))]
    del db[fdb.tuple.range(("log",))]
    del db[fdb.tuple.range(("lock",))]
    del db[fdb.tuple.range(("local",))]


if __name__ == '__main__':
    main()
