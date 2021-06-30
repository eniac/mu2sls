## Setup and Instructions

I followed the tutorial shown here more or less (https://docs.openfaas.com/tutorials/first-python-function/).

You need to install:
 * `openfaas-cli`: to be able to control openfaas from your local machine
 * `k3d`: to be able to run openfaas on a Kubernetes backend locally (you could also use different kubernetes backends)
 * `arkade`: to install openfaas in kubernetes
 * `docker`: since k3d works on docker

### Prepare deployment

After having everything installed, you can run the following to make sure that the infrastructure is ready to deploy functions.

```sh
## Unclear what this does
kubectl rollout status -n openfaas deploy/gateway

## Forwards the gateway port to the local machine port so that the function can be invoked
kubectl port-forward -n openfaas svc/gateway 8080:8080 &

## Or the following for a different local port --- local:pod
kubectl port-forward -n openfaas svc/gateway 8090:8080 & 
## If you do this, you need to add this at the end of all commands: -g http://127.0.0.1:8090

## This is for metrics and not necessary
kubectl port-forward -n openfaas svc/prometheus 9090:9090 &

## Unclear when this is needed
PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)
echo -n $PASSWORD | faas-cli login --username admin --password-stdin 
```

Sometimes you might have to do (unclear when it is rerequired):
```sh
docker login --username konstantinoskallas
```
where you replace your username to be able to push and pull from the docker hub repository.

### Building a function

Assuming that you are in a folder that contains sources for a serverless function, e.g., one created by `faas-cli new hello-python3 --lang python3`, and that `./hello-python3.yml` contains an openfaas configuration (that also contains the name of an image and a public repository).

By running:

```sh
## Build
faas-cli build -f ./hello-python3.yml

## Push to a repository (haven't managed to make it work locally)
faas-cli push -f ./hello-python3.yml

## Deploy the function
faas-cli deploy -f ./hello-python3.yml

## Q: Sometimes removing it is required before deploying
faas-cli remove hello-python3
```

The function is ready to accept trafic and can be invoked using `faas-cli invoke` or `curl`.

## ComposePost Experiment

We now need to interface the serverless function with the rest of the social network.

The first requirement for this is to have adequate code in the function container (Thrift generated code etc).

An additional big requirement is to modify the Thrift Client to make requests that are understood by the serverless function. Maybe the HTTPClient can do the trick?

To build, push, and deploy:
```sh
faas-cli up -f compose-post.yml
```

### Preparation

```sh
mkdir compose-post-test
cd compose-post-test

faas-cli new compose-post --lang python3
```

### Setting up the container

In order to properly set up the container, I added the following in the YAML file of the function `compose-post.yml`.

```yml
configuration:
  copy:
    - ./gen-py
```

In addition, I added the following line in the `requirements.txt` file so that the python thrift library is included in the container:
```
thrift
```

Finally, I added the following lines in the beginning of the handler so that it finds the copied `gen-py` directory:
```python
import os
import sys

gen_py_path = os.path.join(os.path.dirname(__file__), 'gen-py')
sys.path.append(gen_py_path)
```

### Interfacing with HTTP

In order to interface the serverless function to be called using thrift, we need to slightly modify the microservice to not be a server (since serving is now handled by the OpenFaaS infrastructure) and we then need to modify the transport layer so that is interfaces directly with the input and output of the serverless function.

So we need to do the following:
  * Create an input transport that instead of actually reading from a transport it takes the function invocation input and spits it our little by little (as if it was reading it from a transport). (see `DummyReadHttpTransport`)
  * Create a fake transport that instead of actually writing to a transport it accumulates the output and then returns it through the function output. (see `DummyWriteTransport`)
  * Create a processor object that uses these two transports.

I also created a client `compose-post-client.py` to test out that this interfacing works!

### Interfacing with the rest of the microservices application

We need to make sure that the microservices all run and then that OpenFaaS is running, and then that the openfaas port is forwarded in the host (but not in 8080, but rather in 8090).

Note that since we forward the gateway port in the host, we need to make sure that the HttpClient in the mciroservice connects to the host.

> WARNING: There is a bug with buffered transport, I am not sure what exactly it is, but it leads to parsing of responses failing due to a \n in the middle of requests.

## Experimental and exploratory scripting to make the openfaas experiment work

```sh
## Installs openfaas
curl -sSL https://cli.openfaas.com | sudo sh

mkdir -p functions && cd functions

## Scaffolds a new python function
faas-cli new --lang python hello-python

## Or this for python3 (high perf recomment python3-flask or python3-hhtp)
faas-cli new hello-python3 --lang python3

## Build the function image
faas-cli build -f ./hello-python3.yml

## We need to push too, since I haven't managed to make it work locally
faas-cli push -f ./hello-python3.yml


## This creates a docker image

## We need to install a backend for OpenFaas.
## - faasd would work if I was running on native linux, but doesn't seem to work on WSL
## - So I am going with a local Kubernetes deployment.
##   + The first I found is k3d

## Run the following to create a kubernetes cluster (not clear if necessary)

k3d cluster create openfaas-test

## Resposnse
# INFO[0000] Prep: Network
# INFO[0000] Created network 'k3d-openfaas-test' (58dabf1b53c99602f7d3a61c6d0be3152500183e94d8d2ad6b20a13e975a5aab)
# INFO[0000] Created volume 'k3d-openfaas-test-images'
# INFO[0001] Creating node 'k3d-openfaas-test-server-0'
# INFO[0003] Pulling image 'docker.io/rancher/k3s:v1.21.1-k3s1'
# INFO[0008] Creating LoadBalancer 'k3d-openfaas-test-serverlb'
# INFO[0009] Pulling image 'docker.io/rancher/k3d-proxy:v4.4.6'
# INFO[0011] Starting cluster 'openfaas-test'
# INFO[0011] Starting servers...
# INFO[0011] Starting Node 'k3d-openfaas-test-server-0'
# INFO[0016] Starting agents...
# INFO[0016] Starting helpers...
# INFO[0016] Starting Node 'k3d-openfaas-test-serverlb'
# INFO[0017] (Optional) Trying to get IP of the docker host and inject it into the cluster as 'host.k3d.internal' for easy access
# INFO[0018] Successfully added host record to /etc/hosts in 2/2 nodes and to the CoreDNS ConfigMap
# INFO[0018] Cluster 'openfaas-test' created successfully!
# INFO[0018] --kubeconfig-update-default=false --> sets --kubeconfig-switch-context=false
# INFO[0018] You can now use it like this:
# kubectl config use-context k3d-openfaas-test
# kubectl cluster-info

## Run the following to delete the cluster
# k3d cluster delete openfaas-test

## Q: Running `kubectl cluster-info` returns only kubesystem "things" and I am not sure why

## Q: I did that `kubectl config use-context k3d-openfaas-test` as suggested but I have no idea what was the point.

## This seems to return the node (whether it is the one that runs the openfaas I have absolutely no idea)
kubectl get nodes

## After having a kubernetes cluster we install arkade to install openfaas on the cluster

## Run the following to install OpenFaas

arkade install openfaas

## which defaults to this
# arkade install openfaas --function-pull-policy "Always"


## In order to not pull images, we should use this. This is actually bad because it doesn't get the latest image
# arkade install openfaas --function-pull-policy "IfNotPresent"

## Notes after running it:
# To verify that openfaas has started, run:

#   kubectl -n openfaas get deployments -l "release=openfaas, app=openfaas"
# =======================================================================
# = OpenFaaS has been installed.                                        =
# =======================================================================

# # Get the faas-cli
# curl -SLsf https://cli.openfaas.com | sudo sh

# # Forward the gateway to your machine
# kubectl rollout status -n openfaas deploy/gateway
# kubectl port-forward -n openfaas svc/gateway 8080:8080 &

# # If basic auth is enabled, you can now log into your gateway:
# PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)
# echo -n $PASSWORD | faas-cli login --username admin --password-stdin

# faas-cli store deploy figlet
# faas-cli list

# # For Raspberry Pi
# faas-cli store list \
#  --platform armhf

# faas-cli store deploy figlet \
#  --platform armhf

# # Find out more at:
# # https://github.com/openfaas/faas

## I ran the suggested commands (but I have no idea what they do)

kubectl rollout status -n openfaas deploy/gateway
kubectl port-forward -n openfaas svc/gateway 8080:8080 & 

## This is for metrics
kubectl port-forward -n openfaas svc/prometheus 9090:9090 & 
PASSWORD=$(kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode; echo)
echo -n $PASSWORD | faas-cli login --username admin --password-stdin

## Finally deploy our function :')
faas-cli deploy -f ./hello-python3.yml

## Actually deploy using this (given that the image exists)
# faas-cli deploy --image hello-python --name hello-python

## Do we always need this before?
faas-cli remove hello-python3


## This is supposed to show whether deployment suceeded:
kubectl get deploy -n openfaas

## The function didn't start, and so I am debugging through this:
## https://docs.openfaas.com/deployment/troubleshooting/#my-function-didnt-start

## The following shows 0/1
kubectl get deploy -n openfaas-fn

## I think the issue has to do with the hello-python being local

## I managed to deploy figlet by using 
faas-cli store deploy figlet

## and then calling it with 
curl http://127.0.0.1:8080/function/figlet -d "popo"


## After the updaes:
curl 127.0.0.1:8080/function/hello-python3 --data-binary '{
 "url": "https://www.kubernetes.io/",
 "term": "docker"
}'
```