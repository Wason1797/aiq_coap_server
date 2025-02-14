import asyncio


async def get_meshdiag_topology() -> str:
    print("running")
    try:
        proc = await asyncio.create_subprocess_exec(
            "sudo", "ot-ctl", "meshdiag", "topology", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        result = b""

        while True:
            line = await proc.stdout.readline()
            result += line

            if not line:
                break

        rc = await proc.wait()

        if rc != 0:
            print("ERROR RUNNING COMMAND:", (await proc.stderr.readline()).decode())
            return ""

        stdout_str = result.decode()

        if "Error" in stdout_str:
            print("ERROR RUNNING COMMAND:", stdout_str)
            return ""

        return stdout_str.replace("\r", "")

    except FileNotFoundError:
        print("ERROR RUNNING COMMAND: ot-ctl not installed")
        return ""
    except asyncio.IncompleteReadError:
        print("ERROR RUNNING COMMAND: Incomplete read, try again later")
        return ""
