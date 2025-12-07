import json
from langchain_core.messages import AIMessage
from autonomous_hdb_deepagents.agent.state import PipelineState
from autonomous_hdb_deepagents.agent.llm import llm

async def summary_node(state: PipelineState):
    flats = state.enriched_flats or []
    print("[SUMMARY] Summarizing", len(flats), "flats")

    if not flats:
        content = "No flats found matching your criteria."
    else:
        preview = [
            {
                "block": f.get("block"),
                "street": f.get("street_name"),
                "price": f"${f.get('resale_price',0):,}",
                "nearest_mrt": f.get("nearest_mrt"),
                "distance": f.get("dist_formatted")
            }
            for f in flats[:5]
        ]

        prompt = f"""
Summarize HDB flats near {state.mrt_station or state.town or "the area"}.

Preview:
{json.dumps(preview, indent=2)}

Total: {len(flats)}

Include:
- Price range
- Closest flats to MRT
- Best value picks
- Patterns and insights
"""

        resp = await llm.ainvoke(prompt)
        content = resp.content

    state.messages.append(AIMessage(content=content))
    return state
