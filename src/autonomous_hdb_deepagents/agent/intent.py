import json
from langchain_core.messages import HumanMessage
from autonomous_hdb_deepagents.agent.state import PipelineState
from autonomous_hdb_deepagents.agent.llm import llm

async def intent_node(state: PipelineState):
    """
    EXACT logic from your working agent.py
    """
    user_msg = None
    for m in state.messages:
        if isinstance(m, HumanMessage):
            user_msg = m.content
            break

    if not user_msg:
        return state

    prompt = f"""
Extract user intent. Return JSON with all fields even if null:
{{
  "town": "string or null",
  "mrt_station": "string or null",
  "flat_type": "string or null",
  "max_price": "number or null",
  "mrt_radius": "number or null"
}}

RULES:
- MRT mentions: "near <station> MRT", "next to <station>"
- Town mentions: "in <town>"
- Flat type: "4-room", "5 rm"
- Price: "$500k", "under 600k"
- Radius: "within 800m"

User query: "{user_msg}"
Return JSON only.
"""

    resp = await llm.ainvoke(prompt)
    content = resp.content.strip()

    # Strip markdown fences
    if content.startswith("```"):
        content = content.strip("```json").strip("```")

    try:
        intent = json.loads(content)
    except Exception:
        print("[INTENT] JSON parse error:", content)
        intent = {}

    print("[INTENT] Parsed intent →", intent)

    return PipelineState(
        messages=state.messages,
        flats=state.flats,
        enriched_flats=state.enriched_flats,
        town=intent.get("town").upper() if intent.get("town") else None,
        flat_type=intent.get("flat_type"),
        max_price=intent.get("max_price"),
        mrt_radius=intent.get("mrt_radius"),
        mrt_station=intent.get("mrt_station")
    )
