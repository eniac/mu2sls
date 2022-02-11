#!/bin/bash

## Only works on Ubuntu. Only tested on my local machine Ubuntu 18.04.5 LTS

## Install Foundation DB (server, client, Python API)
export MU2SLS_TOP=${MU2SLS_TOP:-$(git rev-parse --show-toplevel --show-superproject-working-tree)/mu2sls}

"${MU2SLS_TOP}/scripts/install-fdb.sh"