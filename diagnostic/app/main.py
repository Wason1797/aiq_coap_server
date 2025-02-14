from fastapi import FastAPI, HTTPException

from app.cmd.otctl import get_meshdiag_topology
from app.cmd.parser import parse_meshdiag_topology_string, convert_parsed_tokens_into_nodes, make_serializable_graph
from app.tasks.runner import CachedTaskRunner

app = FastAPI(title="Open Thread Diagnostics")

runner = CachedTaskRunner()


@app.get("/topology")
async def get_topology():
    await runner.run_task(get_meshdiag_topology)
    topology_str = await runner.wait_for_result()

    if topology_str == "":
        raise HTTPException(status_code=500, detail="unable to run ot-ctl cmd")

    parsed_topology = parse_meshdiag_topology_string(topology_str)

    if not parsed_topology:
        raise HTTPException(status_code=500, detail="unable to parse topology")

    nodes = convert_parsed_tokens_into_nodes(parsed_topology)

    if not nodes:
        raise HTTPException(status_code=500, detail="unable to make node list")

    return make_serializable_graph(nodes)
