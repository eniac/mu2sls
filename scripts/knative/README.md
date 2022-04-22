# knproto

## Setup

on ubuntu 20.04

```bash
./setup1.sh
```

this script change user group, so we need to exit and login again or use

```bash
sudo su - ${USER}
```

then run

```bash
./setup2.sh
```

> Note that sometimes `setup2.sh` might not succeed in installing foundationdb, because they keep changing the URL from which to access it. If that is the case, simply change the url in `setup2.sh` to the correct version and then rerun setup2.sh.

Then run the following to start the cluster

```bash
./start-cluster.sh
```

After running these scripts, the cluster should be ready.

```bash
kubectl get pods -n knative-serving
```

You should see something similar to this:

```
NAME                                      READY   STATUS    RESTARTS   AGE
3scale-kourier-control-54cc54cc58-mmdgq   1/1     Running   0          81s
activator-67656dcbbb-8mftq                1/1     Running   0          97s
autoscaler-df6856b64-5h4lc                1/1     Running   0          97s
controller-788796f49d-4x6pm               1/1     Running   0          97s
domain-mapping-65f58c79dc-9cw6d           1/1     Running   0          97s
domainmapping-webhook-cc646465c-jnwbz     1/1     Running   0          97s
webhook-859796bc7-8n5g2                   1/1     Running   0          96s
```

run

```bash
kubectl --namespace kourier-system get service kourier
```

You should see the ip of the load balancer in **EXTERNAL IP**:

```
kourier   LoadBalancer   10.106.145.38   10.106.145.38   80:30739/TCP,443:31790/TCP   51s
```

> Note: If you see `<pending>` instead of the two IPs, you might need to rerun `minikube tunnel -c > /dev/null &` since the tunnel might not be working for some reason.

## Run Examples:

### Running media service

At the location of the source code (`openfaas-playground/mu2sls`), run:

```sh
python3 scripts/knative_dev.py ${docker_io_username}
```

This compiles all services, builds docker images for them, and pushes them to docker.io.
Then make sure to use `upload_to_remote.sh` to upload the `knproto` dir to a remote machine where you will run the tests. For example, a usage as follows:

```sh
./upload-to-remote.sh cloudlab ms0817.utah.cloudlab.us ${cloudlab_username} ~/.ssh/XXX_rsa
```

Then at the machine where you have knative installed (the one where you uploaded), run the following:

```sh
source setup_env_vars.sh
python3 test_services.py url-shortener-test.csv knative --docker_io_username ${docker_io_username}
```

The above should deploy all services to knative and run a test.

#### Debugging

To debug the above, run:

```sh
kubectl get pods
```

and get the name of the container `$CONTAINER_NAME` and then type:

```sh
kubectl logs ${CONTAINER_NAME} user-container
```

to get the logs for that contianer

### Build Image
At the root of the project, run
```bash
./build_and_push.sh "${docker_io_username}"
```

### Configure

Configuration happens automatically in deploy (that assumes that FDB is running on the machine where functions are deployed).

### Service

You can easily deploy the callee service by running the following command on the machine that has the fdb:

```bash
bash deploy.sh "${docker_io_username}" callee callee # You need the docker_io_username to pull the image
```

`deploy.sh` also runs the `setup_env_vars.sh` to get the values for two config variables. 

If something went wrong and the server is still retrying the requests, instead of update, delete and then run `deploy.sh` again.

```bash
kn service delete callee
```

You can check the services by running:

```bash
kn service list
```

Example Output:

```
NAME     URL                                 LATEST         AGE   CONDITIONS   READY   REASON
callee   http://callee.default.example.com   callee-00001   87s   3 OK / 3     True    
```

### Invocation

Invoke the service using curl

```bash
curl -H "Host: callee.default.example.com" http://${LOAD_BALANCER_IP}
```

## Debugging the container

source setup_env_vars.sh
docker run -it --env "LOAD_BALANCER_IP=${LOAD_BALANCER_IP}" --env "FDB_CLUSTER_DATA=${FDB_CLUSTER_DATA}" ${docker_io_username}/callee /bin/bash

## FoundationDB Debugging

You can access FoundationDB from the physical machine:

```python
python3
>>> import fdb
>>> fdb.api_version(630)
>>> db = fdb.open()
# or db = fdb.open(./fdb.cluster) if you're using a different machine
>>> db[fdb.tuple.range(("data",))]  # get data
>>> db[fdb.tuple.range(("log",))]  # get log
```
## Warmup
```bash
kn service update callee --scale-min 5 --annotation "autoscaling.knative.dev/target=500"
```