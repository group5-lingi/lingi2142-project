#!/usr/bin/bash
sudo ip -6 addr add fde4::5:beef/64 dev eth1
sudo ip link set eth1 up
sudo ip -6 addr add fde4::5:befe/64 dev eth2
sudo ip link set eth2 up
