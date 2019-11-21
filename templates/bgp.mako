log stdout
debug bgp zebra
debug bgp neighbor-events
!
router bgp ${data["as_num"]}
  bgp router-id ${data["routerbgp_id"]}  
  no bgp default ipv4-unicast
  %for neighbor in data["ebgp_neighbors"]:
  neighbor ${neighbor["ip"]} remote-as ${neighbor["as_num"]}
  neighbor ${neighbor["ip"]} next-hop-self    
  %endfor
  %for neighbor in data["ibgp_neighbors"]:
 neighbor ${neighbor["ip"]} remote-as ${neighbor["as_num"]}
 neighbor ${neighbor["ip"]} update-source lo
 %if "RR" in data["type"]:
 neighbor ${neighbor["ip"]} route-reflector-client
 %endif
  %endfor  
  !
  address-family ipv6 unicast
    %if len(data["ebgp_neighbors"]) > 0:
    network fde4:5::/32
    %endif
    %for neighbor in data["ebgp_neighbors"]:
    neighbor ${neighbor["ip"]} activate
    %endfor
    %for neighbor in data["ibgp_neighbors"]:
    neighbor ${neighbor["ip"]} activate
    %endfor    
  exit-address-family
!
