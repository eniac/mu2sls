#!/bin/bash

vsn="6.3.23"
wget "https://github.com/apple/foundationdb/releases/download/${vsn}/foundationdb-clients_${vsn}-1_amd64.deb"
sudo dpkg -i "foundationdb-clients_${vsn}-1_amd64.deb"
rm "foundationdb-clients_${vsn}-1_amd64.deb"
