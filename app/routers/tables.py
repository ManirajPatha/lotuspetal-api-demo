# app/routers/tables.py
from fastapi import APIRouter, Query
from app.services.integration_hub_client import hub_export_table, hub_list_tables

router = APIRouter()

@router.get("/connectors/d365/tables")
async def list_tables(prefix: str | None = Query(None)):
    return await hub_list_tables(prefix)

@router.post("/connectors/d365/tables/{logical}/export")
async def export_table(logical: str, tenant_id: str = Query("demo"), fmt: str = Query("json"), route: str = Query("local"), select: str | None = Query(None), top: int = Query(1000)):
    return await hub_export_table(tenant_id, logical, fmt, route, select, top)
