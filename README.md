# 🏢 Autonomous HDB DeepAgents

**A Multi-Agent Geospatial + Resale-Price Intelligence System for Singapore HDB Search**

This project provides an **autonomous DeepAgent pipeline** that processes natural-language queries like:

- "Find flats near Bukit Batok MRT"
- "Show me 4-room flats in Toa Payoh under 500k"
- "HDB near MRT within 600m with good value picks"

and turns them into:
1. Intent extraction (town, MRT station, flat type, max price, radius)
2. MRT resolver (maps MRT → nearest HDB planning area via MCP SQL tool)
3. Resale flat retrieval via MCP PostgreSQL tools
4. Geospatial enrichment via MCP geospatial-query tools
5. Distance formatting and correction
6. LLM-powered summaries

All orchestrated end-to-end via **DeepAgents + LangGraph**.

---

# 🌳 Project Structure

```text
autonomous-hdb-deepagents/
│
├── pyproject.toml
├── README.md
│
├── src/
│   └── autonomous_hdb_deepagents/
│       │   __init__.py
│       │
│       ├── agent/
│       │   ├── __init__.py
│       │   ├── cli.py                 # CLI entrypoint (uv run -m autonomous_hdb_deepagents.agent.cli)
│       │   ├── deep_agent.py          # DeepAgent factory + LangGraph orchestration pipeline
│       │   ├── intent.py              # LLM-powered intent extraction
│       │   ├── mrt_resolver.py        # MRT → HDB-town resolver (MCP SQL)
│       │   ├── resale.py              # HDB resale SQL query node
│       │   ├── mrt.py                 # Geospatial enrichment node
│       │   ├── summary.py             # LLM summary generation node
│       │   ├── state.py               # PipelineState (Pydantic)
│       │   ├── tools.py               # MCP Toolbox loader + caching
│       │   └── llm.py                 # Shared OpenRouter LLM instance (ChatOpenAI)
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   ├── api_server.py          # FastAPI server providing /health + /query
│       │   └── api_server_launch.py   # Standalone launcher with controlled PYTHONPATH
│       │
│       └── ui/
│           ├── __init__.py
│           └── gradio_app.py          # Gradio full-screen chat UI with sample questions
│
├── notebook/
│   ├── deepagents-multi-agent.ipynb
│   ├── deepagents-sub-agent.ipynb
│   ├── deepagents-custom-model.ipynb
│   └── data-ingestion/
│       ├── hdb-existing-building.ipynb
│       ├── hdb-property-info.ipynb
│       ├── lta-mrt-exits.ipynb
│       ├── moe-sg-schools.ipynb
│       ├── npark-parks.ipynb
│       └── onemap-geocoding-cache.ipynb
│
├── db/
│   └── init/                  # Schema + ingestion SQL
│       ├── 00_schema.sql
│       ├── 01_load_data.sql
│       └── data/              # Preprocessed CSV/GeoJSON from notebooks
│          └── *.csv
│
├── tools.yaml
├── start.sh
├── Dockerfile
└── docker-compose.yml
```

# 📚 Data Ingestion & Processing Notebooks

This project includes a set of **fully reproducible data-ingestion notebooks** located under:
```bash
notebook/data-ingestion/
```

These notebooks document how each official dataset from **data.gov.sg**, **LTA**, **MOE**, **NParks**, and **OneMap** was:
1. Downloaded (CSV/GeoJSON/API)
2. Cleaned
3. Transformed and normalized
4. Converted into SQL-ready tables
5. Inserted into PostgreSQL

These notebooks serve as **transparent documentation** of all preprocessing logic and allow anyone to **rebuild the entire database from scratch**.

## Included Notebooks

| Notebook                      | Purpose                                                                 |
|-------------------------------|-------------------------------------------------------------------------|
| hdb-existing-building.ipynb   | Extracts and processes HDB existing building geometries and metadata.   |
| hdb-property-info.ipynb       | Loads HDB property information dataset and formats it for SQL ingestion.|
| lta-mrt-exits.ipynb           | Processes official LTA MRT exit GeoJSON and creates table-ready geometries. |
| moe-sg-schools.ipynb          | Processes MOE schools master list (locations, categories, addresses).   |
| npark-parks.ipynb             | Loads NParks parks boundaries/points and normalizes names + coordinates.|
| onemap-geocoding-cache.ipynb  | Generates and caches OneMap coordinate lookups to speed up ingestion.   |

# ⚙️ Installation

## 1. Install dependencies

```powershell
uv sync
```

## 2. Install in editable mode
```powershell
uv add --dev --editable .
```

Now you can import:
```python
import autonomous_hdb_deepagents
```

# 🚀 Running the CLI Agent

## Recommended (module form)
```powershell
uv run -m autonomous_hdb_deepagents.agent.cli "Find flats near Bukit Panjang MRT"
```

## Or direct script path:
```powershell
uv run src/autonomous_hdb_deepagents/agent/cli.py "Find flats near Bukit Panjang MRT"
```

## Example Output
```text
[INTENT] Parsed intent → {'town': None, 'mrt_station': 'Bukit Panjang', 'flat_type': None, 'max_price': None, 'mrt_radius': None}
[MRT-RESOLVE] Resolving MRT station: Bukit Panjang
[MRT-RESOLVE] BP → BUKIT PANJANG
[RESALE] Fetching 4 ROOM in BUKIT PANJANG <= 600000...
[RESALE] Retrieved 30 flats
[MRT] Enriching 30 flats (radius=800)
[MRT] Example: BT PANJANG RING RD → BANKIT LRT STATION (162m)
[SUMMARY] Summarizing 30 flats

=== FINAL RESPONSE ===

### **Flats Near Bukit Panjang MRT: Summary**
...
```

# ⚡ Pipeline Overview (DeepAgents + LangGraph)

## 1️⃣ intent_node

Extracts:
- town
- mrt_station
- flat_type
- max_price
- mrt_radius

## 2️⃣ mrt_resolve_node

- Calls MCP `get-mrt-towns`
- Resolves `"BB" → "BUKIT BATOK"`
- Auto-sets `town` if missing

## 3️⃣ resale_node

Uses MCP SQL tool `list-hdb-flats` to fetch:
- block
- street
- price
- coordinates

Defaults:
- flat_type="4 ROOM"
- max_price=600000
- town="TOA PAYOH" (fallback)

## 4️⃣ mrt_node (Geospatial Enrichment)

Uses MCP:
```text
geospatial-query
```

Adds:
- nearest mrt
- distance raw
- formatted distance (e.g., `"367m"`, `"1.1km"`)

Smart unit normalization
- degrees → meters
- km → meters
- meters → meters

## 5️⃣ summary_node

LLM produces:
- price range
- closest flats
- best value picks
- meaningful insights

## 6️⃣ DeepAgent Orchestrator

Graph:
```text
intent → mrt_resolve → resale → mrt → summary → END
```

# 🌐 FastAPI HTTP Server

The API lives under:
```powershell
src/autonomous_hdb_deepagents/api/
```

Start server:
```powershell
uv run python src/autonomous_hdb_deepagents/api/api_server_launch.py
```

Health check
```powershell
curl http://localhost:8000/health
```

Query endpoint (PowerShell-safe):
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/query" -Method Post `
  -Body '{"query":"Find flats near Bukit Batok MRT"}' `
  -ContentType "application/json"

# Sample Outputs
# response
# --------
# ### HDB Flats Near Bukit Batok MRT  …
```

# 🖥️ Web UI (Gradio) — Natural-Language Chat Interface

The project includes a **fully interactive Gradio chat UI** for your autonomous HDB DeepAgent.
This UI is separate from the FastAPI server and can run independently.

## ✔ Features

- Full-screen responsive chat layout
- Sample question buttons
- Built-in DeepAgent orchestration
- Works 100% locally — no external server needed
- Runs in its own process

## 🚀 Running the Gradio UI

From project root:
```powershell
uv run python src/autonomous_hdb_deepagents/ui/gradio_app.py
```

You will see:
```text
* Running on local URL:  http://0.0.0.0:7860
```

Open this in your browser:
```html
➡️ http://localhost:7860
```

# 🔧 Required MCP Tools

You must have these MCP tools available:

## 1. Resale lookup
```text
list-hdb-flats
```

## MRT → HDB town mapping
```text
get-mrt-towns
```

## Geospatial nearest-mrt search
```text
geospatial-query
```

Loaded dynamically via:
```python
ToolboxClient("http://127.0.0.1:5000")
```

# 🧠 Design Principles
  
✔ Fully modular agent layers  
✔ Clear separation of concerns  
✔ State management via Pydantic  
✔ LangGraph deterministic pipeline  
✔ DeepAgent orchestration wrapper  
✔ Supports CLI, server, and notebook workflows  
✔ Clean Python package for reuse  

# 🚀 Running Autonomous HDB DeepAgents with Docker

This section explains how to run the entire system—**database, toolbox, backend API, and Gradio UI**—using docker-compose.

The final architecture looks like this:

┌──────────────────────────┐
│      Docker Host         │
│                          │
│  ┌──────────────┐        │
│  │  PostgreSQL  │◄───────┼── Loads HDB resale + MRT data on first run
│  └──────────────┘        │
│            ▲             │
│            │             │
│  ┌──────────────┐        │
│  │  Toolbox     │◄───────┼── Local MCP agent for structured SQL/Geo tools
│  └──────────────┘        │
│            ▲             │
│            │             │
│  ┌──────────────┐        │
│  │ Backend API  │        │
│  │ (FastAPI)    │        │
│  └──────────────┘        │
│            ▲             │
│            │             │
│  ┌──────────────┐        │
│  │  Gradio UI   │        │
│  └──────────────┘        │
└──────────────────────────┘

## 🐘 1. Postgres Setup (Auto-loaded Data)

On **first run**, Postgres will:
  1. Create hdb_database
  2. Install PostGIS
  3. Create all required tables
  4. Auto-ingest all CSVs

## 🧰 2. Toolbox Setup (Local MCP Server)

The Dockerfile:
- Downloads the toolbox binary
- Runs it on port 5000
- Uses `tools.yaml` inside the container

All agents call Toolbox via:
```bash
TOOLBOX_URL=http://localhost:5000
```

## 🖥️ 3. Backend (FastAPI + Gradio UI)

The backend container exposes:

| Component   | Port |
|-------------|------|
| FastAPI     | 8000 |
| Gradio UI   | 7860 |
| Toolbox API | 5000 |

The start.sh runs these in parallel:
1. Toolbox
2. FastAPI
3. Gradio

## ▶️ 4. Run Everything

Start environment:
```powershell
docker-compose up
```

After successful boot:
- Gradio UI → http://localhost:7860
- FastAPI docs → http://localhost:8000/docs

## ♻️ 5. Reset Everything (including database)

```powershell
docker-compose down -v
```

This clears Postgres volumes and triggers CSV reload on next start.

## 📌 6. Confirming System Works

### In UI:

You should be able to run:
```text
Find cheapest 5-room flats near Punggol MRT under 600k
```

# 📊 Data Sources & Citations

This project uses publicly available datasets from Singapore’s Housing & Development Board (HDB) provided via **data.gov.sg** under the Singapore Open Data Licence.

Please cite the following datasets if you use this project in research, reports, publications, or derivative works:

## APA Citations

- Housing & Development Board. (2016). Resale Flat Prices (Based on Approval Date), 1990–1999 (2024) [Dataset]. data.gov.sg.
Retrieved December 7, 2025, from https://data.gov.sg/datasets/d_ebc5ab87086db484f88045b47411ebc5/view

- Housing & Development Board. (2016). Resale Flat Prices (Based on Approval Date), 2000–Feb 2012 (2024) [Dataset]. data.gov.sg.
Retrieved December 7, 2025, from https://data.gov.sg/datasets/d_43f493c6c50d54243cc1eab0df142d6a/view

- Housing & Development Board. (2016). Resale Flat Prices (Based on Registration Date), From Mar 2012 to Dec 2014 (2024) [Dataset]. data.gov.sg.
Retrieved December 7, 2025, from https://data.gov.sg/datasets/d_2d5ff9ea31397b66239f245f57751537/view

- Housing & Development Board. (2017). Resale Flat Prices (Based on Registration Date), From Jan 2015 to Dec 2016 (2024) [Dataset]. data.gov.sg.
Retrieved December 7, 2025, from https://data.gov.sg/datasets/d_ea9ed51da2787afaf8e51f827c304208/view

- Housing & Development Board. (2021). Resale flat prices based on registration date from Jan-2017 onwards (2025) [Dataset]. data.gov.sg.
Retrieved December 7, 2025, from https://data.gov.sg/datasets/d_8b84c4ee58e3cfc0ece0d773c8ca6abc/view

- Housing & Development Board. (2018). HDB Property Information (2025) [Dataset]. data.gov.sg. Retrieved December 7, 2025 from https://data.gov.sg/datasets/d_17f5382f26140b1fdae0ba2ef6239d2f/view

- National Parks Board. (2023). Parks (2025) [Dataset]. data.gov.sg. Retrieved December 7, 2025 from https://data.gov.sg/datasets/d_0542d48f0991541706b58059381a6eca/view

- Ministry of Education. (2017). General information of schools (2025) [Dataset]. data.gov.sg. Retrieved December 7, 2025 from https://data.gov.sg/datasets/d_688b934f82c1059ed0a6993d2a829089/view

- Land Transport Authority. (2019). LTA MRT Station Exit (GEOJSON) (2025) [Dataset]. data.gov.sg. Retrieved December 7, 2025 from https://data.gov.sg/datasets/d_b39d3a0871985372d7e1637193335da5/view

## 📘 Notes on Dataset Usage

- Data is provided under the **Singapore Open Data Licence**.
- Users are permitted to **reuse, modify, and redistribute** these datasets.
- Proper **attribution must be given**, as included above.
- This project aggregates, normalizes, and enriches the datasets into a PostgreSQL schema suitable for agent-based geospatial queries.