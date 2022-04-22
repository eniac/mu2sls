import argparse
from pprint import pprint

import fdb

fdb.api_version(630)
db = fdb.open()


def print_field(field):
    pprint(db[fdb.tuple.range((field,))])


def main(field):
    if field == "all":
        for field in ["data", "lock", "log", "local"]:
            print(field, ":")
            print_field(field)
            print('-' * 20)
    else:
        print_field(field)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--field", "-f", default="all")
    args = parser.parse_args()
    main(args.field)
