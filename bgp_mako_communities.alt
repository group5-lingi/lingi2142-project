log stdout
debug bgp zebra
debug bgp neighbor-events
ip bgp-community new-format
!
router bgp ${data["as_num"]}
  bgp router-id ${data["routerbgp_id"]}  
  no bgp default ipv4-unicast
  %for neighbor in data["bgp_neighbors"]:
  neighbor ${neighbor["ip"]} remote-as ${neighbor["as_num"]}
  neighbor ${neighbor["ip"]} interface ${data["interfaces"][0]["name"]}
  neighbor ${neighbor["ip"]} update-source ${data["lo_ip"].split("/")[0]}
  neighbor ${neighbor["ip"]} ebgp-multihop
  neighbor ${neighbor["ip"]} send-community
  neighbor ${neighbor["ip"]} route-map rm-in in
  neighbor ${neighbor["ip"]} route-map rm-out out
  %if ${data[bgp-types]} == 0:
  ip community-list 10 permit 1:10
  route-map rm-in permit 10
  set community 1:30
  route-map rm-out 20
  match community-list 10
  %endif
  %if ${data[bgp-types]} == 1:
  ip community-list 10 permit 1:10
  route-map rm-in permit 10
  set community 1:20
  route-map rm-out 20
  match community-list 10
  %endif
  %if ${data[bgp-types]} == 2:
  ip community-list 10 permit 1:10
  route-map rm-in permit 10
  set community 1:20
  route-map rm-out 20
  match community-list 10
  set local-preference 70
  %endif
  %if ${data[bgp-types]} == 3:
  ip community-list 10 permit 1:10 1:20 1:30
  route-map rm-in permit 10
  set community 1:10
  route-map rm-out 20
  match community-list 10
  %endif
  %if ${data[bgp-types]} == 4:
  ip community-list 10 permit 1:10 1:20 1:30
  route-map rm-in permit 10
  set community 1:10
  route-map rm-out 20
  match community-list 10
  set local-preference 70
  %endif
  %endfor  
  !
  address-family ipv6 unicast
    %for neighbor in data["bgp_neighbors"]:
    neighbor ${neighbor["ip"]} activate
    %endfor
  exit-address-family
!
