
##
## Has to run everytime the machine is stopped and restarted
##

# build cluster
minikube start --cpus=12 --memory=20g
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.0.0/serving-crds.yaml
kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.0.0/serving-core.yaml
kubectl apply -f https://github.com/knative/net-kourier/releases/download/knative-v1.0.0/kourier.yaml
kubectl patch configmap/config-network \
  --namespace knative-serving \
  --type merge \
  --patch '{"data":{"ingress.class":"kourier.ingress.networking.knative.dev"}}'
sleep 1
## Call with -c to cleanup old tunnels
minikube tunnel -c > /dev/null &

# wait until the cluster is up

echo "Waiting for cluster to be running..."
while [ "$(kubectl get pods -n knative-serving | grep "Running" | wc -l)" -lt 7 ]
do
    echo -n "."
    sleep 2
done
echo " DONE"
