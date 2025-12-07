import json
from autonomous_hdb_deepagents.agent.state import PipelineState
from autonomous_hdb_deepagents.agent.tools import load_tools

TOWN_CODE_MAP = {
    "AMK": "ANG MO KIO",
    "BB": "BUKIT BATOK",
    "BD": "BEDOK",
    "BH": "BISHAN",
    "BM": "BUKIT MERAH",
    "BP": "BUKIT PANJANG",
    "BT": "BUKIT TIMAH",
    "CCK": "CHOA CHU KANG",
    "CL": "CLEMENTI",
    "CT": "CENTRAL AREA",
    "GL": "GEYLANG",
    "HG": "HOUGANG",
    "JE": "JURONG EAST",
    "JW": "JURONG WEST",
    "KWN": "KALLANG/WHAMPOA",
    "MP": "MARINE PARADE",
    "PG": "PUNGGOL",
    "PRC": "PASIR RIS",
    "QT": "QUEENSTOWN",
    "SB": "SEMBAWANG",
    "SGN": "SERANGOON",
    "SK": "SENGKANG",
    "TAP": "TAMPINES",
    "TG": "TENGAH",
    "TP": "TOA PAYOH",
    "WL": "WOODLANDS",
    "YS": "YISHUN",
}

async def mrt_resolve_node(state: PipelineState):
    if not state.mrt_station:
        print("[MRT-RESOLVE] No MRT station → skip")
        return state

    tools = await load_tools()
    tool = tools["get-mrt-towns"]

    print(f"[MRT-RESOLVE] Resolving MRT station: {state.mrt_station}")

    res = await tool.ainvoke({"mrt_station": state.mrt_station})

    if isinstance(res, str):
        try: res = json.loads(res)
        except: res = []

    if not res:
        print("[MRT-RESOLVE] No results → skip")
        return state

    best = res[0]
    town_code = best.get("town", "").upper()
    resolved = TOWN_CODE_MAP.get(town_code)

    if resolved:
        print(f"[MRT-RESOLVE] {town_code} → {resolved}")
        state.town = resolved

    return state
