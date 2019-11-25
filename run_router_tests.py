#!/usr/bin/python3
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import pexpect
import sys
import json
def main(router_names):
    for r in router_names:
        
        router = pexpect.spawnu('./connect_to.sh isp '+r)
        router.logfile = sys.stdout
        router.expect('bash-4.3# ')
        router.sendline('cd tests')
        router.expect('bash-4.3# ')
        router.sendline('python3.6 ospf_test.py')
        router.expect('bash-4.3# ')

if __name__ == "__main__":
    with open('./templates/auto/conf.json') as json_file:
        data = json.load(json_file)
        router_names = []
        for p in data["pops"]:
            for r in p["routers"]:
                router_names.append(r["name"])
    
        main(router_names)
