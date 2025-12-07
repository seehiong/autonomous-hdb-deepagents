from langgraph.graph import StateGraph, END
from deepagents import CompiledSubAgent
from autonomous_hdb_deepagents.agent.state import PipelineState
from autonomous_hdb_deepagents.agent.intent import intent_node
from autonomous_hdb_deepagents.agent.mrt_resolver import mrt_resolve_node
from autonomous_hdb_deepagents.agent.resale import resale_node
from autonomous_hdb_deepagents.agent.mrt import mrt_node
from autonomous_hdb_deepagents.agent.summary import summary_node

graph = StateGraph(PipelineState)
graph.set_entry_point("intent")

graph.add_node("intent", intent_node)
graph.add_node("mrt_resolve", mrt_resolve_node)
graph.add_node("resale", resale_node)
graph.add_node("mrt", mrt_node)
graph.add_node("summary", summary_node)

graph.add_edge("intent", "mrt_resolve")
graph.add_edge("mrt_resolve", "resale")
graph.add_edge("resale", "mrt")
graph.add_edge("mrt", "summary")
graph.add_edge("summary", END)

compiled_orchestrator = graph.compile()

orchestrator_subagent = CompiledSubAgent(
    name="orchestrator",
    description="Intent → MRT Resolve → Resale → MRT Enrichment → Summary",
    runnable=compiled_orchestrator
)
