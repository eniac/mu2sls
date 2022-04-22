import argparse
import json
from pprint import pprint


def user_log(filename):
    with open(filename, 'r') as f:
        res = []
        for line in f.readlines():
            entry = json.loads(line)
            if entry['kubernetes']['container_name'] == 'user-container':
                res.append(entry)
        logs = [x['log'].strip() for x in res]
        user_logs = [x for x in logs if x.startswith('INFO')]
        user_logs = [x.split(':')[-1].strip() for x in user_logs]
        pprint(user_logs)


def main(args):
    user_log(args.filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--filename', '-f', help='log file')
    args = parser.parse_args()
    main(args)
