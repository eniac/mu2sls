import argparse
import os
import shutil
import subprocess
import tempfile

def run(cmd):
    res = subprocess.run(cmd, stdout=subprocess.PIPE)
    return res.stdout.decode('utf-8').strip()

HOME = run(["git", "rev-parse", "--show-toplevel", "--show-superproject-working-tree"])
MUSLS = os.path.join(HOME, "mu2sls")
KNATIVE_DOCKERFILE = os.path.join(MUSLS, "scripts", "BasicKnativeDockerfile")

## TODO: Pass the csv as an argument and move that to a shell script maybe?
def compile(target_dir):
    compiler = os.path.join(MUSLS, "scripts/compile_services.sh")
    deploy = os.path.join(MUSLS, "tests/media-service-test.csv")
    sls_backend = "knative"
    res = subprocess.run(["bash", compiler, deploy, target_dir, "-s", sls_backend])
    print(res)

## Create and push the docker containers preparing for a knative deployment
def prepare(rel_target_dir, docker_io_username):    
    ## Build a container for each compiled service
    filenames = [fn for fn in os.listdir(rel_target_dir)
                 if os.path.isfile(os.path.join(rel_target_dir, fn))]
    for fn in filenames:
        ## The service name is the first part (without the .py)
        service_name = fn.split(".")[0]

        rel_path_to_app_file = os.path.join(rel_target_dir, fn)
        docker_build(rel_path_to_app_file,
                     docker_io_username,
                     service_name)
    
## It is necessary to build and push to docker so that it can be pulled by knative
def docker_build(app_file, docker_username, service_name):
    res = run(["docker", "build", 
                         "-f", KNATIVE_DOCKERFILE,
                         "--build-arg", f'app_file={app_file}',
                         "-t", f'{docker_username}/{service_name}',
                         MUSLS])
    return 


def main():
    args = parse_arguments()

    ## Create a kmedia directory to store all the files that are necessary
    ##   for building and deploying to knative.
    rel_target_dir = "kmedia"
    kmedia = os.path.join(MUSLS, rel_target_dir)
    shutil.rmtree(kmedia, ignore_errors=True)
    os.mkdir(kmedia)

    compile(kmedia)
    prepare(rel_target_dir, args.docker_io_username)
    shutil.rmtree(kmedia)



def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("docker_io_username", help="the docker_io username to push/pull the images")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    main()