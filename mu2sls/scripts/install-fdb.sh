#!/bin/bash

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
pip3 install foundationdb