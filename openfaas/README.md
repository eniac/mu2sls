# OpenFaaS Playground

A playground that contains experiments using OpenFaaS.

## Table of contents
1.  [Setup and Instructions](#setup-instructions)
2.  [TextService Experiment](#textservice-experiment)
3.  [Complete TextService Experiment](#textservice-experiment-complete)
4.  [Backend Service Experiment](#backend-service-experiment)
5.  [Troubleshooting](#troubleshooting)
6.  [Miscellaneous Experiment Code](#misc-experiment-code)


## Setup and Instructions <a name="setup-instructions"></a>

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

## TextService Experiment <a name="textservice-experiment"></a>

We now need to interface the serverless function with the rest of the social network.

The first requirement for this is to have adequate code in the function container (Thrift generated code etc).

An additional big requirement is to modify the Thrift Client to make requests that are understood by the serverless function. Maybe the HTTPClient can do the trick?

To build, push, and deploy:
```sh
faas-cli up -f compose-post.yml
```

> Note: The service is actually text service but I initially intended for it to be compose post and so naming might be inconsistent at some places.

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

### Interfacing with the rest of the microservices application (on the receiving end)

We need to make sure that the microservices all run and then that OpenFaaS is running, and then that the openfaas port is forwarded in the host (but not in 8080, but rather in 8090).

Note that since we forward the gateway port in the host, we need to make sure that the HttpClient in the mciroservice connects to the host.

> WARNING: There is a bug with buffered transport, I am not sure what exactly it is, but it leads to parsing of responses failing due to a \n in the middle of requests.

### Experiment with colocation

An important thing that we need to understand is how colocated are different serverless invocations, i.e., do they share VM or runtime.

Therefore I did an experiment to observe that for OpenFaaS (since I couldn't find it in the documentation).

It seems that its invocation is a different process (therefore having a different python runtime) meaning that different invocations do not share runtime specific values like globals.

However, it seems that different processes run on the same VM. I observed that by writing a script that writes the pid of the process in a file with the same name in the `/tmp` directory, and then printed the directory contents, and I found that as execution progresses, more and more pid files are stored in that common `/tmp` directory.

## Completing the serverless version Text Service <a name="textservice-experiment-complete"></a>

We are now ready to complete the implementation of the text service, making clients to call further backend microservices as well.

This is not particularly difficult. The standard Thrift clients are used. An issue that needs to be investigated is whether reinitializing the clients incurs significant cost.

__TODO:__ Investigate the cost of reinitializations of all clients and connection objects.

The main difference was that hosts and ports are not visible from within the microservice docker container group to the host. Therefore the Kubernetes containers that are spanwed to execute functions do not have access to the services.

__Solution:__ I addressed this by exposing the ports to the host in the `docker-compose.yml` file in the Social Network application as shown here for `user-mention-service`:

```yaml
user-mention-service:
    ...
    ports:
      - 10009:9090
```

Then we can use the following hostname and port in the serverless function definition to access the `user-mention-service`:

```py
user_mention_service_client = SetupClient(UserMentionService, "host.k3d.internal", 10009)
```

The hostname `host.k3d.internal` is provided by `k3d` and points to the host. The port is the exposed one in the `docker-compose.yml`.

__TODO:__ Add async calls in the text service serverless implementation.

### Complete (but unstable) testing experiment

To run a whole end-to-end experiment (that is not stable at all as it depends on the specific commit of the deathstar beanch too) run `compose-post/test.sh`. It mostly serves for documentation and an exploration checkpoint.

## Backend Service Experiment <a name="backend-service-experiment"></a>

We are now ready to reimplement a backend service in serverless, and figure out how to manage its state. This will probably uncover several issues.

The UrlShortenService looks like a good candidate. It contains a lock, accesses to memcached, and accesses to MongoDB. The experiment is broken up in the following steps:
- Experiment with `asyncio`, which is the defacto async python library. We might need to go back to the previous experiment and reimplement it using asyncio first to make that simpler.
- Figure out how to interface python with a MongoDB client. Then implement the service as if it has no cache.
- Figure out how to interface with memcached, then implement the service with a cache. Then we can think whether cache can also be automated (instead of having to be intertwined with application logic).

__Note:__ Maybe the jaeger address also has to change in serverless

### Experimenting with `asyncio` in TextService

Since the serverless function processes a single request, we only need concurrency in the handler, and therefore we can simply wrap the handler in `asyncio.run`. Then the handler can use `asyncio.gather` to wait on concurrent tasks.

If we actually need concurrency on the processing too, then we might need some form of asyncio wrapping all around Thrift (to allow for concurrency across different requests that are `serve`d).

### Preparation

As before, make a new directory and then use `faas-cli new url-shorten-service --lang python3` to initialize a handler. Then modify the `handler.py`, `requirements.txt`, and the `.yml` file to have a running copy.

### Python MongoDB bindings

We can use [pymongo](https://pymongo.readthedocs.io/en/stable/tutorial.html) and [motor](https://motor.readthedocs.io/en/stable/) for asynchronous. I think that pymongo should be enough to start.

Interfacing with MongoDB is actually very simple, we get a client (the client has a pool by default) and then get a database, a collection, and then we perform the operations that we need.

### Interface two serverless services together

We are now ready to interface TextService with UrlShortenService (they are both implemented in serverless).

In order to invoke a function through another function we need to get the OpenFaaS gateway hostname, and if we use k3d (or other kubernetes) this is `gateway.openfaas`. For reference, this is explained [here](https://github.com/openfaas/workshop/blob/master/lab1b.md).



## Troubleshooting <a name="troubleshooting"></a>

This section includes unexpected issues that and how they can be addressed

### `kubectl` not found

That sometimes happens on my WSL Ubuntu distribution and the way to solve this is to restart Docker. It seems that `kubectl` requires docker to be running properly for it to work.

### Gateway hostname issues

There are two common issues with the gateway and accessing it. When accessing it from the host machine, we need to make sure that its port is forwarded to a localhost port, otherwise it is not accessible. I usually use 8090 as the port since the microservice benchmark uses 8080 for its own purposes. The port can be forwarded as follows:

```sh
kubectl port-forward -n openfaas svc/gateway 8090:8080 & 
```

The second issue is when accessing the gateway through a serverless function (to be able to invoke another function). In the OpenFaaS tutorials the gateway hostname is said to be accessible through `gateway`, but if you use kubernetes to deploy OpenFaaS then the gateway hostname is actually `gateway.openfaas`. See [this tutorial](https://github.com/openfaas/workshop/blob/master/lab1b.md) for more.


## Misc Experimental and exploratory scripting to make the openfaas experiment work <a name="misc-experiment-code"></a>

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