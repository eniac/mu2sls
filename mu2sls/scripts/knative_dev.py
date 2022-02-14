import os
import shutil
import subprocess

def run(cmd):
    res = subprocess.run(cmd, stdout=subprocess.PIPE)
    return res.stdout.decode('utf-8').strip()

HOME = run(["git", "rev-parse", "--show-toplevel", "--show-superproject-working-tree"])
MUSLS = os.path.join(HOME, "mu2sls")
TARGET_DIR = os.path.join(MUSLS, "target")


## TODO: Pass the csv as an argument and move that to a shell script maybe?
def compile():
    compiler = os.path.join(MUSLS, "scripts/compile_services.sh")
    deploy = os.path.join(MUSLS, "tests/media-service-test.csv")
    sls_backend = "knative"
    res = run(["bash", compiler, deploy, TARGET_DIR, "-s", sls_backend])
    print(res)

def prepare():
    kmedia = os.path.join(MUSLS, "kmedia")
    shutil.rmtree(kmedia, ignore_errors=True)
    os.mkdir(kmedia)
    filenames = [fn for fn in os.listdir(TARGET_DIR)
                 if os.path.isfile(os.path.join(TARGET_DIR, fn))]
    for fn in filenames:
        name = fn.split(".")[0]
        os.mkdir(os.path.join(kmedia, name))
        with open(os.path.join(MUSLS, "Dockerfile"), "r") as f:
            dockerfile = f.read()
        ## TODO: Do that properly by adding a reference to an 
        ##       environment variable in the Dockerfile
        dockerfile = dockerfile.replace("PLACEHODLER", name)
        with open(os.path.join(kmedia, name, "Dockerfile"), "w") as f:
            f.write(dockerfile)
        shutil.copyfile(os.path.join(MUSLS, "target", fn), os.path.join(kmedia, name, "app.py"))


def main():
    compile()
    prepare()

if __name__ == '__main__':
    main()