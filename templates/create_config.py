#! /usr/bin/env python3

import sys
import json
from mako.template import Template
from argparse import FileType, ArgumentParser
from pprint import pprint


def main():
    with open('./auto/conf.json') as json_file:
        data = json.load(json_file)

        for pop in data["pops"]:                
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


main()

