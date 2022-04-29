#!/bin/bash

bash setup1.sh
prev=$PWD

sudo su - ${USER}
cd prev

bash setup2.sh
