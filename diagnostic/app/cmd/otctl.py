import subprocess


def get_meshdiag_topology() -> str:
    try:
        result = subprocess.run(["ot-ctl", "meshdiag", "topology"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            print("ERROR RUNNING COMMAND:", result.stderr.decode())
            return ""

        output = result.stdout.decode()

        if "Error" in output:
            print("ERROR RUNNING COMMAND:", output)
            return ""

        return output

    except FileNotFoundError:
        print("ERROR RUNNING COMMAND: ot-ctl not installed")
        return ""
