import asyncio
from langchain_core.messages import AIMessage, HumanMessage
from autonomous_hdb_deepagents.agent.deep_agent import deep_agent

def extract_final_message(result):
    msgs = result.get("messages")
    if isinstance(msgs, list):
        for m in reversed(msgs):
            if isinstance(m, AIMessage):
                return m.content
    return None

async def run_cli(query: str):
    result = await deep_agent.ainvoke({
        "messages": [HumanMessage(content=query)]
    })
    return extract_final_message(result) or "No output extracted."

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: uv run agent/cli.py \"your query\"")
        raise SystemExit

    query = sys.argv[1]

    async def main():
        output = await run_cli(query)
        print("\n=== FINAL RESPONSE ===\n")
        print(output)

    asyncio.run(main())
