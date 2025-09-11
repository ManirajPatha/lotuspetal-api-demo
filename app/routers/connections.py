import os
from fastapi import APIRouter, HTTPException, Query
import httpx
from app.services.integration_hub_client import (
    HubError,
    hub_test,
    hub_poll,
    hub_list_tables,
    hub_register_tables,
    hub_read_rows,
)

router = APIRouter()
HUB_URL = os.getenv("HUB_URL", "http://localhost:8080")

@router.post("/connections/{tenant_id}/d365/test")
async def connection_test(tenant_id: str):
    try:
        return await hub_test(tenant_id)
    except HubError as e:
        raise HTTPException(status_code=e.status, detail=e.message)

@router.post("/connections/{tenant}/d365/pull")
async def pull_d365(
    tenant: str,
    force_full: bool = Query(False),
    limit_pages: int = Query(2, ge=1, le=50),
    max_records: int | None = Query(None, ge=1),
    since_iso: str | None = Query(None),
):
    """
    Demo proxy that forwards to the hub poll endpoint.
    Supports query params like ?force_full=true&limit_pages=5
    """
    params = {
        "force_full": str(force_full).lower(),
        "limit_pages": str(limit_pages),
    }
    if max_records is not None:
        params["max_records"] = str(max_records)
    if since_iso:
        params["since_iso"] = since_iso

    url = f"{HUB_URL}/tenants/{tenant}/connectors/d365:poll"
    async with httpx.AsyncClient(timeout=60) as cli:
        r = await cli.post(url, params=params, json={})
        r.raise_for_status()
        return r.json()

@router.get("/connections/d365/tables")
async def list_tables(prefix: str | None = None):
    try:
        return await hub_list_tables(prefix)
    except HubError as e:
        raise HTTPException(status_code=e.status, detail=e.message)

@router.post("/connections/{tenant_id}/d365/tables/register")
async def register_tables(tenant_id: str, body: dict):
    try:
        tables = body.get("tables") or []
        return await hub_register_tables(tenant_id, tables)
    except HubError as e:
        raise HTTPException(status_code=e.status, detail=e.message)

@router.get("/connections/{tenant_id}/d365/tables/{table}/rows")
async def get_rows(tenant_id: str, table: str, top: int = Query(50, ge=1, le=500), skip: int = Query(0, ge=0)):
    try:
        return await hub_read_rows(tenant_id, table, top=top, skip=skip)
    except HubError as e:
        raise HTTPException(status_code=e.status, detail=e.message)