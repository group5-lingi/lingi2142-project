#! /usr/bin/env python3


# Usage : ./create.py auto_topo
import sys
import json
from argparse import FileType, ArgumentParser
from pprint import pprint
from ipaddress import ip_address

IP_CONF = None


def create_from_file(filename):
        data = { }
        try:
                with open(filename, 'r') as f:
                        for l in f:
                                line = l.replace('\n', '')
                                parts = line.split()
                                if parts[0] == "#":
                                        continue
                                if parts[0] == "pops":
                                        data['pops'] = int(parts[1])
                                else:
                                        if parts[0] not in data:
                                                data[parts[0]] = []
                                                
                                        if len(parts[1:]) > 1:
                                                data[parts[0]].append(parts[1:])
                                        else:
                                                data[parts[0]].append(parts[1])
                                                
                        f.close()
        except:
                sys.exit("error in parsing")
        create_network(data)


                                                        


def create_network(data):

        net = Network(data, IP_CONF)
        total_routers = 0
        i = 0
        net.create_pops()
        net.add_core_routers()
        net.connect_pops()
        net.setup_bgp()

        pprint(net.export())

                

class Interface:
        def __init__(self, router, description="Link", ip=None, name=None):
                if name == None:
                        self.name = router.name+"-eth"+str(len(router.interfaces))
                else:
                        self.name = name
                self.cost = 5
                self.hello_time = 10
                self.dead_time = 40
                self.instance_id = 0
                self.area = "0.0.0.0"
                self.active = True
                self.ip = ip
            
                if description ==None:
                        self.description = "link"
                else:
                        self.description = description

        def export(self):
                return vars(self)




class BGPNeighbor:
        def __init__(self, ip, as_num, type):
                self.ip = ip
                self.as_num = as_num
                self.type = type
        def export(self):
                return vars(self)


class Router:

        def __init__(self, pop, name, router_id, routerbgp_id, passwd="zebra", type=["P"],  hostname=None):
                # default type P : Provider, PE : Customer Edge, RR : Router reflector
                self.pop = pop # Point of Presence
                self.color = None # 0 - Red, 1 - Blue
                if len(pop.routers) == 0:
                        self.color = 0
                else:
                        self.color = 1 - pop.routers[len(pop.routers) - 1].color # takes the other color of the recently added
                self.type = type                                       # router
                self.name = name+"-"+pop.location_name
                self.passwd = passwd
                if hostname == None:
                        self.hostname = self.name
                else:
                        self.hostname = hostname
                self.router_id = router_id
                self.routerbgp_id = router_id
                self.lo_ip = ip_address(IP_CONF["GROUP5"]+IP_CONF["types"]["lo"]+self.pop.location+"::") + len(pop.routers)+1
                self.lo_ip = str(self.lo_ip) + IP_CONF["prefixes"]["lo"]
                self.as_num = IP_CONF["AS"]
                self.ebgp_neighbors = []
                self.ibgp_neighbors = []        
                self.interfaces = []
                self.direct_neighbors = {} # list of routers the router is directly connected to


        def set_router_id(self, id):
                self.router_id = id

        def set_routerbgp_id(self, id):
                self.routerbgp_id = id

        def set_lo_ip(self, ip):  
                self.lo_ip = ip_address(ip)

        def set_as_num(self, num):
                self.as_num = num

        def add_interface(self, name=None, ip=None, description=None):
                self.interfaces.append(Interface(self, description=description, ip=ip, name=name))
        """
        type : "e" => ebgp neighbor , neighbor != None
        "i" => ibgp neighbor , router != None
        default is ibgp
        """
        def add_bgp_neighbor(self,neighbor=None, type="i"):
                if type == "e":
                
                        self.ebgp_neighbors.append(neighbor)
                else:
                        self.ibgp_neighbors.append(neighbor)

    
        def add_link(self, router, start=None): # creates a p2p between self and the other router
                subnet = IP_CONF["GROUP5"] + IP_CONF["types"]["p2p"]
                total_inter_pop_links = start
            
                if self.pop.location_name != router.pop.location_name:
                        # for connections between routers in different pops
                        subnet += IP_CONF["locations"]["P2P-INTER-POP"]
                        subnet += "::"

                        my_if = Interface(self, description="Link to "+router.name)
                        my_if.ip = str(ip_address(subnet) + start) + IP_CONF["prefixes"]["p2p"]
                        self.interfaces.append(my_if)
                        total_inter_pop_links += 1
            
                        router_if = Interface(router, description="Link to "+self.name)
                        router_if.ip = str(ip_address(subnet) + total_inter_pop_links) + IP_CONF["prefixes"]["p2p"]
                        router.interfaces.append(router_if)
                        total_inter_pop_links += 1

                else :
                
                        subnet += IP_CONF["locations"][self.pop.location_name]
                        subnet += "::"
                        my_if = Interface(self, description="Link to "+router.name)
                        my_if.ip = str(ip_address(subnet) + len(self.interfaces) + len(router.interfaces) + 1) + IP_CONF["prefixes"]["p2p"]
                        self.interfaces.append(my_if)
            
                        router_if = Interface(router, description="Link to "+self.name)
                        router_if.ip = str(ip_address(subnet) + len(self.interfaces) + len(router.interfaces) + 1) + IP_CONF["prefixes"]["p2p"]            
                        router.interfaces.append(router_if)


                self.direct_neighbors[router.name] = router
                router.direct_neighbors[self.name] = self
        



        """
        Returns the Router as a dict
        """
        def export(self):
                d =  vars(self)
                d['interfaces'] = [i.export() for i in self.interfaces]
                d['direct_neighbors'] = [r for r in self.direct_neighbors.keys()]
                d['pop_name'] = self.pop.location_name
                d['ebgp_neighbors'] = [n.export() for n in self.ebgp_neighbors]
                d.pop('pop')

        
                return d

        

class POP:
        def __init__(self, location, name="POP-", type="limb"):
                self.routers = []
                self.type = type
                self.name = name + str(location) + "-"+type
                self.location = IP_CONF["locations"][location] # str
                self.location_name = location

        def add_router(self, router):
                self.routers.append(router)


        def add_core_routers(self, net):
                r1 = Router(self, net.generate_next_hostname(), net.generate_next_router_id(),
                            net.generate_next_routerbgp_id())
                self.add_router(r1)
            
                r2 = Router(self, net.generate_next_hostname(), net.generate_next_router_id(),
                            net.generate_next_routerbgp_id())
                self.add_router(r2)
                r1.add_link(r2)

        def update_type(self, type):
                self.type = type
                self.name = "POP-" + str(self.location_name) + "-"+type

        def export(self):
                return {
                
                        "routers" : [x.export() for x in self.routers],
                        "router_names" : [x.name for x in self.routers],        
                        "name" : self.name,
                        "type" : self.type,
                        "location" : self.location,
                        "location_name" : self.location_name
                }



class Network:
        def __init__(self, data, config):
                self.name = config['name']
                self.config = config
                self.pops = []
                self.total_routers = 0
                self.total_inter_pop_links = 1
                self.data = data
                self.init_router_id = ip_address("255.251.0.1")
                self.init_routerbgp_id = ip_address("20.20.0.1")

        def add_pop(self, pop):
                self.pops.append(pop)

        def get_pop(self, name):
                for pop in self.pops:
                        if pop.location_name == name:
                                return pop
                return None


        def create_pops(self):
                i = 0
                for location in self.config['locations']:
                        if i == self.data['pops'] or location == "P2P-INTER-POP":
                                break
                        else:
                                pop = POP(location)
                                if pop.location_name in self.data['core']:
                                        pop.update_type("core")
                                        self.setup_core_pop(pop)
                                self.add_pop(pop)
                                i += 1


        def setup_core_pop(self, pop):
                # should add two route reflectors
                pop.add_router(Router(pop, self.generate_next_hostname(),
                                      self.generate_next_router_id(),
                                      self.generate_next_routerbgp_id(), type=["P", "RR"]))


                pop.add_router(Router(pop, self.generate_next_hostname(),
                                      self.generate_next_router_id(),
                                      self.generate_next_routerbgp_id(), type=["P", "RR"]))
        

        def generate_next_router_id(self):
                id = str(self.init_router_id + 1)
                self.init_router_id += 1
                return id

        def generate_next_routerbgp_id(self):
                id = str(self.init_routerbgp_id + 1)
                self.init_routerbgp_id += 1
                return id

        def generate_next_hostname(self):
                h = "P"+str(self.total_routers +1)
                self.total_routers += 1
                return h


        def add_core_routers(self):
                for p in self.pops:
                        #add two core routers to each POP
                        p.add_core_routers(self)

        def connect_pops(self):
                for cp in self.pops:
                        for r in [ r for r in cp.routers if "RR" not in r.type]:
                                self.connect_router_to_network(r)

        def connect_router_to_network(self, router):
                for p in [pop for pop in self.pops if pop.name != router.pop.name]:
                        for r in p.routers:
                                if r.color == router.color and r.name not in router.direct_neighbors and "RR" not in r.type:
                                       router.add_link(r, start=self.total_inter_pop_links)
                                       self.total_inter_pop_links += 2


        def setup_bgp(self):
                for info in self.data['bgp']:
                        if info[0] == "EXT":
                                # setup the external bgp session
                                # defaults to use the pops first routere
                                router = self.get_pop(info[2]).routers[0]
                                router.add_bgp_neighbor(BGPNeighbor(info[3], info[4], info[1]), type="e")

                                # add the corresponding interface
                                extern_as = info[4]

                                if_ip = self.config["bgp_neighbor_if_ip"][extern_as]
                                router.add_interface(description="eBGP Link to "+extern_as,
                                                     ip=if_ip,
                                                     name=info[5])
                                                 

        def export(self):
                return {
                        "name" : self.name,
                        "pops" : [p.export() for p in self.pops]
                }
        




if __name__ == "__main__":
        if len(sys.argv) > 2 or len(sys.argv) < 2:
                print("Bad usage. Help : ./create.py auto_topo")
                sys.exit(1)
        with open('ipconf.json') as ip_file:        
                IP_CONF = json.load(ip_file)      
                ip_file.close()
        create_from_file(sys.argv[1])

