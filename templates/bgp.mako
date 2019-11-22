log stdout
debug bgp zebra
debug bgp neighbor-events
!
router bgp ${data["as_num"]}
  bgp router-id ${data["routerbgp_id"]}  
  no bgp default ipv4-unicast
  %for neighbor in data["ebgp_neighbors"]:
  neighbor ${neighbor["ip"]} remote-as ${neighbor["as_num"]}
  !
  address-family ipv6 unicast
    neighbor ${neighbor["ip"]} activate
    neighbor ${neighbor["ip"]} update-source ${data["lo_ip"].split("/")[0]}
    neighbor ${neighbor["ip"]} next-hop-self
    neighbor ${neighbor["ip"]} route-map rm-in in
  exit-address-family
  !
  %endfor
  route-map rm-in permit 10
    set ipv6 next-hop global ${data["lo_ip"].split("/")[0]}
  %for neighbor in data["ibgp_neighbors"]:
  !
  neighbor ${neighbor["ip"]} remote-as ${neighbor["as_num"]}
  address-family ipv6 unicast
  %if len(data["ebgp_neighbors"]) > 0:
    network fde4:5::/32
  %endif
    neighbor ${neighbor["ip"]} activate
  %if "RR" in data["type"]:
    neighbor ${neighbor["ip"]} route-reflector-client
  %endif
    neighbor ${neighbor["ip"]} update-source ${data["lo_ip"].split("/")[0]}
  exit-address-family
  %endfor  
  !
!
