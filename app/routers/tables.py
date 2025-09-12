# app/routers/tables.py
from typing import List
from fastapi import APIRouter, Query
from pydantic import BaseModel
from app.services.integration_hub_client import hub_export_table, hub_list_tables

router = APIRouter()

@router.get("/connectors/d365/tables")
async def list_tables(prefix: str | None = Query(None)):
    return await hub_list_tables(prefix)

@router.post("/connectors/d365/tables/{logical}/export")
async def export_table(logical: str, tenant_id: str = Query("demo"), fmt: str = Query("json"), route: str = Query("local"), select: str | None = Query(None), top: int = Query(1000)):
    return await hub_export_table(tenant_id, logical, fmt, route, select, top)

class RegisterTablesBody(BaseModel):
    tables: List[str]

@router.post("/connectors/d365/tables:register")
async def register_tables(body: RegisterTablesBody, tenant_id: str = Query("demo")):
    # simple proxy into the hub
    from app.services.integration_hub_client import hub_register_tables
    return await hub_register_tables(tenant_id, body.tables)

@router.get("/connectors/d365/tables/{logical}/rows")
async def read_rows(
    logical: str,
    tenant_id: str = Query("demo"),
    select: str | None = Query(None, description="Comma-separated columns"),
    top: int = Query(100, ge=1, le=5000),
):
    from app.services.integration_hub_client import hub_rows
    return await hub_rows(tenant_id, logical, select, top)