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

# Allow BGP inside our network
ip6tables -A INPUT -p tcp --dport 179 -s fde4:5:1000::/36,fde4:5:2000::/36 -j ACCEPT
ip6tables -A OUTPUT -p tcp --dport 179 -d fde4:5:1000::/36,fde4:5:2000::/36 -j ACCEPT
ip6tables -A FORWARD -p tcp --dport 179 -s fde4:5:1000::/36,fde4:5:2000::/36 -d fde4:5:1000::/36,fde4:5:2000::/36 -j ACCEPT

# Allow ICMPv6
ip6tables -A INPUT -p ipv6-icmp -j ACCEPT
ip6tables -A FORWARD -p ipv6-icmp -j ACCEPT
ip6tables -A OUTPUT -p ipv6-icmp -j ACCEPT


# Allow OSPF inside our network
ip6tables -A INPUT -p 89 -i P10-FB-eth0 -j ACCEPT
ip6tables -A OUTPUT -p 89 -o P10-FB-eth0 -j ACCEPT
ip6tables -A INPUT -p 89 -i P10-FB-eth1 -j ACCEPT
ip6tables -A OUTPUT -p 89 -o P10-FB-eth1 -j ACCEPT


# Block spoofing attempts / Only allow from the assigned subnet

# Allow stuff that goes through our network
ip6tables -A FORWARD ! -s fde4:5:1000::/36 ! -d fde4:5:1000::/36 -j ACCEPT
ip6tables -A FORWARD ! -s fde4:5:1000::/36 ! -d fde4:5:2000::/36 -j ACCEPT
ip6tables -A FORWARD ! -s fde4:5:2000::/36 ! -d fde4:5:1000::/36 -j ACCEPT
ip6tables -A FORWARD ! -s fde4:5:2000::/36 ! -d fde4:5:2000::/36 -j ACCEPT


