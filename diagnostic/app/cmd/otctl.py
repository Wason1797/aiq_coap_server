import asyncio
from cachetools import TTLCache
from asyncache import cached

cache = TTLCache(maxsize=1024, ttl=30)


@cached(cache=cache)
async def get_meshdiag_topology() -> str:
    try:
        proc = await asyncio.create_subprocess_exec(
            "sudo", "ot-ctl", "meshdiag", "topology", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout_str = ""

        while True:
            line = (await proc.stdout.readuntil(b"\r\n")).decode()
            stdout_str += line

            if "Done" in line:
                break

        rc = await proc.wait()

        if rc != 0:
            print("ERROR RUNNING COMMAND:", await proc.stderr.readline().decode())
            return ""

        if "Error" in stdout_str:
            print("ERROR RUNNING COMMAND:", stdout_str)
            return ""

        return stdout_str.replace("\r", "")

    except FileNotFoundError:
        print("ERROR RUNNING COMMAND: ot-ctl not installed")
        return ""
