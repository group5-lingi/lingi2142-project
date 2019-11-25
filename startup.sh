#!/bin/bash
sudo ip -6 addr add fde4::5:beef/64 dev eth1
sudo ip link set eth1 up
sudo ip -6 addr add fde4:5:3000:1::/64 dev eth2
sudo ip link set eth2 up
sudo ip -6 addr add fde4::5:beff/64 dev eth3
sudo ip link set eth3 up
sudo ip -6 addr add fde4:4:f001:5::/64 dev eth4
sudo ip link set eth4 up

