
__TODO__:
- Is there a way to give the exact Cloudlab configuration setup in a programatic way for them to start the cloudlab instance?
- Should we provide source code on Zenodo or github?
- TODO: Provide a virtual box with all dependencies for both local and remote development.
- TODO: Make sure that running all experiments one after the other gives reasonable results (sometime it didn't when we run it on our own)
- TODO: Sometimes the fdb database gets stuck, and it requires restarting (semaphore issue) 
```sh
sudo service foundationdb stop
sleep 60
sudo service foundationdb start
```
- TODO: Maybe add the kill kn service between invocations `kn service delete --all`

# Artifact Documentation for "Executing Microservice Applications on Serverless, Correctly"

This document describes the artifact for the POPL 23 paper titled "Executing Microservice Applications on Serverless, Correctly".

It contains 5 sections:
- List of Claims
- Download, installation, and sanity-testing instructions
- Evaluation instructions
- Reusability instructions
- Additional Description


## List of Claims

Our artifact contains all claims made in the paper regarding the prototype and its evaluation. The proofs in the paper are not mechanized and therefore are not part of the artifact.

The claims made in our paper are:
- We have developed the `mu2sls` prototype that generates a serverless implementation from a set of service specifications. You can find information about this claim in the __Additional Artifact Information__ __TODO: Link__ section, where we describe the structure of the artifact code, and how it corresponds to the paper.
- We have evaluated our prototype w.r.t. the three questions (Q1), (Q2), (Q3) described in Section 8. You can reproduce the experiments for this claim by following the __Evaluation Instructions Section__ __TODO: Link__.

## Download, installation, and sanity-testing instructions

You have to satisfy the following three requirements for the "Sanity-Check" part of our paper artifact:
- Create a Cloudlab account and check that you can connect to cloudlab machines
- Download the source code of our artifact and install requirements
- Run local and remote tests of our artifact

### Creating a Cloudlab account

All of the experiments on our paper run on [Cloudlab](https://www.cloudlab.us/) machines, which you can get access to for free with your institution email. You can use the following [link](https://cloudlab.us/signup.php) to register for a cloudlab account. 

Once you have the account, set up a key to be able to connect to Cloudlab machines using `ssh` and make sure that you can start a machine and connect to it.

### Downloading artifact and installing requirements

The virtual box instance should contain all these requirements, but we are providing them here for completeness. Feel free to skip this section if you are using virtualbox.

Our artifact has the following requirements:
- To run the local artifact tests:
  + `git`, `python3` 
  + Python3 packages as shown in `requirements.txt`
  + Download the artifact code from [github](https://github.com/angelhof/mu2sls.git)
- To run the experiments on cloudlab:
  + `rsync` and `mosh`
- To modify the code and run your own microservice applications on cloudlab:
  + `docker` so that you can push images to docker.io 

On most Ubuntu distributions you can install all of them using:
```sh
sudo apt update
sudo apt install git python3 rsync mosh

git clone https://github.com/angelhof/mu2sls.git

cd mu2sls
python3 -m pip install -r requirements.txt

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
- Physical node type: c6525-25g (if available to get the same results as the ones we got in the paper)

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
sudo apt install mosh
```

Now you can log in the remote node and setup knative:

```sh
mosh --ssh="ssh -p 22 -i ${private_key}" ${node_username}@${node_address}

## On the remote machine:
tmux # Use tmux to be able to detach

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

TODO

In order to get the same exact results, you can use the `c6525-25g` configuration on cloudlab. Just note that this is a powerful machine, so you might need to reserve it in advance before using it on Cloudlab.

In the cloudlab machine, run all the experiments (Q1-Q3) using:

```sh
bash run_all_eval.sh
```

__TODO: Write how much time are the experiments supposed to take__
- About two-three hours for small experiments
- about XXX hours for media
- about XXX hours for hotel_reservation


This takes about __TODO: XXX__ so you can leave it running and come back later. It prints request statistics for each experiment while it runs. 

Then you need to pull results locally using:

__TODO: Add a script that pulls all results__

```sh
scp -i ${private_key} ${node_username}@${node_address}:knative/single_stateful.log ./results/single_stateful.log
scp -i ${private_key} ${node_username}@${node_address}:knative/chain.log ./results/chain.log
scp -i ${private_key} ${node_username}@${node_address}:knative/tree.log ./results/tree.log
```

and then you can plot the results using:

```sh
python3 experiments/plot-results.py
```

which generates plots in `plots`.




## Reusability Instructions

You can use `mu2sls` for your application by developing its services using the programming model that `mu2sls` supports. 

For an example of a service `Caller2` that simply forwards its results to a backend service (`Backend`) see `tests/source_specs/async-test/caller2.py`, and for the example of a backend service that tries to perform a transaction where it increments the counter for the input key see `tests/source_specs/async-test/backend.py`.

Then, you have to write a `csv` file that contains the information for all services for the compiler to compile them and to be able to build and deploy them.

For an example of a csv file that composes `Caller2`, `Backend`, and a frontend service `Caller1`, see `experiments/chain.csv`.

The names of the services (which need to correspond with their class definitions) are in the first field of the csv and the source files of the application services are indicated in the second field of the `csv` files.

Then you can use __TODO: XXX__ to deploy your services locally with a python interpreter. To deploy them remotely, you need to __TODO__.


## Additional Artifact Information

TODO:
- Explain how different parts in the paper correspond to the code in the artifact