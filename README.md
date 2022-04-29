## Running experiments on cloudlab

__TODO:__ Simplify those

Local Requirements:
- `rsync`
- `mosh` (prefered)

We suggest setting all necessary variables in a variable file that you source, for example:

```sh
source vars.sh
```

We provide a template file in `vars_template.sh`.

#### Preparing Local setup

Start a machine with Ubuntu 18.04 and adequate CPU and RAM on cloudlab. Then upload all relevant files there using:

```sh
./scripts/upload-to-remote.sh cloudlab ${node_address} ${node_username} ${private_key}
```

Login the remote machine:

```sh
ssh -i ${private_key} ${node_username}@${node_address}
```

Not required: You can install `mosh` on the remote machine to have a better experience for low quality networks:

```sh
# On the remote machine
sudo apt update
sudo apt install mosh
```

Then you can log in the remote machine using:

```sh
mosh --ssh="ssh -p 22 -i ${private_key}" ${node_username}@${node_address}
```

#### Installing and Starting cluster

In the machine you better use `tmux` to be able to detach from the session:

```sh
tmux
```

To setup, you need to run two scripts:

```sh
cd knative
./setup1.sh

## Relogin
sudo su - ${USER}

cd knative
./setup2.sh
```

Then, you can start the `knative` cluster using:
```sh
./start-cluster.sh
```

#### (Local) Building and pushing application docker images

In order to run an application, you need to first build it on your local machine and push it to an image registry. If you need to do that, update the `$docker_io_username` variable in `vars.sh` to include your `docker_io_username`, alternatively, you can use the prebuilt images.

Example usage of build script:
```sh
## Build and deploy the single-stateful application
python3 scripts/knative_dev.py ${docker_io_username} tests/single-stateful.csv
```

#### Deploying an application and running tests

In order to deploy an application in the remote machine, you need to use the following script with the `.csv` file as the first argument. Change the `--docker_io_username` if you have built scripts in a different registry.

```sh
python3 test_services.py single-stateful.csv knative --docker_io_username konstantinoskallas
```

#### Running experiments

You can run the experiments for all small applications using the following command remotely:

```sh
bash eval_small_applications.sh
```

Then you need to pull results locally using:

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