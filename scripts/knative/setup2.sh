#!/bin/bash -x

# kubectl
sudo apt-get install -y apt-transport-https ca-certificates curl
sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl

# minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
rm minikube-linux-amd64

# knative
wget --no-check-certificate --content-disposition https://github.com/knative/client/releases/download/knative-v1.0.0/kn-linux-amd64
mv kn-linux-amd64 kn
chmod +x kn
sudo mv kn /usr/local/bin/

## Note: The URLs change often, so you need to make sure and update them from here:
##       https://apple.github.io/foundationdb/downloads.html

vsn="6.3.23"

# foundationdb
wget "https://github.com/apple/foundationdb/releases/download/${vsn}/foundationdb-clients_${vsn}-1_amd64.deb"
wget "https://github.com/apple/foundationdb/releases/download/${vsn}/foundationdb-server_${vsn}-1_amd64.deb"
sudo dpkg -i "foundationdb-clients_${vsn}-1_amd64.deb" "foundationdb-server_${vsn}-1_amd64.deb"
sudo chmod +x /usr/lib/foundationdb/make_public.py
sudo /usr/lib/foundationdb/make_public.py
cat /etc/foundationdb/fdb.cluster
rm "foundationdb-clients_${vsn}-1_amd64.deb" "foundationdb-server_${vsn}-1_amd64.deb"

# local fdb client
sudo apt install -y python3-pip
pip3 install foundationdb==${vsn}
pip3 install httpx

# wrk2
git clone https://github.com/giltene/wrk2.git
cd wrk2
make -j
sudo apt install -y luarocks
sudo luarocks install  https://raw.githubusercontent.com/tiye/json-lua/main/json-lua-0.1-4.rockspec
sudo luarocks install luasocket
sudo luarocks install uuid
cd ..
