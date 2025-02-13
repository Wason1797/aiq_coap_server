import asyncio


async def get_meshdiag_topology() -> str:
    try:
        proc = await asyncio.create_subprocess_exec(
            "sudo", "ot-ctl", "meshdiag", "topology", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout_str = ""

        while True:
            line = (await proc.stdout.readline()).decode()
            if "Done" in line:
                break

            stdout_str += line.decode()

        rc = await proc.wait()

        if rc != 0:
            print("ERROR RUNNING COMMAND:", await proc.stderr.readline().decode())
            return ""

        if "Error" in stdout_str:
            print("ERROR RUNNING COMMAND:", stdout_str)
            return ""

        return stdout_str

    except FileNotFoundError:
        print("ERROR RUNNING COMMAND: ot-ctl not installed")
        return ""
