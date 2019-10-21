#! /bin/sh
ldconfig
%for interface in data['interfaces']:

# Assigning IP addr for ${interface['name']}
ip link set dev ${interface['name']} up
ip -6 addr add ${interface['ip']} dev ${interface['name']}
%endfor

# zebra is required to make the link between all FRRouting daemons
# and the linux kernel routing table
LD_LIBRARY_PATH=/usr/local/lib /usr/lib/frr/zebra -A 127.0.0.1 -f /etc/zebra.conf -z /tmp/${data['name'].lower()}.api -i /tmp/${data['name'].lower()}_zebra.pid &

# launching FRRouting OSPF daemon
LD_LIBRARY_PATH=/usr/local/lib /usr/lib/frr/ospf6d -f /etc/${data['name'].lower()}_ospf.conf -z /tmp/${data['name'].lower()}.api -i /tmp/${data['name'].lower()}_ospf6d.pid -A 127.0.0.1


