## Running the media service test

Here is the code that I used to run the media-service test (in the `openfaas-playground/mu2sls directory`)

```sh
./tests/compile_and_load.sh tests/media-service-test.csv
```

Then we get a python terminal with the services in `media-service-test.csv` deployed and read to invoke.
An example invocation:

```python
>>> deployed_services[1].upload_user_review(1, 2, 100)
>>> deployed_services[1].upload_user_review(1, 2, 100)
>>> deployed_services[1].read_reviews(1)
[None, None, None]
```
