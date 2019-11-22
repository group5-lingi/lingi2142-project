#!/bin/bash

# fde4:5:1000::/36,fde4:5:2000::/36 is the range for IP's of our internal routers

# Flush old rules, so new rules don't interfere
ip6tables -F INPUT
ip6tables -F OUTPUT
ip6tables -F FORWARD
ip6tables -F

# Set the default policy to DROP
ip6tables -P INPUT DROP
ip6tables -P OUTPUT DROP
ip6tables -P FORWARD DROP

# Allow established/related
ip6tables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
ip6tables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
ip6tables -A FORWARD -m state --state ESTABLISHED,RELATED -j ACCEPT

ip6tables -A INPUT -i lo -j ACCEPT
ip6tables -A OUTPUT -o lo -j ACCEPT

# Allow BGP sessions to ebgp neighbors
%for neighbor in data["ebgp_neighbors"]:
ip6tables -A INPUT -p tcp --dport 179 -i ${neighbor["interface"]["name"]} -s ${neighbor["ip"]} -j ACCEPT
ip6tables -A OUTPUT -p tcp --dport 179 -o ${neighbor["interface"]["name"]} -d ${neighbor["ip"]} -j ACCEPT
%endfor

# Allow BGP inside our network
ip6tables -A INPUT -p tcp --dport 179 -s fde4:5:1000::/36,fde4:5:2000::/36 -j ACCEPT
ip6tables -A OUTPUT -p tcp --dport 179 -d fde4:5:1000::/36,fde4:5:2000::/36 -j ACCEPT
ip6tables -A FORWARD -p tcp --dport 179 -s fde4:5:1000::/36,fde4:5:2000::/36 -d fde4:5:1000::/36,fde4:5:2000::/36 -j ACCEPT

# Allow ICMPv6
ip6tables -A INPUT -p ipv6-icmp -j ACCEPT
ip6tables -A FORWARD -p ipv6-icmp -j ACCEPT
ip6tables -A OUTPUT -p ipv6-icmp -j ACCEPT

# Block traffic to our routers (maybe except some subnet)

# Allow OSPF inside our network
%for interface in data["interfaces"]:
%if interface["type"] == "i":
ip6tables -A INPUT -p 89 -i ${interface["name"]} -j ACCEPT
ip6tables -A OUTPUT -p 89 -o ${interface["name"]} -j ACCEPT
%endif
%endfor

# Allow ICMPv6 inside our network

# Block spoofing attempts / Only allow from the assigned subnet

# Allow stuff that goes through our network
ip6tables -A FORWARD ! -s fde4:5:1000::/36 ! -d fde4:5:1000::/36 -j ACCEPT
ip6tables -A FORWARD ! -s fde4:5:1000::/36 ! -d fde4:5:2000::/36 -j ACCEPT
ip6tables -A FORWARD ! -s fde4:5:2000::/36 ! -d fde4:5:1000::/36 -j ACCEPT
ip6tables -A FORWARD ! -s fde4:5:2000::/36 ! -d fde4:5:2000::/36 -j ACCEPT

