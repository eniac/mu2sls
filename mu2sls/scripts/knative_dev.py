import os
import shutil
import subprocess
import tempfile

def run(cmd):
    res = subprocess.run(cmd, stdout=subprocess.PIPE)
    return res.stdout.decode('utf-8').strip()

HOME = run(["git", "rev-parse", "--show-toplevel", "--show-superproject-working-tree"])
MUSLS = os.path.join(HOME, "mu2sls")

## TODO: Pass the csv as an argument and move that to a shell script maybe?
def compile(target_dir):
    compiler = os.path.join(MUSLS, "scripts/compile_services.sh")
    deploy = os.path.join(MUSLS, "tests/media-service-test.csv")
    sls_backend = "knative"
    res = run(["bash", compiler, deploy, target_dir, "-s", sls_backend])
    print(res)

def prepare(target_dir):
    ## Create a kmedia directory to store all the files that are necessary
    ##   for building and deploying to knative.
    kmedia = os.path.join(MUSLS, "kmedia")
    shutil.rmtree(kmedia, ignore_errors=True)
    os.mkdir(kmedia)

    ## Copy all the flask handlers to their own directories.
    filenames = [fn for fn in os.listdir(target_dir)
                 if os.path.isfile(os.path.join(target_dir, fn))]
    for fn in filenames:
        name = fn.split(".")[0]
        os.mkdir(os.path.join(kmedia, name))
        shutil.copyfile(os.path.join(MUSLS, "target", fn), os.path.join(kmedia, name, "app.py"))

        ## TODO: The dockerfile copying is not necessary anymore
        with open(os.path.join(MUSLS, "Dockerfile"), "r") as f:
            dockerfile = f.read()
        ## TODO: Do that properly by adding a reference to an 
        ##       environment variable in the Dockerfile
        dockerfile = dockerfile.replace("PLACEHODLER", name)
        with open(os.path.join(kmedia, name, "Dockerfile"), "w") as f:
            f.write(dockerfile)
    
    ## TODO: This is not necessary anympore
    ## Copy compiler and runtime
    src_compiler_dir = os.path.join(MUSLS, "compiler")
    dst_compiler_dir = os.path.join(kmedia, "compiler")
    shutil.copytree(src_compiler_dir, dst_compiler_dir)
    
    src_runtime_dir = os.path.join(MUSLS, "runtime")
    dst_runtime_dir = os.path.join(kmedia, "runtime")
    shutil.copytree(src_runtime_dir, dst_runtime_dir)
    



def main():
    target_dir = tempfile.mkdtemp()
    compile(target_dir)
    prepare(target_dir)
    shutil.rmtree(target_dir)

if __name__ == '__main__':
    main()