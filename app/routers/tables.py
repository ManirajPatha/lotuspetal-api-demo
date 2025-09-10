# app/routers/tables.py
from fastapi import APIRouter, Query
from app.services.integration_hub_client import hub_list_tables

router = APIRouter()

@router.get("/connectors/d365/tables")
async def list_tables(prefix: str | None = Query(None)):
    return await hub_list_tables(prefix)
