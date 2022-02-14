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

## TODO: Actually the whole prepare is completely unneccessary.
def prepare(intermediate_dir, target_dir):
    ## Copy all the flask handlers to their own directories.
    filenames = [fn for fn in os.listdir(intermediate_dir)
                 if os.path.isfile(os.path.join(intermediate_dir, fn))]
    for fn in filenames:
        name = fn.split(".")[0]
        os.mkdir(os.path.join(target_dir, name))
        shutil.copyfile(os.path.join(MUSLS, "target", fn), os.path.join(target_dir, name, "app.py"))
    
## It is necessary to build and push to docker so that it can be pulled by knative
def docker_build_push(app_file, docker_username, service_name):
    res = run(["docker", "build", 
                         "-f", KNATIVE_DOCKERFILE,
                         "--build-arg", f'app_file={app_file}',
                         "-t", f'{docker_username}/{service_name}',
                         MUSLS])


def main():
    args = parse_arguments()

    ## An intermediate directory to hold the compiled files
    intermediate_dir = tempfile.mkdtemp()

    ## Create a kmedia directory to store all the files that are necessary
    ##   for building and deploying to knative.
    kmedia = os.path.join(MUSLS, "kmedia")
    shutil.rmtree(kmedia, ignore_errors=True)
    os.mkdir(kmedia)

    compile(intermediate_dir)
    prepare(intermediate_dir, kmedia)
    shutil.rmtree(intermediate_dir)

    rel_path_to_app_file = os.path.join("kmedia", "cast_info", "app.py")
    docker_build_push(rel_path_to_app_file,
                      args.docker_io_username,
                      "cast_info")

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("docker_io_username", help="the docker_io username to push/pull the images")
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    main()