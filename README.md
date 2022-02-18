# Microservices 2 Serverless

A repository that contains experiments on a compiler that implements microservice applications on serverless platforms. The compiler is in the `mu2sls` directory and the directory `openfaas` contains old experiments on the openfaas serverless platform.

## Table of contents
1.  [Setup and Instructions](#setup-instructions)
5.  [TODO Items](#todo-items)
6.  [Compilation Sketch](#compilation-sketch)
7.  [Related Work](#related-work)
8.  [Potential Benchmarks](#benchmarks)
8.  [Ideas](#ideas)
9.  [Troubleshooting](#troubleshooting)

## Setup and Instructions <a name="setup-instructions"></a>

TODO

## TODO Items <a name="todo-items"></a>

* Figure out the difficulties of stateful microservices and figure out if we can lift their implementation to be transparent persistence usage.

* Investigate services that would require non-persistent state. Authentication service (session variable), service that gets paginated results and has next pointer.

* Think about an optimization that keeps beldi transaction calls lazy and fuses transactions that are next to each other.

* TODO: The HTTP transport also needs to be modified so that it can understand the error messages that OpenFaaS returns.

* TODO: For performance measurements, I need to make a timing function with python decorators to time different parts of the process, such as my transport layers, etc.

* TODO: Package all python helper code (thrift, general helpers) in one or more libraries. These can all be in the same repo for now (different directories).

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

__Done:__ using descriptors. 



__Alternatives:__

1. Either implement special versions of classes such as integers and lists, overriding all the special methods that they support.

2. Otherwise (or in addition), if we have the source code of special method definitions, we can print it out modified in the modified code, so that even the special methods go through the classes.

## Related Work <a name="related-work"></a>

This section first contains a discussion of the serverless domain particularities, as well as pointers and references to related papers and software so that we don't forget it:

### Particularities of serverless

Here we briefly enumerate the particular characteristics that make the serverless domain different than standard traditional distributed systems.

1. In the serverless domain there is no relation between the host and the function invocation, namely the user does not have any control over the host that the invocation is executed. This disallows the development of protocols such as consensus since there is a requirement to know the hosts.
2. Serverless function invocations are particularly volatile and they are only guaranteed to execute at-least-once, possibly failing in the middle. This requires stronger than usual state backends since they need to be "idempotent" (whatever that means). Usual distributed systems need to be fault-tolerant (the backend needs to not return trash when one of its nodes fails) but it doesn't need to take care about the faults of the client code.
3. Serverless scales faster and to higher levels (e.g., lambda up to 1000 concurrent invocations), which means that contention becomes a serious issue.
4. Serverless functions usually execute with a time limit. Systems like Kappa and gg try to tackle that.

### Related Papers

- [Boki](NOT YET OUT): A serverless runtime that exports a shared log to functions. 
  + This log can be used to get durability, fault-tolerance for the application state without sacrificing performance. Durable objects and workflows can be implemented on top of it.
  + __Difference__ This paper focuses on providing a low level efficient primitive to applications, and not on a high-level interface for writing serverless programs. Users still have to implement their application using the Boki libraries. 
  + __Q:__ How does this differ from Badrish's work and FASTER?
  + __Q:__ Can all data structures with strong guarantees be implemented on top of a log?
  + __Possible Backend__ -- Especially since it builds on top of Nightcore. 

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