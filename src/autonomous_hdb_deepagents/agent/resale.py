import json
from autonomous_hdb_deepagents.agent.state import PipelineState
from autonomous_hdb_deepagents.agent.tools import load_tools

def normalize_flat_type(ft):
    if not ft:
        return "4 ROOM"
    ft = ft.replace("-", " ").replace("rm", " room").upper()
    ft = ft.replace("  ", " ")
    # Map canonical forms
    mappings = {
        "4 ROOM": "4 ROOM",
        "5 ROOM": "5 ROOM",
        "3 ROOM": "3 ROOM",
        "2 ROOM": "2 ROOM",
    }
    for key in mappings:
        if key in ft:
            return mappings[key]
    return ft

async def resale_node(state: PipelineState):
    town = (state.town or "TOA PAYOH").upper()
    flat_type = normalize_flat_type(state.flat_type)
    max_price = state.max_price or 600000

    tools = await load_tools()
    sql = tools["list-hdb-flats"]

    print(f"[RESALE] Fetching {flat_type} in {town} <= {max_price}...")

    flats = await sql.ainvoke({
        "town": town,
        "max_price": max_price,
        "flat_type": flat_type
    })

    if flats is None:
        flats = []

    if isinstance(flats, str):
        try: flats = json.loads(flats)
        except: flats = []
        
    if not isinstance(flats, list):
        flats = []

    print(f"[RESALE] Retrieved {len(flats)} flats")

    state.flats = flats
    return state
