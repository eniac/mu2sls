# mu2sls

This is the repository for the `mu2sls` prototype, described in the POPL23 paper titled "Executing Microservice Applications on Serverless, Correctly".

## Running POPL23 paper experiments

See the [POPL23_ARTIFACT_README.md](https://github.com/angelhof/mu2sls/blob/main/POPL23_ARTIFACT_README.md).

## Requirements

The `mu2sls` framework requires `python3.8` and above.

## Deploying an application and running tests

In order to deploy an application on your local machine, you need to use the following script with the `.csv` file as the first argument. For example, for an application that contains a single-stateful service, you can use the `experiments/single-stateful.csv` as follows:

```sh
python3 test_services.py experiments/single-stateful.csv local
```
The test that will be run is defined in the `TEST_FUNC_FROM_FILE` dictionary in file `tests/test_services.py`.


## (Local) Building and pushing application docker images

In order to run an application, you need to first build it on your local machine and push it to an image registry. If you need to do that, update the `$docker_io_username` variable in `vars.sh` to include your `docker_io_username`, alternatively, you can use the prebuilt images.

Example usage of build script:
```sh
## Build and deploy the single-stateful application
python3 scripts/knative_dev.py ${docker_io_username} experiments/single-stateful.csv
```

## Developing an application using mu2sls

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
