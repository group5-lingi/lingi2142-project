log stdout
debug bgp zebra
debug bgp neighbor-events
!
router bgp ${data["as_num"]}
  bgp router-id ${data["routerbgp_id"]}
  no bgp default ipv4-unicast
!
!	eBGP
!
  %for neighbor in data["ebgp_neighbors"]:
  neighbor ${neighbor["ip"].split("/")[0]} remote-as ${neighbor["as_num"]}
  address-family ipv6 unicast
    network fde4:5::/32
    neighbor ${neighbor["ip"].split("/")[0]} activate
    neighbor ${neighbor["ip"].split("/")[0]} route-map set-nexthop in
    %if neighbor["ip"] == "fde4::1:dead":
    neighbor fde4::1:dead password ASes6500165005
    %endif
  exit-address-family

  %endfor



!
!	iBGP
!
  bgp route-reflector allow-outbound-policy
  %for neighbor in data["ibgp_neighbors"]:
  !
  neighbor ${neighbor["ip"]} remote-as ${neighbor["as_num"]}
  address-family ipv6 unicast
    neighbor ${neighbor["ip"]} activate
  %if "RR" in data["type"]:
    neighbor ${neighbor["ip"]} route-reflector-client
  %endif
    neighbor ${neighbor["ip"]} update-source lo
  exit-address-family

  %endfor  
  !

  
  route-map set-nexthop permit 10
   set ipv6 next-hop global ${data["lo_ip"].split("/")[0]}
   set ipv6 next-hop prefer global   

 
!
