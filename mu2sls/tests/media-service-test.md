## Running the media service test

Here is the code that I used to run the media-service test (in the `openfaas-playground/mu2sls directory`)

First, upload the latest files to the remote cloudlab instance by running the following in the knproto directory (note that knproto needs to be a sibling directory to openfaas-playground):

```sh
./upload-to-remote.sh cloudlab amdXXX.utah.cloudlab.us ${cloudlab_user} ${path_to_ssh}
```

Then, ssh in the cloudlab instance and run:

```sh
cd knproto
./setup1.sh
sudo su - ${USER}
cd knproto
./setup2.sh
./start-cluster.sh

source setup_env_vars.sh
```

And now you are ready to execute things.

In the meantime, you should have compiled the media service in a local machine (from openfaas-playground/mu2sls):

```sh
python3 scripts/knative_dev.py konstantinoskallas tests/media-service-test.csv
```

instead of konstantinoskallas you can use your docker.io username.

Then on the cloudlab machine run:

```sh
python3 test_services.py media-service-test.csv knative --docker_io_username konstantinoskallas
```

The above deploys the services and runs a test.

Then you can run:

```sh
python3 populate_media.py
```

Then, we need to run the workload PENDING.

Some installation instructions for the workload generator (salvaged from my latest cloudlab machine):

```sh
cd knproto
git clone https://github.com/giltene/wrk2.git
cd wrk2
make

sudo apt install luarocks
sudo luarocks install json-lua
## or sudo luarocks install  https://raw.githubusercontent.com/tiye/json-lua/master/json-lua-0.1-3.rockspec
sudo luarocks install luasocket
sudo luarocks install uuid
```