#!/bin/bash

mode=${1?type of remote machine (aws/cloudlab)}
ip=${2?IP of remote machine not given}
user=${3?user in remote machine}

## Optionally the caller can give us a private key for the ssh
key=$4
if [ -z "$key" ]; then
    key_flag=""
else
    key_flag="-i ${key}"
fi

export mu2sls_dir=${MU2SLS_TOP:-$(git rev-parse --show-toplevel --show-superproject-working-tree)/mu2sls}

## Upload the whole knproto directory to a remote machine
if [ "${mode}" = "cloudlab" ]; then
    rsync --rsh="ssh -p 22 ${key_flag}" --progress -p -r "${mu2sls_dir}/scripts/knative" "${user}@${ip}:/users/${user}"
    rsync --rsh="ssh -p 22 ${key_flag}" --progress -p -r "${mu2sls_dir}/runtime" "${mu2sls_dir}/scripts" "${user}@${ip}:/users/${user}/knproto"
    rsync --rsh="ssh -p 22 ${key_flag}" --progress -p "${mu2sls_dir}"/tests/* "${user}@${ip}:/users/${user}/knproto"
else
    rsync --rsh="ssh -p 22 ${key_flag}" --progress -p -r ../knproto "${user}@${ip}:/home/${user}"
fi


