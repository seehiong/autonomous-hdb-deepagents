from deepagents import create_deep_agent
from autonomous_hdb_deepagents.agent.llm import llm
from autonomous_hdb_deepagents.agent.pipeline import orchestrator_subagent

system_prompt = """
You are an HDB property finder. Always forward user queries to the orchestrator.
"""

deep_agent = create_deep_agent(
    model=llm,
    system_prompt=system_prompt,
    subagents=[orchestrator_subagent]
)
