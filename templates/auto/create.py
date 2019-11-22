#! /usr/bin/env python3


# Usage : ./create.py auto_topo
import sys
import json
from pprint import pprint
from ipaddress import ip_address

IP_CONF = None


INIT_FILE='#!/bin/bash\nGROUPNUMBER=5\n# Node configs\nCONFIGDIR=isp\n# boot script name\nBOOT="boot"\n# startup script name\nSTARTUP="start"\nPREFIXBASE="fde4:${GROUPNUMBER}"\nPREFIXLEN=32\n# You can reuse the above two to generate ip addresses/routes, ...\n# e.g. "${PREFIXBASE}:1234::/$((PREFIXLEN+16))"\n# This function describes the network topology that we want to emulate\nfunction mk_topo {\n'


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
    net = create_network(data)
    generate_mini_topo(net)

                                                        


def create_network(data):

    net = Network(data, IP_CONF)
    total_routers = 0
    i = 0
    net.create_pops()
    net.connect_pops()
    net.setup_bgp()
    if 'cust' in net.data:
        net.create_customers()
        net.connect_customers()
    json.dump(net.export(), sys.stdout, indent=4)
    return net

def generate_mini_topo(network):
    with open('isp_topo', 'w') as f:
        f.write(INIT_FILE)
        add_links(f, network)
        f.write("}\n")
        f.close()

def add_links(f, net):
    links_set= {}
    for p in net.pops:
        for router in p.routers:
            for dn in router.direct_neighbors:
                if router.name+"-"+dn not in links_set:
                    f.write("\tadd_link "+router.name+" "+dn+"\n")
                    links_set[router.name+"-"+dn] = True
                    links_set[dn+"-"+router.name] = True
                    # for b in router.bridge_nodes:
                    #     f.write("\tbridge_node "+router.name+" eth"+str(b["eth"])+" "+b["interface"]+"\n")

    for p in net.pops:
        for router in p.routers:
            for b in router.bridge_nodes:
                f.write("\tbridge_node "+router.name+" eth"+str(b["eth"])+" "+b["interface"]+"\n")
                                  
                



## customer - intergface, type, subnet

## ebpg neighbors - interfaec, lsit of as nums
## rename ebgp neighbors


class Customer:
    def __init__(self, pop, interface, subnet, type="home"):
        self.interface = interface # interface the customer is connected on
        self.pop = pop
        self.type = type
        self.subnet = subnet

    def export(self):
        d = vars(self)
        d.pop('pop')
        d['interface'] = self.interface.export()
        return d

        


class Interface:
    def __init__(self, router, description="Link", ip=None, name=None, type=None):
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
        self.type= type
                  
        if description ==None:
            self.description = "link"
        else:
            self.description = description

    def export(self):
        return vars(self)




class BGPNeighbor:
    def __init__(self, ip, as_num, type, interface=None):
        self.ip = ip
        self.as_num = as_num
        self.interface = interface
        self.type = type
    def export(self):
        d =  vars(self)
        if self.interface == None:
            d.pop('interface')
        else :
            d['interface'] = self.interface.export()
            
        return vars(self)
    


class Router:

    def __init__(self, pop, name, router_id, routerbgp_id, passwd="zebra", type=["P"],  hostname=None, color=None):
        # default type P : Provider, PE : Customer Edge, RR : Router reflector
        self.pop = pop # Point of Presence
        if color != None:
            self.color = color # 0 - Red, 1 - Blue
        else:
            if len(pop.routers) == 0:
                self.color = 0
            else:
                self.color = 1 - pop.routers[len(pop.routers) - 1].color # takes the other color of the recently added
        self.type = type                                       # router
        self.name = name+"-"+pop.location
        self.passwd = passwd
        self.customers = []
        if hostname == None:
            self.hostname = self.name
        else:
            self.hostname = hostname
        self.router_id = router_id
        self.routerbgp_id = routerbgp_id
        self.lo_ip = ip_address(self.pop.network.config["GROUP5"]+self.pop.network.config["types"]["lo"]+str(self.pop.location_number)+"00::") + len(pop.routers)+1
        self.lo_ip = str(self.lo_ip) + self.pop.network.config["prefixes"]["lo"]
        self.as_num = IP_CONF["AS"]
        self.ebgp_neighbors = []
        self.ibgp_neighbors = []        
        self.interfaces = []
        self.direct_neighbors = {} # list of routers the router is directly connected to
        self.bridge_nodes = []


    def set_router_id(self, id):
        self.router_id = id
        
    def set_routerbgp_id(self, id):
        self.routerbgp_id = id

    def add_customer(self, customer):
        self.customers.append(customer)
    def set_lo_ip(self, ip):  
        self.lo_ip = ip_address(ip)

    def set_as_num(self, num):
        self.as_num = num

    def add_interface(self, name=None, ip=None, description=None, type=None):
        new_if = Interface(self, description=description, ip=ip, name=name, type=type)
        self.interfaces.append(new_if)

        return new_if
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

    
    """
    Returns the Router as a dict
    """
    def export(self):
        d =  vars(self)
        d['interfaces'] = [i.export() for i in self.interfaces]
        d['direct_neighbors'] = [r for r in self.direct_neighbors.keys()]
        d['pop_name'] = self.pop.location
        d['ebgp_neighbors'] = [n.export() for n in self.ebgp_neighbors]
        d['ibgp_neighbors'] = [n.export() for n in self.ibgp_neighbors]
        d['customers'] = [c.export() for c in self.customers]
        d.pop('pop')        
        return d

        
        
class POP:
    def __init__(self, network, location, name="POP-", type="limb", subnet=None):
        self.routers = []
        self.network = network
        self.type = type
        self.name = name+"-"+type
        self.location = location
        self.location_number = self.network.config['locations'].index(self.location) + 1
        self.total_p2p = 1
        self.subnet = subnet

        

    def add_router(self, router):
                
        self.routers.append(router)


    def add_core_routers(self):
        r1 = Router(self, self.network.generate_next_hostname(),
                    self.network.generate_next_router_id(),
                    self.network.generate_next_routerbgp_id())
        self.add_router(r1)

        r2 = Router(self, self.network.generate_next_hostname(),
                    self.network.generate_next_router_id(),
                    self.network.generate_next_routerbgp_id())
        self.add_router(r2)
        
        self.network.link_routers(r1, r2)

    def update_type(self, type):
        self.type = type
        self.name = "POP-" + str(self.location) + "-"+type

    def export(self):
        return {            
            "routers" : [x.export() for x in self.routers],
            "router_names" : [x.name for x in self.routers],        
            "name" : self.name,
            "type" : self.type,
            "location" : self.location
        }


"""
Represents our ISP Network
"""
class Network:
    def __init__(self, data, config):
        """ 
        data : parsed auto_topo file
        config : dict of ipconf.json
        """
        self.config = config        
        self.name = config['name']
        self.pops = []
        self.customers = []
        self.total_routers = 0
        self.total_inter_pop_links = 1
        self.data = data
        self.total_home_customers = 0
        self.total_enterprise_customers = 0
        self.init_router_id = ip_address("59.59.59.1")
        self.init_routerbgp_id = ip_address("20.20.0.1")
        self.eth = 1



    def generate_next_home_customer_id(self):
        cust_id = format(self.total_home_customers, '04x');
        self.total_home_customers += 1
        return cust_id

    def generate_next_enterprise_customer_id(self):
        cust_id = format(self.total_enterprise_customers, '03x')
        self.total_enterprise_customers += 1
        return cust_id


    def generate_next_customer_subnet(self, type, pop): # type = home || enterprise
        subnet = self.config['GROUP5']+ self.config['types'][type]
        if type == "home":
            subnet += str(pop.location_number) # only have a location associated with home users
            cust_id = self.generate_next_home_customer_id()
            subnet += cust_id[0:2]+":"+cust_id[2:] + "::"+ self.config['prefixes'][type]
        
        elif type == "enterprise" :
            subnet += self.generate_next_enterprise_customer_id()+"::"+self.config['prefixes'][type]

        return subnet
            

        
    def generate_next_eth(self):
        res = self.eth
        self.eth += 1
        return res

    def add_pop(self, pop):
        self.pops.append(pop)

    def get_pop(self, name):
        for pop in self.pops:
            if pop.location == name:
                return pop
        return None


    def add_customer(self, customer):
        self.customers.append(customer)

    def create_customers(self):
        for i in range(len(self.data['cust'])):
            cust_info = self.data['cust'][i]
            customer = POP(self, cust_info[0], name="CUST", type=cust_info[1], subnet=self.generate_next_customer_subnet(cust_info[1], self.get_pop(cust_info[0])))
            self.setup_customer(customer)
            self.add_customer(customer)

    """ 
    Gives the customer 1 router with an interface
    """
    def setup_customer(self, customer):
        r1 = Router(customer, "CUST1-", "60.60.60.1", "60.60.61.1")
        customer.add_router(r1)
        self.link_routers(r1, self.get_pop(customer.location).routers[0])

    def create_pops(self):
        """ Creates our points of presence"""
        for i in range(len(self.config['locations'])):
            location = self.config['locations'][i] # str
            if self.config['locations'].index(location) == self.data['pops']:
                break
            pop = POP(self, location)
            pop.add_core_routers()
            if 'core' in self.data and pop.location in self.data['core']:
                pop.update_type("core")
                self.setup_core_pop(pop)
            self.add_pop(pop)


    def setup_core_pop(self, pop):
        # should add two route reflectors
        rr1 = Router(pop, self.generate_next_hostname(),
                     self.generate_next_router_id(),
                     self.generate_next_routerbgp_id(), type=["P", "RR"], color=0)
        pop.add_router(rr1)
        rr2 = Router(pop, self.generate_next_hostname(),
                     self.generate_next_router_id(),
                     self.generate_next_routerbgp_id(), type=["P", "RR"], color=1)
        pop.add_router(rr2)
        #connect route reflectors to every other router in our core POP
        for r in pop.routers:
            if r.name != rr1.name and r.name != rr2.name:
                self.link_routers(rr1, r)
                self.link_routers(rr2, r)

        # link the two together
        self.link_routers(rr1, rr2)
        

        # create ibgp session between them
        self.create_ibgp_session(rr1, rr2)
  

    # adds the interfaces the two routers will use to communicate
    def link_routers(self,r1, r2):

        if r1.name in r2.direct_neighbors or r1.name == r2.name or r1 == r2:
            return                
        subnet = self.config["GROUP5"] + self.config["types"]["p2p"]
        
        if r1.pop.location != r2.pop.location:
            # for connections between routers in different pops
            subnet +=  self.config['INTERPOPNET']+"00"
            subnet += "::"

            r1_if = Interface(r1, description="Link to "+r2.name, type="i")
            r1_if.ip = str(ip_address(subnet) + (4096 * self.total_inter_pop_links)) + self.config["prefixes"]["p2p"]
            r1.interfaces.append(r1_if)
                        
            r2_if = Interface(r2, description="Link to "+r1.name)
            r2_if.ip = str(ip_address(subnet) + (4096 * self.total_inter_pop_links) + 1) + self.config["prefixes"]["p2p"]
            r2.interfaces.append(r2_if)
            self.total_inter_pop_links += 1


        else :
            # same pop routers
            subnet += str(r1.pop.location_number)+"00"
            subnet += "::"
            r1_if = Interface(r1, description="Link to "+r2.name, type="i")
            r1_if.ip = str(ip_address(subnet) + ( 4096 * r2.pop.total_p2p) ) + self.config["prefixes"]["p2p"]

            r1.interfaces.append(r1_if)
                        
            r2_if = Interface(r2, description="Link to "+r1.name)
            r2_if.ip = str(ip_address(subnet) + ( 4096 * r2.pop.total_p2p) + 1) + self.config["prefixes"]["p2p"]            
            r2.interfaces.append(r2_if)
 

            r1.pop.total_p2p += 1
        

        r1.direct_neighbors[r2.name] = r2
        r2.direct_neighbors[r1.name] = r1
        
        #print(r1.name+" to "+r2.name+" : "+r1_if.ip)
        #print(r2.name+" to "+r1.name+" : "+r2_if.ip)

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
            p.add_core_routers()
                  
    def connect_pops(self):
        """ Connects the Points of Presence using Odd - Even """
        for cp in self.pops:
            # Connect every router that is not a route reflector
            # this is because route reflectors are configured
            # different from our ordinary routers
            for r in [ r for r in cp.routers if "RR" not in r.type]:
                self.connect_router_to_network(r)

    def connect_router_to_network(self, router):
        for p in [pop for pop in self.pops if pop.name != router.pop.name]:
            for r in p.routers:
                if r.color == router.color and r.name not in router.direct_neighbors and "RR" not in r.type and r.pop.location == self.data['core'][0]:
                    self.link_routers(router, r)
                                  
    def setup_bgp(self):
        """ setups up bgp based on the config : auto_topo"""
        for info in self.data['bgp']:
            if info[0] == "EXT":
                # setup the external bgp session
                # defaults to use the pops first routere
                router = self.get_pop(info[2]).routers[0]

                 # add the corresponding interface
                extern_as = info[4]
                
                if_ip = self.config["bgp_neighbor_if_ip"][extern_as]
                interface = router.add_interface(description="eBGP Link to "+extern_as,
                                                 ip=if_ip,
                                                 name=info[5], type="e")
                
                router.add_bgp_neighbor(BGPNeighbor(info[3].split("/")[0], info[4], info[1], interface=interface),
                                        type="e")


                # add this info for creating the bridge_nodes
                router.bridge_nodes.append({"interface" : info[5],
                                                            "eth" : self.generate_next_eth()})
                
            elif info[0] == "INT":
                if info[1] == "odd-even":
                    # setup ibg sessions with same colored routers
                    self.setup_ibgp_odd_even()


    def get_route_reflectors(self):
        rr = []
        core_pops = [self.get_pop(name) for name in self.data['core']]
        for cp in core_pops:
            for r in cp.routers:
                if "RR" in r.type:
                    rr.append(r)
        return rr

                                        
    def setup_ibgp_odd_even(self):
        rr = self.get_route_reflectors()
        for r in rr:
            self.setup_ibgp_same_color(r)


    def get_all_routers(self, type=None):
        routers = []
        for p in self.pops:
            for r in p.routers:
                routers.append(r)
        return routers


    def connect_customers(self):
        for customer in self.customers:
            pop = self.get_pop(customer.location)
            type = customer.type
            cust = Customer(pop, customer.routers[0].interfaces[0], customer.subnet, type)
            pop.routers[0].add_customer(cust)
                                                                     
            
    
    def create_ibgp_session(self, r1, r2):
        r1_neighbor = BGPNeighbor(r2.lo_ip.split("/")[0], r2.as_num, "IBGP")
        r2_neighbor = BGPNeighbor(r1.lo_ip.split("/")[0], r1.as_num, "IBGP")

        if r1.name == r2.name or r1 == r2:
            return
        else:
            r1.add_bgp_neighbor(r1_neighbor, type="i")
            r2.add_bgp_neighbor(r2_neighbor, type="i")
                  
                
    def setup_ibgp_same_color(self,  rr):
        routers = self.get_all_routers()
        for r in routers:
            if r.color == rr.color:
                self.create_ibgp_session(r, rr)

    def export(self):
        return {
            "name" : self.name,
            "pops" : [p.export() for p in self.pops],
            "customers" : [c.export() for c in self.customers]
        }
              




if __name__ == "__main__":
    if len(sys.argv) > 2 or len(sys.argv) < 2:
        print("Bad usage. Help : ./create.py auto_topo")
        sys.exit(1)
    with open('ipconf.json') as ip_file:        
        IP_CONF = json.load(ip_file)
        ip_file.close()
        create_from_file(sys.argv[1])

