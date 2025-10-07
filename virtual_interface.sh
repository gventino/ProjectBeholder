#!/bin/bash

# virtual interface macvlan-host
sudo ip link add macvlan-host link enp7s0 type macvlan mode bridge

# ip binding
sudo ip addr add 192.168.1.200/24 dev macvlan-host

# set interface up
sudo ip link set macvlan-host up
