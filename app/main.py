from fastapi import FastAPI
from app.db import init_db
from app.routers import connections, submissions
from app.routers import tables
from app.routers import d365_rows

app = FastAPI(title="lotuspetal-api-demo")

init_db()

@app.get("/")
def demo_root():
    return {
        "service": "lotuspetal-api-demo",
        "routes": {
            "test": "POST /connections/{tenant_id}/d365/test",
            "pull": "POST /connections/{tenant_id}/d365/pull",
            "export": "POST /submissions/{tenant_id}/d365/export",
            "tables": "GET /connectors/d365/tables?prefix={prefix}"
        }
    }

app.include_router(connections.router)
app.include_router(submissions.router)
app.include_router(tables.router)
app.include_router(d365_rows.router)