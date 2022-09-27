
__TODO__:
- Is there a way to give the exact Cloudlab configuration setup in a programatic way for them to start the cloudlab instance?
- Should we provide source code on Zenodo or github?
- TODO: Provide a virtual box with all dependencies for both local and remote development.

# Artifact Documentation for "Executing Microservice Applications on Serverless, Correctly"

This document describes the artifact for the POPL 23 paper titled "Executing Microservice Applications on Serverless, Correctly".

It contains 5 sections:
- List of Claims
- Download, installation, and sanity-testing instructions
- Evaluation instructions
- Reusability instructions
- Additional Description


## List of Claims

TODO

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

To run the local tests, simply navigate to the `mu2sls` directory and then execute `./run_tests.sh`.

To run a remote test, you need to follow the following instructions.

#### Installing mu2sls and knative on a Cloudlab machine

TODO:
- Create a cloudlab machine
- copy from README
- run the single-stateful test (it should be OK)


## Evaluation Instructions

TODO

## Reusability Instructions

TODO

## Additional Artifact Information

TODO:
- Explain how different parts in the paper correspond to the code in the artifact