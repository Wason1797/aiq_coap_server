import asyncio


async def get_meshdiag_topology() -> str:
    try:
        proc = await asyncio.create_subprocess_exec(
            "sudo ot-ctl", "meshdiag", "topology", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        stderr

        if stderr:
            print("ERROR RUNNING COMMAND:", stderr.decode())
            return ""

        output = stdout.decode()

        if "Error" in output:
            print("ERROR RUNNING COMMAND:", output)
            return ""

        return output

    except FileNotFoundError:
        print("ERROR RUNNING COMMAND: ot-ctl not installed")
        return ""
