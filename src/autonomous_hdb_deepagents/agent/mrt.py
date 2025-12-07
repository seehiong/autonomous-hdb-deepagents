import json
from autonomous_hdb_deepagents.agent.state import PipelineState
from autonomous_hdb_deepagents.agent.tools import load_tools

def format_meters(meters):
    if meters < 1000:
        return f"{int(round(meters))}m"
    km = meters / 1000
    if km < 10:
        return f"{km:.1f}km"
    return f"{int(round(km))}km"

async def mrt_node(state: PipelineState):
    flats = state.flats
    radius = state.mrt_radius or 800

    print(f"[MRT] Enriching {len(flats)} flats (radius={radius})")

    tools = await load_tools()
    geo = tools["geospatial-query"]

    # Deduplicate coords
    uniq = {}
    for f in flats:
        lat, lon = f.get("lat"), f.get("lon")
        if lat and lon:
            uniq.setdefault((lat, lon), []).append(f)

    coord_results = {}

    for (lat, lon) in uniq:
        res = await geo.ainvoke({
            "mode": "nearest_mrt",
            "lat": lat,
            "lon": lon,
            "radius": radius
        })

        if isinstance(res, str):
            try: res = json.loads(res)
            except: res = []

        if not res:
            coord_results[(lat, lon)] = {
                "nearest_mrt": None,
                "dist_formatted": "N/A"
            }
            continue

        best = res[0]
        raw = best.get("dist_m")

        # Determine unit from your working logic
        if raw < 0.1:
            meters = raw * 111000
        elif raw < 1000:
            meters = raw * 1000
        else:
            meters = raw

        coord_results[(lat, lon)] = {
            "nearest_mrt": best.get("label"),
            "dist_formatted": format_meters(meters)
        }

    # Attach results
    enriched = []
    for f in flats:
        lat, lon = f.get("lat"), f.get("lon")
        extra = coord_results.get((lat, lon), {})
        f["nearest_mrt"] = extra.get("nearest_mrt")
        f["dist_formatted"] = extra.get("dist_formatted")
        enriched.append(f)

    if enriched:
        e = enriched[0]
        print(f"[MRT] Example: {e['street_name']} → {e['nearest_mrt']} ({e['dist_formatted']})")

    state.enriched_flats = enriched
    return state
