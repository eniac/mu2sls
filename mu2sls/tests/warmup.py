import subprocess

import test_services

deployment_file = "media-service-test.csv"


def main():
    deployment_list, service_list = test_services.deployment_list_from_deployment_file(deployment_file)
    deployment_list = [x[0] for x in deployment_list]
    for name in deployment_list:
        res = subprocess.run(
            f'kn service update {name} --scale-min 2 --annotation "autoscaling.knative.dev/target=500"',
            shell=True, stdout=subprocess.PIPE)
        res = res.stdout.decode('utf-8').strip()
        print(f"{name}: {res}")


if __name__ == '__main__':
    main()
