from fastapi import FastAPI, Request, HTTPException
import httpx

from app.db import init_db
from app.routers import connections, submissions
from app.routers import tables as tables_router   # keep one include only
from app.routers import d365_rows
from app.services.integration_hub_client import HUB  # if you use this elsewhere
from app.settings import settings

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
            "tables": "GET /connectors/d365/tables?prefix={prefix}",
            "tables_tenant": "GET /tenants/{tenant_id}/connectors/d365/tables?prefix={prefix}",
            "rows": "GET /connectors/d365/tables/{logical}/rows",
            "rows_tenant": "GET /tenants/{tenant_id}/connectors/d365/tables/{logical}/rows",
            "export_rows": "GET /connectors/d365/tables/{logical}/export?fmt=csv&route=local&top=100",
            "export_rows_tenant": "GET /tenants/{tenant_id}/connectors/d365/tables/{logical}/export?fmt=csv&route=local&top=100"
        }
    }

# ---------- LIST TABLES ----------

# Shortcut (no tenant in path) → use default DEMO_TENANT_ID internally
@app.get("/connectors/d365/tables")
async def demo_list_tables(request: Request):
    params = dict(request.query_params)
    async with httpx.AsyncClient(timeout=30) as cli:
        # Note: hub list-tables endpoint may not require tenant_id.
        r = await cli.get(f"{settings.HUB_URL}/connectors/d365/tables", params=params)
        r.raise_for_status()
        return r.json()

# Tenant-aware version (explicit tenant in path)
@app.get("/tenants/{tenant_id}/connectors/d365/tables")
async def demo_list_tables_tenant(tenant_id: str, request: Request):
    params = dict(request.query_params)
    async with httpx.AsyncClient(timeout=30) as cli:
        # If your hub list endpoint is tenantless, you can still call it directly:
        r = await cli.get(f"{settings.HUB_URL}/connectors/d365/tables", params=params)
        r.raise_for_status()
        return r.json()

# ---------- ROWS ----------

# Shortcut (no tenant in path) → uses default DEMO_TENANT_ID
@app.get("/connectors/d365/tables/{logical}/rows")
async def demo_rows_default(logical: str, request: Request):
    params = dict(request.query_params)
    tenant = settings.DEMO_TENANT_ID
    async with httpx.AsyncClient(timeout=30) as cli:
        r = await cli.get(
            f"{settings.HUB_URL}/tenants/{tenant}/connectors/d365/tables/{logical}/rows",
            params=params
        )
        r.raise_for_status()
        return r.json()

# Tenant-aware version (explicit tenant)
@app.get("/tenants/{tenant_id}/connectors/d365/tables/{logical}/rows")
async def demo_rows_tenant(tenant_id: str, logical: str, request: Request):
    params = dict(request.query_params)
    async with httpx.AsyncClient(timeout=30) as cli:
        r = await cli.get(
            f"{settings.HUB_URL}/tenants/{tenant_id}/connectors/d365/tables/{logical}/rows",
            params=params
        )
        r.raise_for_status()
        return r.json()

# ---------- EXPORT ----------

# Shortcut (no tenant) → uses default DEMO_TENANT_ID
@app.get("/connectors/d365/tables/{logical}/export")
async def demo_export_rows_default(logical: str, request: Request):
    params = dict(request.query_params)
    tenant = settings.DEMO_TENANT_ID
    # Implementation choice:
    #  A) forward to a hub export endpoint if you created one, or
    #  B) fetch rows from hub and build CSV in demo.
    # Here we forward to a hub "rows" then return CSV streamed back from hub
    async with httpx.AsyncClient(timeout=None) as cli:
        r = await cli.get(
            f"{settings.HUB_URL}/tenants/{tenant}/connectors/d365/tables/{logical}/rows",
            params=params
        )
        r.raise_for_status()
        data = r.json()
        # If you already have export-in-hub, replace above call with that hub export endpoint.
        return data

# Tenant-aware export
@app.get("/tenants/{tenant_id}/connectors/d365/tables/{logical}/export")
async def demo_export_rows_tenant(tenant_id: str, logical: str, request: Request):
    async with httpx.AsyncClient(timeout=60) as cli:
        r = await cli.get(
            f"{HUB}/tenants/{tenant_id}/connectors/d365/tables/{logical}/export",
            params=dict(request.query_params)
        )
        r.raise_for_status()
        return r.json()

# Routers you already have
app.include_router(connections.router)
app.include_router(submissions.router)
app.include_router(tables_router.router)
app.include_router(d365_rows.router)