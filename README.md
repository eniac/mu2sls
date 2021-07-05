# OpenFaaS Playground

A playground and repository that contains all my experiments using OpenFaaS and description of the compilation project.

## Table of contents
1. [Setup and Instructions](#setup-instructions)
2. [TextService Experiment](#textservice-experiment)
3. [Complete TextService Experiment](#textservice-experiment-complete)
4. [TODO Items](#todo-items)
5. [Compilation Sketch](#compilation-sketch)
6. [Related Work](#related-work)
7. [Ideas](#ideas)
8. [Miscellaneous Experiment Code](#misc-experiment-code)


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

To run a whole end-to-end experiment (that is not stable at all as it depends on the specific commit of the deathstar beanch too) run `./test.sh`. It mostly serves for documentation and an exploration checkpoint.


## TODO Items <a name="todo-items"></a>

* Figure out the difficulties of stateful microservices and figure out if we can lift their implementation to be transparent persistence usage.

* Investigate Python native asyncio and use that instead of the concurrent futures.

* TODO: The HTTP transport also needs to be modified so that it can understand the error messages that OpenFaaS returns.

* TODO: For performance measurements, I need to make a timing function with python decorators to time different parts of the process, such as my transport layers, etc.

* TODO: Think about how to have proper tests. Jaeger is not enough: it requires manual effort, and also it doesn't work atm.

* TODO: Make sure that all setup for an experiment can be run with a single shell script.

* TODO: Package all python helper code (thrift, general helpers) in one or more libraries. These can all be in the same repo for now (different directories).

* TODO: Investigate why kubectl port-forward stops and how to fix that.

* See if we can somehow leverage the Azure traces workload.

## Compilation Sketch <a name="compilation-sketch"></a>

### Calls to external Services

#### Thrift calls (Exactly-Once)

We could handle calls through Thrift differently than the rest, since we can compile both the caller's and the callee's Thrift to add a layer to ensure idempotence. Essentially, thrift requests will be orchestrated like Beldi calls. This means that the client will perform a Beldi-invoke.

__Note:__ Since Beldi logs invocations using a callback (to ensure that the caller has the result before the calle marks itself as done), we need to ensure that this is possible using the communication that is offered by Thrift.

#### Rest of external services (at-least once)

For the rest fo the calls we should probably assume that they are idempotent, i.e., given the same inputs, the service state will be unaffected, therefore that we can perform them more than once without caring. Even if we interpose on the sender side of the request (through Beldi), it seems that exactly once cannot be guaranteed for external services, since network might fail/nodes might crash and therefore a request might need to be resent even if it has already been processed.


### Data Objects

The data objects that we need to make sure we control accesses to are the global variables and the fields of the Thrift Handler object.

Out of these objects, I have (until now) identified two categories:
 - Objects that are initialized every time (they are runtime local)
 - Objects that are the state of the application and therefore need to be stored using Beldi

For the initialize objects we can identify their initialization procedures either by making a dataflow analysis in the main function, or by asking explicitly for the initialization procedure through an annotation.

Then, in serverless we simply initialize them in the header.

For the rest of the objects we need to go through Beldi, simply by passing all of their accesses to Beldi

### Determinism

To ensure that the function is determinstic, we can ask a user to decorate all nondeterministic calls so that we send them through Beldi too.

### Unique Invocation Identifier

This is probably necessary to add an identifier in all requests that is unique per end-user call so that we can identify double executions etc.

### Double Billing (Potentially big issue)

There is an issue (that we might or might not care about). Naive compilation of each request handling to a serverless function will lead to multi-billing for the same request. More precisely, we will need to pay N times for each request, where N is the call path length. This is because while executing a request, we will make subrequests, waiting for both of them to finish executing. This keeps going until the end of the microservice graph.

This is handled in microservice deployments by using thread pools and I assume that when a call blocks, te thread yields so that we achieve concurrency. To achieve a similar yielding in our case we would have to extend the serverless execution platform with a scheduler and an event loop so that blocking threads do not consume resources.

__Note:__ This issue can potentially be solved by compiling to continuations, so that we can yield and schedule different function invocations across blocking actions.

### Potential Optimizations

- Do not reinitialize init objects everytime
- Do not go through Beldi everytime for all object 
- Sharing the runtime for state (see more in Photon paper)


## Related Work <a name="related-work"></a>

This section contains pointers and references to related papers and software so that we don't forget it:

- [Photons](https://dl.acm.org/doi/10.1145/3419111.3421297): A framework that invokes serverless functions in the same runtime to improve performance and allow for state and data sharing.
  + This is very close to our work and we might need to compare with it. It is not clear if they provide automation with respect to compilation or whether they require the programmers to reimplement their applications.
  + __Difference:__ Their work provides abstractions to developers for sharing state, while we will do that automatically. Also they assume their code is initially already in serverless, and therefore can provide small automation to isolate accesses to globals, but that's it.
  + __Possible Backend__

- [Nightcore](https://dl.acm.org/doi/10.1145/3445814.3446701): An alternative serverless engine that is focused on microservice applications.
  + It might be useful to have that as a backend for our experiments (since it will be significantly more efficient than FaaS).
  + __Possible Backend__

- [Kappa](https://dl.acm.org/doi/10.1145/3419111.3421277): A framework that extends serverless capabilities with checkpoints and messages.
  + Kappa is a programming framework and therefore requires reimplementation of an application. It could be potentially used as a target for our compiler, meaning that our compiler could produce code that can be executed by kappa.
  + They provide a lightweight pass that transforms input __python__ source code to continuation style, allowing them to pause and serialize execution at specific points of execution. They dont have any heuristics for picking the pause points though, and so we could use our compiler to come up with good points for pausing (e.g., blocking points). We can certainly reuse parts of that, or even all of it.
  + __Possible shortcoming:__ Kappa provides a coordinator that ensures exactly once execution of effectul calls. If we implemented microservices naively on top of Kappa, we would end up with huge overhead as all calls (even the stateless ones) will have to go through there, leading to significant, unneccessary overhead.
  + __Possible shortcoming:__ Their checkpointing and serialization seems to be very efficient and scalable (it only depends on the capabilities of the storage solution, where they use Redis) if the functions are independent. However, in a microservice application I would expect that checkpoints would require a Beldi like solution, therefore not being that scalable.
  + __Possible Backend__
  + __TODO:__ Understanding its shortcomings might help if we compare to a naive solution against it.

- [Fault Tolerance Shim](https://dl.acm.org/doi/10.1145/3342195.3387535): A framework that interposes serverless applications to guarantee read atomic isolation, i.e., visibility of partial writes in a transaction.
  + Orthogonal to our work, as this can be used instead of Beldi to provide different undelying guarantees if needed. In theory, our work now should be parametrizable by the underlying transactional store.

- [gg](https://www.usenix.org/system/files/atc19-fouladi.pdf): A compiler/framework that implements pure computational applications on top serverless. 
  + It is only vaguely related as it focuses on a completely different type of applications.


## Ideas <a name="ideas"></a>

* Compiler could also be helpful for testing, in principle it should decouple the platform specific details and it should abstract over calls to other services, therefore allowing for modular testing.

* Lazy importing of code for latency critical applications that are short lived.

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
