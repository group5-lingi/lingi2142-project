log stdout
debug bgp zebra
debug bgp neighbor-events
!
%for customer in data["customers"]:
ipv6 prefix-list ${customer["interface"]["name"]} seq 5 permit ${customer["subnet"]} ge 48 le 56  
%endfor

router bgp ${data["as_num"]}
  bgp router-id ${data["routerbgp_id"]}
  no bgp default ipv4-unicast
!
!	eBGP
!

 ipv6 prefix-list ours fde4:5::/32
  %for neighbor in data["ebgp_neighbors"]:
  neighbor ${neighbor["ip"].split("/")[0]} remote-as ${neighbor["as_num"]}
  address-family ipv6 unicast
    network fde4:5::/32
    


    %if neighbor["type"] == "SC":
    neighbor ${neighbor["ip"].split("/")[0]} route-map rm-in-sc in
    neighbor ${neighbor["ip"].split("/")[0]} route-map rm-out-sc-p-allow-own out


    %endif
    %if neighbor["type"] == "P":
    neighbor ${neighbor["ip"].split("/")[0]} route-map rm-in-p in
    neighbor ${neighbor["ip"].split("/")[0]} route-map rm-out-sc-p-allow-own out
    neighbor ${neighbor["ip"].split("/")[0]} route-map rm-out-sc-p-allow-client out
 
    %endif
    %if neighbor["type"] == "PB":
    neighbor ${neighbor["ip"].split("/")[0]} route-map rm-in-pb in
    neighbor ${neighbor["ip"].split("/")[0]} route-map rm-out-sc-p out
    %endif
    %if neighbor["type"] == "C":
    neighbor ${neighbor["ip"].split("/")[0]} route-map rm-in-c in
    %endif
    %if neighbor["type"] == "CB":
    neighbor ${neighbor["ip"].split("/")[0]} route-map rm-in-cb in
    %endif
    neighbor ${neighbor["ip"].split("/")[0]} send-community
    neighbor ${neighbor["ip"].split("/")[0]} activate
    neighbor ${neighbor["ip"].split("/")[0]} route-map set-nexthop in
    %if neighbor["ip"] == "fde4:5:3000:1::1":
    neighbor fde4:5:3000:1::1 password ASes6500165005
    %endif
  exit-address-family

  %endfor

  %for customer in data["customers"]:
  address-family ipv6 unicast
    neighbor ${customer["interface"]["ip"].split("/")[0]} prefix-list ${customer["interface"]["name"]} in  
  exit-address-family  
%endfor


!
!	iBGP
!
  bgp route-reflector allow-outbound-policy
  %for neighbor in data["ibgp_neighbors"]:
  !
  neighbor ${neighbor["ip"].split("/")[0]} send-community
  neighbor ${neighbor["ip"].split("/")[0]} route-map NO-ADVERTISE-I out
      
  neighbor ${neighbor["ip"]} remote-as ${neighbor["as_num"]}
  address-family ipv6 unicast
    neighbor ${neighbor["ip"]} activate
  %if "RR" in data["type"]:
    neighbor ${neighbor["ip"]} route-reflector-client
  %endif
    neighbor ${neighbor["ip"]} update-source lo
  %if len(data["ebgp_neighbors"]) > 0:
    !neighbor ${neighbor["ip"]} route-map set-nexthop out
    !neighbor ${neighbor["ip"]} route-map set-nexthop in
  %endif
    neighbor ${neighbor["ip"]} password ${neighbor["password"]}
  exit-address-family

  %endfor  
  !

  
  route-map set-nexthop permit 10
   set ipv6 next-hop global ${data["lo_ip"].split("/")[0]}
   set ipv6 next-hop prefer global   

 
!
!	Route Maps
!
   
   bgp community-list set-local-pref-70-community permit 65005:170
   bgp community-list set50-local-pref-80-community permit 65005:180
   bgp community-list set-local-pref-90-community permit 65005:190
   bgp community-list no-export-community permit 65005:60
   bgp community-list no-advertise-community permit 65005:70
   bgp community-list client-community permit 65005:10 65005:20

! Set community on ingress

   route-map rm-in-sc permit 10
     set community 65005:30

 
   route-map rm-in-c permit 23
     set community 65005:10
     
   
   route-map rm-in-cb permit 24
    set local-preference 70
    set community 65005:20

  

! Set local pref on match

   route-map set-local-pref-60 permit 10
     match community set-local-pref-70-community
     set local-preference 60

   route-map set-local-pref-70 permit 11
     match community set-local-pref-80-community
     set local-preference 70

   route-map set-local-pref-80 permit 12
     match community set-local-pref-90-community
     set local-preference 80

! Block on match

   route-map NO-ADVERTISE-E deny 13
     match community no-advertise-community
   route-map NO-ADVERTISE-E permit 14

   route-map NO-ADVERISE-I deny 15
     match community no-advertise-community
   route-map NO-ADVERTISE-I permit 16


! Allow on own prefix

   route-map rm-out-sc-p-allow-own permit 18
     match ipv6 prefix-list ours


! Block EBGP on match

   route-map NO-EXPORT deny 19
     match community no-export-community
   route-map NO-EXPORT permit 20

   route-map rm-in-p permit 21
     set community 65005:40


   route-map rm-in-pb permit 22
     set local-preference 70
     set community 65005:50


   bgp community-list allow-all permit 65005:10 65005:20 65005:30 65005:40 65005:50
 
 
