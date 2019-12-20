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
ip6tables -A INPUT -p tcp --dport 179 -i styx -s fde4::1 -j ACCEPT
ip6tables -A OUTPUT -p tcp --dport 179 -o styx -d fde4::1 -j ACCEPT
ip6tables -A INPUT -p tcp --dport 179 -i P1-BR-eth9 -s fde4:5:1100::0071 -j ACCEPT
ip6tables -A OUTPUT -p tcp --dport 179 -o P1-BR-eth9 -d fde4:5:1100::0071 -j ACCEPT

# Allow BGP inside our network
ip6tables -A INPUT -p tcp --dport 179 -s fde4:5:1000::/36,fde4:5:2000::/36 -j ACCEPT
ip6tables -A OUTPUT -p tcp --dport 179 -d fde4:5:1000::/36,fde4:5:2000::/36 -j ACCEPT
ip6tables -A FORWARD -p tcp --dport 179 -s fde4:5:1000::/36,fde4:5:2000::/36 -d fde4:5:1000::/36,fde4:5:2000::/36 -j ACCEPT

# Allow ICMPv6
ip6tables -A INPUT -p ipv6-icmp -j ACCEPT
ip6tables -A FORWARD -p ipv6-icmp -j ACCEPT
ip6tables -A OUTPUT -p ipv6-icmp -j ACCEPT


# Allow OSPF inside our network
ip6tables -A INPUT -p 89 -i P1-BR-eth0 -j ACCEPT
ip6tables -A OUTPUT -p 89 -o P1-BR-eth0 -j ACCEPT
ip6tables -A INPUT -p 89 -i P1-BR-eth1 -j ACCEPT
ip6tables -A OUTPUT -p 89 -o P1-BR-eth1 -j ACCEPT
ip6tables -A INPUT -p 89 -i P1-BR-eth2 -j ACCEPT
ip6tables -A OUTPUT -p 89 -o P1-BR-eth2 -j ACCEPT
ip6tables -A INPUT -p 89 -i P1-BR-eth3 -j ACCEPT
ip6tables -A OUTPUT -p 89 -o P1-BR-eth3 -j ACCEPT
ip6tables -A INPUT -p 89 -i P1-BR-eth4 -j ACCEPT
ip6tables -A OUTPUT -p 89 -o P1-BR-eth4 -j ACCEPT
ip6tables -A INPUT -p 89 -i P1-BR-eth5 -j ACCEPT
ip6tables -A OUTPUT -p 89 -o P1-BR-eth5 -j ACCEPT
ip6tables -A INPUT -p 89 -i P1-BR-eth6 -j ACCEPT
ip6tables -A OUTPUT -p 89 -o P1-BR-eth6 -j ACCEPT
ip6tables -A INPUT -p 89 -i P1-BR-eth7 -j ACCEPT
ip6tables -A OUTPUT -p 89 -o P1-BR-eth7 -j ACCEPT
ip6tables -A INPUT -p 89 -i P1-BR-eth8 -j ACCEPT
ip6tables -A OUTPUT -p 89 -o P1-BR-eth8 -j ACCEPT


# Block spoofing attempts / Only allow from the assigned subnet
ip6tables -A INPUT -i ZCUST1--BR-eth0 ! -s fde4:5:4000::/48 -j DROP
ip6tables -A OUTPUT -o ZCUST1--BR-eth0 ! -d fde4:5:4000::/48 -j DROP
ip6tables -A FORWARD -i ZCUST1--BR-eth0 ! -s fde4:5:4000::/48 -j DROP
ip6tables -A FORWARD -o ZCUST1--BR-eth0 ! -d fde4:5:4000::/48 -j DROP

# Allow stuff that goes through our network
ip6tables -A FORWARD ! -s fde4:5:1000::/36 ! -d fde4:5:1000::/36 -j ACCEPT
ip6tables -A FORWARD ! -s fde4:5:1000::/36 ! -d fde4:5:2000::/36 -j ACCEPT
ip6tables -A FORWARD ! -s fde4:5:2000::/36 ! -d fde4:5:1000::/36 -j ACCEPT
ip6tables -A FORWARD ! -s fde4:5:2000::/36 ! -d fde4:5:2000::/36 -j ACCEPT


