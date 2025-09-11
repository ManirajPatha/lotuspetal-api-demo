from fastapi import APIRouter, Query, HTTPException
from app.services.integration_hub_client import hub_get_rows
import httpx

router = APIRouter()

@router.get("/tenants/{tenant}/connectors/d365/tables/{logical}/rows")
async def get_rows(
    tenant: str,
    logical: str,
    top: int | None = Query(50, ge=1, le=5000),  # default 50 for safety
    select: str | None = Query(None, alias="$select"),
    orderby: str | None = Query(None, alias="$orderby"),
    filter_: str | None = Query(None, alias="$filter"),
):
    try:
        return await hub_get_rows(tenant, logical, top, select, orderby, filter_)
    except httpx.ReadTimeout:
        raise HTTPException(status_code=504, detail="Gateway timeout calling integration-hub")
    except httpx.HTTPStatusError as e:
        # bubble up hub error info
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
