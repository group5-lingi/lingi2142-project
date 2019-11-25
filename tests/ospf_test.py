import asyncio
import sys
import mtrpacket
import json



def main(lo_ips):
    fails = 0
    print(lo_ips)
    loop = asyncio.get_event_loop()
    coroutines = []
    for i, r in enumerate(lo_ips):
        print("PING "+r+"("+lo_ips[r]+")")
        try:
            coroutines.append(probe(lo_ips[r], fails))
            try:
                loop.run_until_complete(coroutines[i])
            except mtrpacket.HostResolveError:
                print("Can't resolve host '{}'".format())
        except:
            print("ERROR")
    loop.close()



async def probe(host, fails):
    async with mtrpacket.MtrPacket() as mtr:
        result = await mtr.probe(host)

        #  If the ping got a reply, report the IP address and time
        if result.success:
            print('reply from {} in {} ms'.format(
                result.responder, result.time_ms))
        else:
            print('no reply from '+host)
            fails += 1






if __name__ == "__main__":
    with open('../templates/auto/conf.json') as json_file:
        data = json.load(json_file)
        lo_ips = {}
        for p in data["pops"]:
            for r in p["routers"]:
                lo_ips[r["name"]] = r["lo_ip"].split("/")[0]
        for c in data["customers"]:
            for r in c["routers"]:
                lo_ips[r["name"]] = r["lo_ip"].split("/")[0]
    main(lo_ips)

#  We need asyncio's event loop to run the coroutine
# loop = asyncio.get_event_loop()
# try:
#     probe_coroutine = probe(hostname)
#     try:
#         loop.run_until_complete(probe_coroutine)
#     except mtrpacket.HostResolveError:
#         print("Can't resolve host '{}'".format(hostname))
# finally:
#     loop.close()
