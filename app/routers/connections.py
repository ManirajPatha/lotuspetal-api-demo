from fastapi import APIRouter, HTTPException, Query
from app.services.integration_hub_client import (
    HubError,
    hub_test,
    hub_poll,
    hub_list_tables,
    hub_register_tables,
    hub_read_rows,
)

router = APIRouter()

@router.post("/connections/{tenant_id}/d365/test")
async def connection_test(tenant_id: str):
    try:
        return await hub_test(tenant_id)
    except HubError as e:
        raise HTTPException(status_code=e.status, detail=e.message)

@router.post("/connections/{tenant_id}/d365/pull")
async def connection_pull(tenant_id: str, body: dict | None = None):
    try:
        tables = (body or {}).get("tables")
        force_full = bool((body or {}).get("force_full"))
        return await hub_poll(tenant_id, tables=tables, force_full=force_full)
    except HubError as e:
        raise HTTPException(status_code=e.status, detail=e.message)

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