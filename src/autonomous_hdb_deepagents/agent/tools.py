import os
from toolbox_langchain import ToolboxClient

_toolbox_client = None

async def load_tools():
    global _toolbox_client

    if _toolbox_client is None:
        toolbox_url  = os.getenv("TOOLBOX_URL", "http://localhost:5000")
        print(f"[MCP] Connecting to Toolbox at: {toolbox_url}")
        _toolbox_client = ToolboxClient(toolbox_url)

    tools = await _toolbox_client.aload_toolset()
    print("[MCP] Loaded tools:", [t.name for t in tools])
    return {t.name: t for t in tools}