import os
import sys

# ---------------------------------------
# FORCE PYTHONPATH TO INCLUDE ./src
# ---------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))          # .../api
ROOT = os.path.abspath(os.path.join(BASE, ".."))           # .../autonomous-hdb-deepagents
SRC = os.path.join(ROOT, "src")

sys.path.insert(0, SRC)

print(">>> PYTHONPATH injected:", sys.path)

# ---------------------------------------
# Run Uvicorn with RELOAD
# ---------------------------------------
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "autonomous_hdb_deepagents.api.api_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[SRC, ROOT],
    )
