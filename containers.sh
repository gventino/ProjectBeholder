#!/bin/bash

# virtual docker network that simulates physical devices
sudo docker network create -d macvlan \
  --subnet=192.168.1.0/24 \
  --gateway=192.168.1.1 \
  -o parent=enp7s0 \
  homelab

# benign services
sudo docker run -d \
  --network homelab \
  --ip 192.168.1.10 \
  --name web-server \
  nginx

sudo docker run -d \
  --network homelab \
  --ip 192.168.1.11 \
  --name db-tcc \
  -e MYSQL_ROOT_PASSWORD=root \
  mysql:8.0

sudo docker run -d \
  --network homelab \
  --ip 192.168.1.12 \
  --name ftp-server \
  stilliard/pure-ftpd
