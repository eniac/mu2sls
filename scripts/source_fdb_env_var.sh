
## Sourced script

## This script sets up an environment variable (after all installation is done)
##
## The FDB_CLUSTER_DATA which contains the cluster info to start fdb clients
##

export FDB_CLUSTER_FILE=/etc/foundationdb/fdb.cluster

export FDB_CLUSTER_DATA="$(cat ${FDB_CLUSTER_FILE})"