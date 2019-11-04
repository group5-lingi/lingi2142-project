#! /usr/bin/env python3

import sys
import json
from mako.template import Template
from argparse import FileType, ArgumentParser


def main():
    with open('conf.json') as json_file:
        data = json.load(json_file)

        print("Creating start scripts")
        template = Template(filename="start.mako")
        for conf in data:
            with open("../isp/" + conf['name'] + "_start", 'w') as f:
                f.write(template.render(data=conf))

        print("Creating boot scripts")
        template = Template(filename="boot.mako")
        for conf in data:
            with open("../isp/" + conf['name'] + "_boot", "w") as f:
                f.write(template.render(data=conf))

        print("Creating ld.so.conf")
        template = Template(filename="ld.so.conf.mako")
        for conf in data:
            with open("../isp/" + conf['name'] + "/ld.so.conf", "w") as f:
                f.write(template.render(data=conf))

        print("Creating OSPF config")
        template = Template(filename="ospf6d.mako")
        for conf in data:
            with open("../isp/" + conf['name'] + "/" + conf['name'].lower() + "_ospf.conf", "w") as f:
                f.write(template.render(data=conf))

        print("Creating BGP config")
        template = Template(filename="bgp.mako")
        for conf in data:
            with open("../isp/" + conf['name'] + "/" + conf['name'].lower() + "_bgp.conf", "w") as f:
                f.write(template.render(data=conf))


        print("Creating zebra config")
        template = Template(filename="zebra.mako")
        for conf in data:
            with open("../isp/" + conf['name'] + "/" + conf['name'].lower() + "_zebra.conf", "w") as f:
                f.write(template.render(data=conf))


main()

