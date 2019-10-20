! -*- zebra -*-
!
! zebra sample configuration file
!
hostname ${data['name']}
password ${data['passwd']} 
enable password zebra
!
! Interface's description.
!
interface lo
 description loopback.
!
%for interface in data['interfaces']:
interface ${interface['name']}
 description ${interface['description']}
!
%endfor

