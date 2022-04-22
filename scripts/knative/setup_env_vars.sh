
## Sourced script

## This script sets up two important environment variables (after all installation is done)
##
## The LOAD_BALANCER_IP which is the IP of the serverless load balancer
##
## The FDB_CLUSTER_DATA which contains the cluster info to start fdb clients
##

lb_ip_file=/tmp/lb_ip_file

## This is very brittle parsing, and might often fail
## TODO: Improve
kubectl --namespace kourier-system get service kourier -o yaml | 
    grep "clusterIP:" |                 # Find the cluster IP
    cut -d ':' -f 2 |                   # Get the IP
    awk '{$1=$1};1' > "${lb_ip_file}"   # Remove leading and trailing whitespace

export LOAD_BALANCER_IP="$(cat ${lb_ip_file})"

fdb_cluster_file=/etc/foundationdb/fdb.cluster

export FDB_CLUSTER_DATA="$(cat ${fdb_cluster_file})"
