import argparse
import os
import shutil
import subprocess
import tempfile


def run_collect_output(cmd):
    ## Note: PIPE for stdout is problematic when we don't gather the output in var,
    ## because it prints all output at once in the end and the stderr in the process. 
    res = subprocess.run(cmd, stdout=subprocess.PIPE)
    return res.stdout.decode('utf-8').strip()

MUSLS = run_collect_output(["git", "rev-parse", "--show-toplevel", "--show-superproject-working-tree"])
KNATIVE_DOCKERFILE = os.path.join(MUSLS, "scripts", "BasicKnativeDockerfile")

## TODO: Pass the csv as an argument and move that to a shell script maybe?
def compile(target_dir, args):
    compiler = os.path.join(MUSLS, "scripts/compile_services.sh")
    deploy = args.deployment_file
    # deploy = os.path.join(MUSLS, "tests/media-service-test.csv")
    sls_backend = "knative"
    res = subprocess.run(["bash", compiler, deploy, target_dir, "-s", sls_backend])
    return res

## Create and push the docker containers preparing for a knative deployment
def prepare(rel_target_dir, docker_io_username, deployment_file):

    ## Get the basename of the deployment file as namespace for the docker images
    image_namespace = os.path.basename(deployment_file).split(".")[0]

    ## Build a container for each compiled service
    filenames = [fn for fn in os.listdir(rel_target_dir)
                 if os.path.isfile(os.path.join(rel_target_dir, fn))]
    for fn in filenames:
        ## The service name is the first part (without the .py)
        service_name = fn.split(".")[0]

        rel_path_to_app_file = os.path.join(rel_target_dir, fn)
        docker_build(rel_path_to_app_file,
                     docker_io_username,
                     image_namespace,
                     service_name)

        docker_push(docker_io_username, image_namespace, service_name)
    
## It is necessary to build and push to docker so that it can be pulled by knative
def docker_build(app_file, docker_username, image_namespace, service_name):
    res = subprocess.run(["docker", "build", 
                          "-f", KNATIVE_DOCKERFILE,
                          "--build-arg", f'app_file={app_file}',
                          "-t", f'{docker_username}/{image_namespace}-{service_name}',
                          MUSLS])
    return res 

def docker_push(docker_username, image_namespace, service_name):
    res = subprocess.run(["docker", "push", f'{docker_username}/{image_namespace}-{service_name}'])
    return res 

def deploy_services(docker_username, service_list, deployment_file,
                    enable_logging=True,
                    enable_txn=True,
                    enable_custom_dict=False):
    ## Get the basename of the deployment file as namespace for the docker images
    image_namespace = os.path.basename(deployment_file).split(".")[0]

    for service in service_list:
        knative_service_name, docker_io_name = service
        res = subprocess.run(["bash", "deploy.sh", 
                              docker_username,
                              knative_service_name,
                              f'{image_namespace}-{docker_io_name}',
                              '--env', f'ENABLE_LOGGING={enable_logging}',
                              '--env', f'ENABLE_TXN={enable_txn}',
                              '--env', f'ENABLE_CUSTOM_DICT={enable_custom_dict}'])

def main():
    args = parse_arguments()

    ## Create a kmedia directory to store all the files that are necessary
    ##   for building and deploying to knative.
    rel_target_dir = "kmedia"
    kmedia = os.path.join(MUSLS, rel_target_dir)
    shutil.rmtree(kmedia, ignore_errors=True)
    os.mkdir(kmedia)

    compile(kmedia, args)
    prepare(rel_target_dir, args.docker_io_username, args.deployment_file)
    shutil.rmtree(kmedia)



def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("docker_io_username", help="the docker_io username to push/pull the images")
    parser.add_argument("deployment_file", 
                        help="the deployment file (a csv)")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    main()