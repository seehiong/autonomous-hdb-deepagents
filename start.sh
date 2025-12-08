#!/bin/bash
set -e

echo "🚀 Starting Toolbox on :5000"
/usr/local/bin/toolbox --tools-file tools.yaml --ui &

echo "🚀 Starting FastAPI on :8000"
uv run uvicorn autonomous_hdb_deepagents.api.api_server:app --host 0.0.0.0 --port 8000 &

echo "🎨 Starting Gradio UI on :7860"
uv run python -m autonomous_hdb_deepagents.ui.gradio_app