!
! OSPF configuration for ${data['name']}
!
log stdout
service advanced-vty
!
debug ospf6 neighbor state
!
%for interface in data['interfaces']:
interface ${interface['name']}
    ipv6 ospf6 cost ${interface['cost']}
    %if interface['active']:
    ipv6 ospf6 hello-interval ${interface['hello_time']}
    ipv6 ospf6 dead-interval ${interface['dead_time']}
    %else:
    ipv6 ospf6 passive
    %endif
    ipv6 ospf6 instance-id ${interface['instance_id']}
!
%endfor
interface lo
    ipv6 ospf6 cost 5
    ipv6 ospf6 hello-interval 40
    ipv6 ospf6 dead-interval 40
    ipv6 ospf6 instance-id 0
!
router ospf6
    ospf6 router-id ${data['router_id']}
    %for nic in data['interfaces']:
    interface ${nic['name']} area ${nic['area']}
    %endfor
    interface lo area 0.0.0.0
!

