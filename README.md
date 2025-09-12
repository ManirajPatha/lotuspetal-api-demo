
---

# 📗 lotuspetal-api-demo — README.md

# LotusPetal API Demo (calls integration-hub)

This is a **demo app** that presents simple product-style endpoints and forwards the work to the **integration-hub**. Use it to validate:
- D365 connectivity (whoami)
- Table discovery & registration (proxied)
- Polling (proxied)
- Reading rows
- Exporting data (CSV/ZIP via hub)

> In production, your real lotuspetal-api would call the hub in the same way.

---

## Requirements

- Python 3.11+
- Running **integration-hub** (default: `http://localhost:8080`)

---

## Setup

1) Clone & create virtualenv
```powershell
git clone <your-repo-url> lotuspetal-api-demo
cd lotuspetal-api-demo
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

2. Create .env

HUB_URL=http://localhost:8080
# Optional: if hub expects an internal token
HUB_SHARED_TOKEN=<same-token-as-hub>

3. Run

uvicorn app.main:app --reload --port 8000

4. Verify

Open http://localhost:8000/ → should list demo endpoints

Key Demo Endpoints

Most endpoints proxy to the hub. Adjust if your code names differ.

Root / Health

GET / → service + endpoints JSON

Connection Tests

POST /connections/demo/d365/test
(demo → hub → D365 WhoAmI)

Table Discovery & Registration (proxied)

GET /connectors/d365/tables?prefix=cr83d_
POST /connectors/d365/tables:register
{ "tables": ["cr83d_sourcingevent", "cr83d_school"] }

Poll (proxied)
POST /connections/demo/d365/pull?force_full=true

Read Rows (direct convenience to hub)

GET /connectors/d365/tables/{logical}/rows
Example: /connectors/d365/tables/cr83d_employee/rows

Export Examples

Submission export (ZIP via hub)
POST /submissions/demo/d365/export
{
  "submission_package_id": "mani123",
  "route": "local",
  "answers": { "event_id": "....", "supplier_name": "..." },
  "attachments": []
}

Expect: ok:true, location:"local:...\\out\\<tenant>\\submission_mani123.zip"

Table export (CSV)
GET /connectors/d365/tables/account/export?fmt=csv&route=local&top=100

End-to-End Demo Script

Start hub (8080) then demo (8000).
POST /connections/demo/d365/test → WhoAmI ok.
GET /connectors/d365/tables?prefix=cr83d_ → list your custom tables.
POST /connectors/d365/tables:register → choose tables to monitor.
POST /connections/demo/d365/pull?force_full=true → ingest data.
GET /connectors/d365/tables/<logical>/rows → verify real rows.
GET /submissions/demo/d365/export → ZIP created under hub’s SUBMISSION_DIR.

How it connects to the hub

Uses HUB_URL from .env to call the hub endpoints.
Optionally sends X-Internal-Token: <HUB_SHARED_TOKEN> header if enabled.
Keeps the demo thin; all vendor logic lives in the hub.

Troubleshooting

404 Not Found: confirm the route exists in the demo; some admin routes only exist on the hub (8080).
Hub errors: check the hub logs (PowerShell window running on port 8080).
Exports not found: remember export files are saved by the hub, not the demo; check hub’s SUBMISSION_DIR.

.gitignore

.venv/
__pycache__/
*.pyc
.env
*.zip
out/
*.log
