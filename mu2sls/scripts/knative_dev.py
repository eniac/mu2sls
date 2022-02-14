import os
import shutil
import subprocess

def run(cmd):
    res = subprocess.run(cmd, stdout=subprocess.PIPE)
    return res.stdout.decode('utf-8').strip()

HOME = run(["git", "rev-parse", "--show-toplevel", "--show-superproject-working-tree"])
MUSLS = os.path.join(HOME, "mu2sls")

def compile():
    compiler = os.path.join(MUSLS, "scripts/compile_services.sh")
    deploy = os.path.join(MUSLS, "tests/media-service-test.csv")
    target = os.path.join(MUSLS, "target")
    sls_backend = "knative"
    res = run(["bash", compiler, deploy, target, "-s", sls_backend])
    print(res)

def prepare():
    kmedia = os.path.join(MUSLS, "kmedia")
    shutil.rmtree(kmedia, ignore_errors=True)
    os.mkdir(kmedia)
    filenames = os.listdir(os.path.join(MUSLS, "target"))
    for fn in filenames:
        name = fn.split(".")[0]
        os.mkdir(os.path.join(kmedia, name))
        with open(os.path.join(MUSLS, "Dockerfile"), "r") as f:
            dockerfile = f.read()
        dockerfile = dockerfile.replace("PLACEHODLER", name)
        with open(os.path.join(kmedia, name, "Dockerfile"), "w") as f:
            f.write(dockerfile)
        shutil.copyfile(os.path.join(MUSLS, "target", fn), os.path.join(kmedia, name, "app.py"))


def main():
    compile()
    prepare()

if __name__ == '__main__':
    main()