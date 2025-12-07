import os
import json
import asyncio
from typing import List, Dict, Optional
from pydantic import BaseModel, ConfigDict

from deepagents import CompiledSubAgent, create_deep_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langgraph.graph import StateGraph, END
from toolbox_langchain import ToolboxClient


# ============================================================
# LLM
# ============================================================
llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="amazon/nova-2-lite-v1:free",
    temperature=0
)


# ============================================================
# Tool loading (cached client)
# ============================================================
_toolbox_client: Optional[ToolboxClient] = None

async def get_toolbox_client():
    global _toolbox_client
    if _toolbox_client is None:
        _toolbox_client = ToolboxClient("http://127.0.0.1:5000")
    return _toolbox_client

async def load_tools():
    client = await get_toolbox_client()
    tools = await client.aload_toolset()
    return {t.name: t for t in tools}


# ============================================================
# Pipeline State
# ============================================================
class PipelineState(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    messages: List[BaseMessage] = []
    flats: List[Dict] = []
    enriched_flats: List[Dict] = []
    # Intent
    town: Optional[str] = None
    flat_type: Optional[str] = None
    max_price: Optional[int] = None
    mrt_radius: Optional[int] = None
    mrt_station: Optional[str] = None



# ============================================================
# INTENT EXTRACTION NODE
# ============================================================
async def intent_node(state: PipelineState):
    user_msg = None
    for m in state.messages:
        if isinstance(m, HumanMessage):
            user_msg = m.content
            break

    if not user_msg:
        return state

    prompt = """
Extract user intent. Return JSON with these fields (include even if null):
{
  "town": "string or null",
  "mrt_station": "string or null",
  "flat_type": "string or null",
  "max_price": "number or null",
  "mrt_radius": "number or null"
}

RULES:
1. MRT mentions: "near <name> MRT", "<name> station", "around <name>" → extract "mrt_station"
   Examples: "Bukit Panjang MRT" → "BUKIT PANJANG", "Toa Payoh station" → "TOA PAYOH"

2. Town mentions (explicit): "in <town>", "<town> area" → extract "town"
   Examples: "in Bedok", "Tampines area" → "BEDOK", "TAMPINES"

3. Flat types: "4-room", "4 room", "4rm" → "4 ROOM"; "5-room" → "5 ROOM"

4. Prices: "$500k", "500k", "500,000", "under 600k" → numeric

5. Radius: "within 500m", "800m" → numeric (in meters)

6. Use UPPERCASE for town/station names.

7. Return null if not mentioned. Return ALL five fields.

User query: "%s"

RETURN JSON ONLY. NO EXPLANATION.
""" % user_msg

    resp = await llm.ainvoke(prompt)
    content = resp.content.strip()
    
    # Try to extract JSON from response
    try:
        # Handle case where LLM wraps response in markdown
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        intent = json.loads(content)
    except Exception as e:
        print(f"[INTENT] JSON parse error: {e}, raw: {content}")
        intent = {}

    print("[INTENT] Parsed intent →", intent)

    return PipelineState(
        messages=state.messages,
        flats=state.flats,
        enriched_flats=state.enriched_flats,
        town=intent.get("town"),
        flat_type=intent.get("flat_type"),
        max_price=intent.get("max_price"),
        mrt_radius=intent.get("mrt_radius"),
        mrt_station=intent.get("mrt_station")
    )


# ============================================================
# TOWN CODE TO FULL NAME MAPPING
# ============================================================
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


# ============================================================
# MRT RESOLVER NODE
# ============================================================
async def mrt_resolve_node(state: PipelineState):
    if not state.mrt_station:
        print("[MRT-RESOLVE] No MRT station detected → skip")
        return state

    tools = await load_tools()
    tool = tools["get-mrt-towns"]

    print(f"[MRT-RESOLVE] Resolving MRT station: {state.mrt_station}")

    res = await tool.ainvoke({"mrt_station": state.mrt_station})

    if isinstance(res, str):
        try: 
            res = json.loads(res)
        except: 
            res = []

    if not (isinstance(res, list) and len(res) > 0):
        print("[MRT-RESOLVE] No rows returned → skipping town override")
        return state

    # Get the nearest/best town mapping
    best = res[0]
    town_code = best.get("town")
    
    if not town_code:
        print("[MRT-RESOLVE] No town code found in result")
        return state
    
    # Map town code to full town name
    resolved_town = TOWN_CODE_MAP.get(town_code.upper())
    
    if resolved_town:
        print(f"[MRT-RESOLVE] MRT → {town_code} → {resolved_town}")
    else:
        print(f"[MRT-RESOLVE] Warning: No mapping for town code '{town_code}'")
        # Try to use distance to determine best town from all results
        resolved_town = None
        for row in res:
            tc = row.get("town", "").upper()
            if tc in TOWN_CODE_MAP:
                resolved_town = TOWN_CODE_MAP[tc]
                print(f"[MRT-RESOLVE] Using alternative: {tc} → {resolved_town}")
                break

    return PipelineState(
        messages=state.messages,
        flats=state.flats,
        enriched_flats=state.enriched_flats,
        town=resolved_town or state.town,
        flat_type=state.flat_type,
        max_price=state.max_price,
        mrt_radius=state.mrt_radius,
        mrt_station=state.mrt_station
    )


# ============================================================
# RESALE NODE
# ============================================================
async def resale_node(state: PipelineState):
    town = state.town or "TOA PAYOH"
    flat_type = state.flat_type or "4 ROOM"
    max_price = state.max_price or 600000

    tools = await load_tools()
    sql = tools["list-hdb-flats"]

    print(f"[RESALE] Fetching {flat_type} in {town} <= {max_price}...")

    flats = await sql.ainvoke({
        "town": town,
        "max_price": max_price,
        "flat_type": flat_type
    })

    if isinstance(flats, str):
        try: flats = json.loads(flats)
        except: flats = []

    if not isinstance(flats, list):
        flats = []

    print(f"[RESALE] Retrieved {len(flats)} flats")

    return PipelineState(
        messages=state.messages,
        flats=flats,
        enriched_flats=[],
        town=town,
        flat_type=flat_type,
        max_price=max_price,
        mrt_radius=state.mrt_radius,
        mrt_station=state.mrt_station
    )



# ============================================================
# MRT ENRICHMENT NODE
# ============================================================
async def mrt_node(state: PipelineState):
    flats = state.flats or []
    radius = state.mrt_radius or 800

    print(f"[MRT] Enriching {len(flats)} flats (radius={radius})")

    tools = await load_tools()
    geo = tools["geospatial-query"]

    # Deduplicate coords
    uniq = {}
    for f in flats:
        lat = f.get("lat")
        lon = f.get("lon")
        if lat and lon:
            uniq.setdefault((lat, lon), []).append(f)

    coord_results = {}
    for (lat, lon), group in uniq.items():
        res = await geo.ainvoke({
            "mode": "nearest_mrt",
            "lat": lat,
            "lon": lon,
            "radius": radius
        })

        if isinstance(res, str):
            try: 
                res = json.loads(res)
            except: 
                res = []

        if isinstance(res, list) and res:
            best = res[0]
            raw_dist = best.get("dist_m")
            
            # Determine unit and format
            if raw_dist is not None:
                # Check if it's likely degrees (small values < 0.1)
                if raw_dist < 0.1:
                    # Assume degrees, convert to meters
                    meters = raw_dist * 111000  # 1 degree ≈ 111km
                    formatted = format_meters(meters)
                    unit = "degrees"
                elif raw_dist < 1000:
                    # Assume kilometers (0.1 to 1000)
                    meters = raw_dist * 1000
                    formatted = format_meters(meters)
                    unit = "km"
                else:
                    # Assume meters
                    formatted = format_meters(raw_dist)
                    unit = "m"
            else:
                formatted = "N/A"
                unit = None
            
            coord_results[(lat, lon)] = {
                "nearest_mrt": best.get("label"),
                "dist_raw": raw_dist,
                "dist_formatted": formatted,
                "dist_unit": unit
            }
        else:
            coord_results[(lat, lon)] = {
                "nearest_mrt": None,
                "dist_raw": None,
                "dist_formatted": "N/A",
                "dist_unit": None
            }

    enriched = []
    for f in flats:
        lat = f.get("lat")
        lon = f.get("lon")
        extra = coord_results.get((lat, lon), {})
        f["nearest_mrt"] = extra.get("nearest_mrt")
        f["dist_raw"] = extra.get("dist_raw")
        f["dist_formatted"] = extra.get("dist_formatted")
        f["dist_unit"] = extra.get("dist_unit")
        enriched.append(f)

    if enriched:
        example = enriched[0]
        print(f"[MRT] Enrichment complete — example: {example['street_name']} → {example['nearest_mrt']} ({example['dist_formatted']})")
    else:
        print("[MRT] Enrichment complete — no flats")

    return PipelineState(
        messages=state.messages,
        flats=state.flats,
        enriched_flats=enriched,
        town=state.town,
        flat_type=state.flat_type,
        max_price=state.max_price,
        mrt_radius=radius,
        mrt_station=state.mrt_station
    )


# ============================================================
# DISTANCE FORMATTING HELPERS
# ============================================================
def format_meters(meters):
    """Format distance in meters to human-readable string."""
    if meters is None:
        return "N/A"
    
    if meters < 1000:
        return f"{int(round(meters))}m"
    else:
        km = meters / 1000
        if km < 10:
            # Show 1 decimal for < 10km
            return f"{km:.1f}km".rstrip('0').rstrip('.') + "km"
        else:
            # Round to nearest km for >= 10km
            return f"{int(round(km))}km"


# ============================================================
# SUMMARY NODE
# ============================================================
async def summary_node(state: PipelineState):
    flats = state.enriched_flats or []
    print("[SUMMARY] Summarizing", len(flats), "flats")

    if not flats:
        summary = "No flats found matching your criteria."
    else:
        # Create a preview with formatted distances
        preview = []
        for flat in flats[:5]:  # Show first 5 as preview
            preview.append({
                "block": flat.get("block"),
                "street": flat.get("street_name"),
                "price": f"${flat.get('resale_price', 0):,}",
                "nearest_mrt": flat.get("nearest_mrt", "Unknown").replace(" MRT STATION", ""),
                "distance": flat.get("dist_formatted", "N/A")
            })
        
        prompt = f"""
Summarize the following HDB flats near {state.mrt_station or state.town or 'the area'}:

Flats data (first {len(preview)} of {len(flats)}):
{json.dumps(preview, indent=2)}

Total flats found: {len(flats)}

Please provide a concise summary that includes:
1. Price range
2. Closest flats to MRT stations (use the actual distances like "350m", "1.2km")
3. Best value picks
4. Any notable patterns

Format distances in a human-readable way (e.g., "350m" not "0.35km").
"""
        resp = await llm.ainvoke(prompt)
        summary = resp.content

    return PipelineState(
        messages=state.messages + [AIMessage(content=summary)],
        flats=state.flats,
        enriched_flats=state.enriched_flats,
        town=state.town,
        flat_type=state.flat_type,
        max_price=state.max_price,
        mrt_radius=state.mrt_radius,
        mrt_station=state.mrt_station
    )


# ============================================================
# BUILD PIPELINE GRAPH (ORCHESTRATOR)
# ============================================================
graph = StateGraph(PipelineState)
graph.add_node("intent", intent_node)
graph.add_node("mrt_resolve", mrt_resolve_node)
graph.add_node("resale", resale_node)
graph.add_node("mrt", mrt_node)
graph.add_node("summary", summary_node)

graph.set_entry_point("intent")
graph.add_edge("intent", "mrt_resolve")
graph.add_edge("mrt_resolve", "resale")
graph.add_edge("resale", "mrt")
graph.add_edge("mrt", "summary")
graph.add_edge("summary", END)

compiled_orchestrator = graph.compile()

orchestrator_subagent = CompiledSubAgent(
    name="orchestrator",
    description="Orchestrates intent → MRT resolve → resale → MRT-enrichment → summary.",
    runnable=compiled_orchestrator
)



# ============================================================
# DEEP AGENT
# ============================================================
system_prompt = """
You are an HDB property finder. Always forward user queries to the orchestrator.
"""

deep_agent = create_deep_agent(
    model=llm,
    system_prompt=system_prompt,
    subagents=[orchestrator_subagent]
)



# ============================================================
# CLI HELPER
# ============================================================
def extract_final_message(result):
    msgs = result.get("messages")
    if isinstance(msgs, list):
        for m in reversed(msgs):
            if isinstance(m, AIMessage):
                return m.content
    return None



# ============================================================
# CLI ENTRYPOINT
# ============================================================
async def run_cli(query: str):
    result = await deep_agent.ainvoke({
        "messages": [HumanMessage(content=query)]
    })

    final = extract_final_message(result)
    return final or "No output extracted."


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py \"your query\"")
        sys.exit(1)

    query = sys.argv[1]

    async def main():
        out = await run_cli(query)
        print("\n=== FINAL RESPONSE ===\n")
        print(out)

    asyncio.run(main())
