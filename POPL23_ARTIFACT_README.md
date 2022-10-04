# Artifact Location

The following Zenodo link contains a virtual machine image that can be used to run the local experiments and orchestrate the evaluation on cloudlab (TODO: Add link).

The source code of our artifact can be found here (https://github.com/angelhof/mu2sls) and the artifact README can also be found here (https://github.com/angelhof/mu2sls/blob/main/POPL23_ARTIFACT_README.md).

# Artifact Documentation for "Executing Microservice Applications on Serverless, Correctly"

This document describes the artifact for the POPL 23 paper titled "Executing Microservice Applications on Serverless, Correctly".

It contains 5 sections:
- List of Claims
- Download, installation, and sanity-testing instructions
- Evaluation instructions
- Reusability instructions
- Additional Description
- Troubleshooting


## List of Claims

Our artifact contains all claims made in the paper regarding the prototype and its evaluation. The proofs in the paper are not mechanized and therefore are not part of the artifact.

The claims made in our paper are:
- We have developed the `mu2sls` prototype that generates a serverless implementation from a set of service specifications. You can find information about this claim in the "Additional Artifact Information" section, where we describe the structure of the artifact code, and how it corresponds to the paper.
- We have evaluated our prototype w.r.t. the three questions (Q1), (Q2), (Q3) described in Section 8. You can reproduce the experiments for this claim by following the "Evaluation Instructions Section".

## Download, installation, and sanity-testing instructions

You have to satisfy the following three requirements for the "Sanity-Check" part of our paper artifact:
- Create a Cloudlab account and check that you can connect to cloudlab machines
- Download the source code of our artifact and install requirements
- Run local and remote tests of our artifact

### Creating a Cloudlab account

All of the experiments on our paper run on [Cloudlab](https://www.cloudlab.us/) machines, which you can get access to for free with your institution email. You can use the following [link](https://cloudlab.us/signup.php) to register for a cloudlab account. 

Once you have the account, set up a key to be able to connect to Cloudlab machines using `ssh` and make sure that you can start a machine and connect to it.

### Downloading artifact and installing requirements

The virtual box instance should contain all these requirements, but we are providing them here for completeness. Skip this section if you are using virtualbox.

Our artifact has the following requirements:
- To run the local artifact tests:
  + `git`, `python3.8` 
  + Python3 packages as shown in `requirements.txt`
  + Download the artifact code from [github](https://github.com/angelhof/mu2sls.git)
  + foundationdb client and python API
- To run the experiments on cloudlab:
  + `rsync` and `mosh`
- To modify the code and run your own microservice applications on cloudlab:
  + `docker` so that you can push images to docker.io (if you want to rebuild the images yourself, which is not necessary to run the evaluation)

On most Ubuntu distributions you can install all of them using:
```sh
sudo apt update
sudo apt install git rsync mosh

## Install pyenv to install python3.8
sudo apt update; sudo apt install make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

curl https://pyenv.run | bash

## Add the necessary pyenv post-installation commands in .bashrc
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc
echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc
source ~/.bashrc
## Note that after this point we need to source /root/.bashrc before executing something with python3.8 in the Dockerfile

## Install and set python 3.8.13 as the global python version
pyenv install -v 3.8.13 && pyenv global 3.8.13


## Download the project and install its requirements
git clone https://github.com/angelhof/mu2sls.git

cd mu2sls
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
bash scripts/install_fdb_client.sh

## To install docker on Ubuntu follow this guide: https://docs.docker.com/desktop/install/ubuntu/
```

### Running the local and remote tests

To run the local tests, simply navigate to the `mu2sls` directory and then execute `./run_tests.sh`. You should get no failing test and no error, just a skipped test.

To run a remote test, you need to follow the following instructions.

#### Installing mu2sls and knative on a Cloudlab machine

You need to follow these instructions from the virtual box image (or a machine that satisfies the requirements described above).

##### Start a Cloudlab Machine

First, create a cloudlab experiment. As a profile, select `small-lan`, and as parametrization choose (see also image in `docs/cloudlab_parametrization.PNG`):
- Number of Nodes: 1
- OS image: UBUNTU 18.04
- Physical node type: c6525-25g (if available to get the same results as the ones we got in the paper). If that is not available, you should use an AMD node so that the installation works.

Leave the rest of the parameters as they are. Then pick a name for the experiment and a project and start the experiment.

You then have to wait until your experiment is ready, at which point you should copy the node from the `SSH command` column from the `List View` tab.

##### Setup the Cloudlab machine

Create a `vars.sh` file based on `vars_template.sh` and modify the node address and username (as copied from cloudlab) and the location of your ssh key. Leave the docker_io_username as is.

Source the vars file to be able to easily run the following scripts.
```sh
source vars.sh
```

Upload all relevant files there using:

```sh
./scripts/upload-to-remote.sh cloudlab ${node_address} ${node_username} ${private_key}
## You will have to type yes due to connecting to this host for the first time
```

Login the remote machine to install mosh (for a better experience when using a low quality network):

```sh
ssh -i ${private_key} ${node_username}@${node_address}

## On the remote machine:
sudo apt update
sudo apt install mosh -y
```

Now you can log in the remote node and setup knative:

```sh
mosh --ssh="ssh -p 22 -i ${private_key}" ${node_username}@${node_address}

## On the remote machine:
tmux # Use tmux to be able to detach
## Reattach using: `tmux attach-session`

## In the tmux session
## Copy each of the following lines separately, because they cannot all be pasted at once
cd knative; ./setup1.sh

## Relogin
sudo su - ${USER}

cd knative; ./setup2.sh
```

##### Start the cluster

You can start the `knative` cluster using:
```sh
./start-cluster.sh
```

Then you need to setup all environment variables to be able to run experiments:
```sh
source setup_env_vars.sh
```

##### Run a test on the cluster

Run a simple test with a single-stateful service.
```sh
python3 test_services.py media-service-test.csv knative --docker_io_username konstantinoskallas

## The output should looks something like this:
# fatal: not a git repository (or any of the parent directories): .git
# Deploying composereview...
# Downloading image from docker.io/konstantinoskallas/media-service-test-compose_review...
# Updating Service 'composereview' in namespace 'default':

#   0.013s The Configuration is still working to reflect the latest desired specification.
#   3.782s Traffic is not yet migrated to the latest revision.
#   3.806s Ingress has not yet been reconciled.
#   3.818s Waiting for load balancer to be ready
#   4.009s Ready to serve.

# Service 'composereview' updated to latest revision 'composereview-00001' is available at URL:
# http://composereview.default.example.com
# Deploying frontend...
# ...
# ...
# ...
# Service 'userreview' updated to latest revision 'userreview-00001' is available at URL:
# http://userreview.default.example.com
# ERROR:root:sync_invoke 28
# ERROR:root:sync_invoke 24
# ERROR:root:sync_invoke 147
```

The `ERROR`s in the end are just logs that show the time it took to execute the requests, so they might be slightly different. This output shows that the test works.

## Evaluation Instructions

In order to get the same exact results, you can use the `c6525-25g` configuration on cloudlab. Just note that this is a powerful machine, so you might need to reserve it in advance before using it on Cloudlab.

In the cloudlab machine, run all the experiments (Q1-Q3) using:

```sh
bash run_all_eval.sh --single_stateful --chain --tree --media --hotel
```

__TODO: Write how much time are the experiments supposed to take__

This takes about __TODO: XXX__ so you can leave it running and come back later. It prints request statistics for each experiment while it runs. 

Then you need to pull results on your local machine (virtualbox) using:

```sh
bash experiments/pull_results.sh "${private_key}" "${node_username}" "${node_address}"
```

and then you can plot the results using:

```sh
python3 experiments/plot-results.py
```

which generates three plots in the `plots` directory, named `figure9.pdf`, `figure10.pdf`, and `figure11.pdf`, corresponding to the ones in the paper.


## Reusability Instructions

You can use `mu2sls` for your application by developing its services using the programming model that `mu2sls` supports. 

For an example of a service `Caller2` that simply forwards its results to a backend service (`Backend`) see `tests/source_specs/async-test/caller2.py`, and for the example of a backend service that tries to perform a transaction where it increments the counter for the input key see `tests/source_specs/async-test/backend.py`.

Then, you have to write a `csv` file that contains the information for all services for the compiler to compile them and to be able to build and deploy them. You should put this `csv` file in the `experiments` directory if you want to reuse our scripts for uploading it to the remote cluster.

For an example of a csv file that composes `Caller2`, `Backend`, and a frontend service `Caller1`, see `experiments/chain.csv`.

The names of the services (which need to correspond with their class definitions) are in the first field of the csv and the source files of the application services are indicated in the second field of the `csv` files.

Then you can add a test for your application by adding a function in `tests/test_services.py` and then adding a line in the `TEST_FUNC_FROM_FILE` definition (lines 132-139 in `tests/test_services.py`) to associate your `csv` application file with the test function name. To write the test function, see `run_test_async` (lines 118-130 in `tests/test_services.py`).

You can add multiple calls to your test, first calling a few "update" methods and then calling some method that shows the state to test that it was updated correctly.

Then you can run this test locally by calling the following:

```sh
export csv_file=# Your csv file
python3 tests/test_services.py "${csv_file}" local
```

As a bonus, to run the test remotely, you first need to build and push the docker images and upload the csv to the remote machine using the following:

```sh
export csv_file=# Your csv file
export docker_io_username=# your docker.io username so that you push the images
python3 scripts/knative_dev.py "${docker_io_username}" "${csv_file}"

## For the following to find your csv and upload it, it needs to be in the
## experiments directory.
./scripts/upload-to-remote.sh cloudlab ${node_address} ${node_username} ${private_key}
```

and then connect to the remote machine where the cluster is running (see the "Setup the Cloudlab machine" section above), and run:

```sh
## On the remote machine
export csv_file=# The csv file path on the remote machine
export docker_io_username=# your docker.io username where you have pushed the images
python3 test_services.py "${csv_file}" knative --docker_io_username "${docker_io_username}"
```

## Additional Artifact Information

This section describes the code of the artifact and how it is split among directories. 
- First of all, `experiments` and `tests` contain service definitions, workload definitions, and scripts related to experiment running. 
- The `scripts` directory contains utility scripts.
- The `compiler` directory contains the translation components.
  + `service.py` defines what a service and its state is.
  + `ast_utils.py` contains utility functions for manipulating python ASTs.
  + `compiler.py` contains the end-to-end translation; it calls `frontend.py`, which finds services, it orchestrates them accordingly, and then calls `backend.py` to turn them back to python code.
- The `runtime` directory contains the runtime components that wrap calls and provide storage functionality. The most important modules are described below:
  + `runtime/beldi/logger.py` and `runtime/beldi/beldi.py` contain the implementation of the instrumentation (Sections 5 and 6) that ensures that method updates are atomic, and that implements transactions and logging on top of a key-value store.
  + the `runtime/local` directory contains the local instrumentation that allows for local deployment and debugging.
  + `runtime/wrappers.py` is the module that wraps arbitrary python objects and uses the `logger.py` to implement their method updates. It also contains the optimizer wrapper (described in Section 7 of the paper).


## Troubleshooting

Each experiment takes about a few minutes to run, and therefore if something gets stuck for much longer than that (no new output), you could interrupt the experiments using CTRL+C, and then clean up the database and loaded serverless functions using:
```sh
kn service delete --all
sudo service foundationdb stop
sleep 20
sudo service foundationdb start
```

Then you can rerun the rest of the evaluation by omiting the flags that have already successfully finished, e.g., if `single_stateful` has complete successfully, you can run:
```sh
bash run_all_eval.sh --chain --tree --media --hotel # omiting `--single_stateful` that has already executed
```