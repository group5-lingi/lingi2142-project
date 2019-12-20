!
! OSPF configuration for ${data['name']}
!
log stdout
service advanced-vty
!
debug ospf6 neighbor state
!
%for interface in data['interfaces']:
%if interface['type'] == "e":
interface ${interface['name']}
%else:
interface ${interface['name']}
%endif
    ipv6 ospf6 cost ${interface['cost']}
    %if interface['type'] == 'i':
    ipv6 ospf6 hello-interval ${interface['hello_time']}
    ipv6 ospf6 dead-interval ${interface['dead_time']}

! This line works with CISCO-routers and with FRRouting once ospf6 passwords are implemented
!   ipv6 ospf6 message-digest-key 1 md5 testPassword

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
    ipv6 ospf6 message-digest-key 1 md5 testPassword
!
router ospf6
    ospf6 router-id ${data['router_id']}
    %for nic in [ d for d in data['interfaces'] if d['type'] != "e"]:
    interface ${nic['name']} area ${nic['area']}
    %endfor
    interface lo area 0.0.0.0
    ipv6 ospf6 authentication message-digest
!

