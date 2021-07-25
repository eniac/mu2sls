# OpenFaaS Playground

A playground and repository that contains all my experiments using OpenFaaS and description of the compilation project.

## Table of contents
1.  [Setup and Instructions](#setup-instructions)
2.  [TextService Experiment](#textservice-experiment)
3.  [Complete TextService Experiment](#textservice-experiment-complete)
4.  [Backend Service Experiment](#backend-service-experiment)
5.  [TODO Items](#todo-items)
6.  [Compilation Sketch](#compilation-sketch)
7.  [Related Work](#related-work)
8.  [Potential Benchmarks](#benchmarks)
8.  [Ideas](#ideas)
9.  [Troubleshooting](#troubleshooting)
10. [Miscellaneous Experiment Code](#misc-experiment-code)


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


## TODO Items <a name="todo-items"></a>

* Figure out what correctness means for a persistent serverless implementation. This means sketch the spec of the translation; what is it trying to achieve. Then we can decide what to do with each call and invocation, and response.

* Figure out the difficulties of stateful microservices and figure out if we can lift their implementation to be transparent persistence usage.

* Investigate services that would require non-persistent state. Authentication service (session variable), service that gets paginated results and has next pointer.

* Think about an optimization that keeps beldi transaction calls lazy and fuses transactions that are next to each other.

* TODO: The HTTP transport also needs to be modified so that it can understand the error messages that OpenFaaS returns.

* TODO: Check performance improvements by using python3-flask or python3-http template for serverless.

* TODO: Write Frontend tests

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

For the rest of the objects we need to go through Beldi, simply by passing all of their accesses to Beldi.

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
- Cross service transactions (normally this is very difficult)

### Dataflow Analysis

__TODO:__ We need to decide whether we want to perform some form of dataflow analysis on the code, or whether we want to avoid it. This is not straightforward to answer. Dataflow analyses can be complex and imprecise in dynamic languages like Python. 

### Transactions that involve requests too

Cross service transactions cannot normally be done. If we include all services and their thrift code through Beldi though they might be able to be done.

__TODO:__ Investigate

## Handling data objects (object fields)

Our compiler takes a service handler that has data fields, and then it transforms this object to an object where the accesses to these fields can happen safely in a serverless setting.

 - For the static objects (like the thrift client) the only thing that needs to be done is to initialize them so there are no issues.

 - However, for the persistent objects we start having correctness issues. 
   + First of all, there is concurrency, where we lose atomicity over accesses. This is bad for primitives, e.g., incrementing a counter, but even worse for collections, where method calls perform the updates. One way to address that would be to ask from the user to add begin/end tx in their code, and delegate finding these begin/end  to other frameworks and techniques, such as Blazes. I think we can expect users to add begin/end tx/atomic when they need atomicity. 
   + Even if we address this, then we need to somehow make this efficient, since we cannot access Beldi everytime we need to load.
  
__IDEA:__ Actually, if persistent objects are only accessed through methods (and not primitive actions), then we can actually wrap all of their methods with transactions (so that at least each operation is atomic) and checks to ensure that after each operation is done, if there was an update to the object, then it is immediately propagated to Beldi.

__Proposal:__ All method calls to persistent objects are expected to be linearizable. If the user needs more guarantees, then they can add locks/transactions/critical sections around the code where they need more. Primitive operations are expected to be atomic. (an increment is not atomic since it requires get+set). The user can bypass standard linearizability in objects by implementing their own methods with critical sections so that things work. 

Also, storing collections in Beldi might require rethinking of its mechanisms to be efficient. We don't want to serialize a whole object and deserialize it.

__TODO:__ How can we start measuring implementation of lists on Beldi and whether it is efficient.

__Point:__ I think that we can avoid thinking about adding transactions for now, and let the users have to deal with it. There is work on that, and it has nothing to do with us. If you have an object that you want to access in a concurrent way, then you need to add locks in your code.

### Wrapping objects 

Wrapping an object requires wrapping all its fields and methods (attributes). 

__Method-only access objects:__ If an object is only accessed through methods, then it is very simple to wrap it. It is as if we had an RPC proxy item. Simply find all its methods (using `dir`, `getattr`, and the `callable` check) and rewrite all of them with methods that instead first do something else, then do the method, and then do something else. 

__Field access objects:__ Objects that have accesses through fields are not that straightforward. What is the correct way to rewrite an object's field accesses? We can wrap the whole object in a wrapper object that overrides its getattr and setattr methods to get them from beldi. However, if the attribute is callable, then we need to make sure that we wrap it using a beldi transaction too, since we have only gotten the method of the function.

Q: Is that correct? Or do we need to delay a call to a method and get the method again when the time comes?
A: This is how I do it now.

If we solve wrapping, then there are correctness questions that are involved. If an object is only accessed through methods, then it is very simple to ensure that each method is atomic. If an object is accessed through its fields, then it is quite likely that the user needs to add beldi transactions in their code (or we add it by default around each request). Otherwise, a set after a get will not happen atomically, and therefore all concurrency issues might happen.

### Laziness and Dynamic Optimization

Is it possible to use laziness to somehow dynamically optimize calls to Beldi and object accesses while the code runs? Essentially instead of performing calls, return unevaluated objects and only when needing the value performing requests. This might help since it might allow for batching requests, or not reading writing of the same value, etc.

This is an interesting possibility, and could make a lot of sense. To achieve this, it requires a program representation where effects are separated from simple computation, and therefore we can perform optimizations on the objects.

An interesting optimizations is performing only the last of two subsequent sets.

__NOTE:__ This is even more relevant when there are consecutive method invocations, and by default we would have to do cascading gets and cascading sets before and after each method invocation. Actually this is wrong, since wrapping is only done on a surface level.

__Question:__ Do we actually need to wrap deeper than just the surface level? Probably not, as long as we wrap the external layer we are good.

### Overriding special methods

Special methods, such as `__len__` or `__add__` cannot be overriden and they have to be defined in the class object. If we have the source code of the definition of a class, we might be able to do something about this, using the compiler to create a new class (or a subclass) that rewrites these methods to go through beldi. However, that is certainly not straightforward.

__IDEA:__ Actually, we might be able to simply conservatively, add all special methods to the wrapped object and send them through a special method function that checks if the underlying object has it, and calls it instead. Since there is a finite number of special methods we can do that. It works for `__add__`.

### Setting an object

Setting an object is kinda important. Especially for primitives. In order to do that, we need to wrap sets to the wrapped object.

__TODO:__ Investigate whether descriptors can help with this. Fix sets to an object using descriptors.



__Alternatives:__

1. Either implement special versions of classes such as integers and lists, overriding all the special methods that they support.

2. Otherwise (or in addition), if we have the source code of special method definitions, we can print it out modified in the modified code, so that even the special methods go through the classes.

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

- [Diamond](https://www.usenix.org/conference/osdi16/technical-sessions/presentation/zhang-irene): A framework that offers ACID guarantees and reactive updates for application state in a WAN setting. The particularity of the setting is reactivity and the wide area, which requires combining the storage with the reactive framework to ensure consistency.
  + __Key take away:__ System has to be data-aware to be able to provide consistency. In their setting too the developer has to annotate the important fields.
  + __Note:__ Interposition is simple and not a technical challenge. Therefore, our work needs to focus on something technical!

- [Durable Functions]() __TODO__

- [Ambrosia]() __TODO__

- [Orleans]() __TODO__

## Potential Benchmarks <a name="benchmarks"></a>

This section contains pointers to potential benchmarks/applications/workloads that we might want to use:

- [DeathstarBench](https://github.com/delimitrou/DeathStarBench) A benchmark of microservice applications that are mostly stateless (except for the backends) and contain a lot of small microservices that comprise a big graph.
  + This application sets contains the biggest graphs of services showcasing some important properties.
  + They are all written in a very similar style (which might be bad for the generality of our approaches).
  + They are mostly easy to run and the code is easy to read.

- [μSuite](https://akshithasriraman.eecs.umich.edu/publication/iiswc/) An OLDI (whatever that means) microservice benchmark suite that contains 4 applications that all follow a two level pattern: a mid-tier service that fans out requests to leafs and then aggregates their responses to make a response.
  + (+) These applications are good candidates (if I understand correctly the mid-tier service also has state) and are different than the DeathstarBench ones
  + (-) The implementations look very hacky and would require reimplementation probably
  + (-) All the applications follow a simple 2-layer pattern

- Potential Alternatives
  + RPC applications and benchmarks (maybe look at the RPC HotOS 2021 papers?)
  + Vincent proposed to look for authentication services (they create sessions, i.e., non-persistent state) or services that return pages of results (and therefore give you a pointer to fetch the rest of the results with every query).
  + Sock Shop
  + Ignis Benchmarks

## Ideas <a name="ideas"></a>

* Compiler could also be helpful for testing, in principle it should decouple the platform specific details and it should abstract over calls to other services, therefore allowing for modular testing.

* Lazy importing of code for latency critical applications that are short lived.

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
