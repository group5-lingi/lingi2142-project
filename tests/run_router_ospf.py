from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import pexpect
import json
def main(router_names):
    for r in router_names:
        router = pexpect.spawnu('../connect_to.sh ../isp '+r)
        router.expect('bash-3.4#')
        

if __name__ == "__main__":
    with open('../templates/auto/conf.json') as json_file:
    data = json.load(json_file)
    router_names = []
    for p in data["pops"]:
        for r in p["routers"]:
            router_names.append(r["name"])
    for c in data["customers"]:
        for r in c["routers"]:
            router_names.append(r["name"])

    
    main(router_names)
