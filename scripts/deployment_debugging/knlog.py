import argparse
import subprocess


def run_collect_output(cmd):
    res = subprocess.run(cmd, stdout=subprocess.PIPE)
    return res.stdout.decode('utf-8').strip()


def main(name):
    pod_ls = run_collect_output(['kubectl', 'get', 'pods'])
    pod_ls = pod_ls.split('\n')
    pod_ls = [x for x in pod_ls if name in x]
    # assert len(pod_ls) == 1
    pod = pod_ls[0]
    pod_name = pod.split()[0]
    logs = run_collect_output(['kubectl', 'logs', pod_name, 'user-container'])
    print(logs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('name', help='log file')
    args = parser.parse_args()
    main(args.name)
