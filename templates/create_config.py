#! /usr/bin/env python3

import sys
import json
import os
import stat
from mako.template import Template
from argparse import FileType, ArgumentParser
from pprint import pprint



def setup_self():
    with open('./auto/conf.json') as json_file:
        data = json.load(json_file)
        
        for pop in data["pops"]:
            print("POP "+pop['name']+" "+pop['location'])
            print("Creating start scripts")
            template = Template(filename="start.mako")
            for router in pop["routers"]:
                with open("../isp/" + router['name'] + "_start", 'w') as f:
                    f.write(template.render(data=router))
                    st = os.stat(f.name)
                    os.chmod(f.name, st.st_mode | stat.S_IEXEC)
                        

            print("Creating boot scripts")
            template = Template(filename="boot.mako")
            for router in pop["routers"]:
                with open("../isp/" + router['name'] + "_boot", "w") as f:
                    f.write(template.render(data=router))
                    st = os.stat(f.name)
                    os.chmod(f.name, st.st_mode | stat.S_IEXEC)                        
                

            print("Creating ld.so.conf")
            template = Template(filename="ld.so.conf.mako")
            for router in pop["routers"]:
                with open("../isp/" + router['name'] + "/ld.so.conf", "w") as f:
                    f.write(template.render(data=router))

            print("Creating firewall.sh")
            template = Template(filename="firewall.mako")
            for router in pop["routers"]:
                with open("../isp/" + router['name'] + "/" + router['name'].lower() + "_firewall.sh", "w") as f:
                    f.write(template.render(data=router))
                    st = os.stat(f.name)
                    os.chmod(f.name, st.st_mode | stat.S_IEXEC)


            print("Creating OSPF config")
            template = Template(filename="ospf6d.mako")
            for router in pop["routers"]:
                with open("../isp/" + router['name'] + "/" + router['name'].lower() + "_ospf.conf", "w") as f:
                    f.write(template.render(data=router))                        


            print("Creating BGP config")
            template = Template(filename="bgp.mako")
            for router in pop["routers"]:
                with open("../isp/" + router['name'] + "/" + router['name'].lower() + "_bgp.conf", "w") as f:
                    f.write(template.render(data=router))


            print("Creating zebra config")
            template = Template(filename="zebra.mako")
            for router in pop["routers"]:
                with open("../isp/" + router['name'] + "/" + router['name'].lower() + "_zebra.conf", "w") as f:
                    f.write(template.render(data=router))





def setup_customers():
        with open('./auto/conf.json') as json_file:
            data = json.load(json_file)
            for pop in data["customers"]:
                print("POP "+pop['name']+" "+pop['location'])
                print("Creating start scripts")
                template = Template(filename="start.mako")
                for router in pop["routers"]:
                    with open("../isp/" + router['name'] + "_start", 'w') as f:
                        f.write(template.render(data=router))
                        

                print("Creating boot scripts")
                template = Template(filename="boot.mako")
                for router in pop["routers"]:
                    with open("../isp/" + router['name'] + "_boot", "w") as f:
                        f.write(template.render(data=router))
                        
                

                print("Creating ld.so.conf")
                template = Template(filename="ld.so.conf.mako")
                for router in pop["routers"]:
                    with open("../isp/" + router['name'] + "/ld.so.conf", "w") as f:
                        f.write(template.render(data=router))

                print("Creating OSPF config")
                template = Template(filename="ospf6d.mako")
                for router in pop["routers"]:
                    with open("../isp/" + router['name'] + "/" + router['name'].lower() + "_ospf.conf", "w") as f:
                        f.write(template.render(data=router))                        


                print("Creating BGP config")
                template = Template(filename="bgp.mako")
                for router in pop["routers"]:
                    with open("../isp/" + router['name'] + "/" + router['name'].lower() + "_bgp.conf", "w") as f:
                        f.write(template.render(data=router))


                print("Creating zebra config")
                template = Template(filename="zebra.mako")
                for router in pop["routers"]:
                    with open("../isp/" + router['name'] + "/" + router['name'].lower() + "_zebra.conf", "w") as f:
                        f.write(template.render(data=router))
                    

def main():

    setup_self()
    #setup_customers()
main()

