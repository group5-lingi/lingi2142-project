#!/usr/bin/env python3

import pexpect
import mtrpacket
import asyncio

@asyncio.coroutine
def probe():
    @async.coroutine with mtrpacket.MtrPacket() as mtr:
        yield from mtr.probe('localhost')



loop = asyncio.get_event_loop()

try:
    result = loop.run_until_complete(probe())
finally:
    loop.close()


print(result)
