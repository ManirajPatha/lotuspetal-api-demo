from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from app.services.integration_hub_client import HubError, hub_submit

router = APIRouter(prefix="/submissions", tags=["submissions"])

class AttachmentIn(BaseModel):
    name: str
    url: Optional[str] = None
    byte_size: Optional[int] = None
    content_type: Optional[str] = None

class SubmitRequest(BaseModel):
    submission_package_id: str = Field(..., min_length=3)
    answers: Dict[str, Any]
    attachments: List[AttachmentIn] = []
    route: str = "dryrun"  # email|sftp later

@router.post("/{tenant_id}/d365/export")
async def export_pack(tenant_id: str, body: SubmitRequest):
    try:
        return await hub_submit(tenant_id, body.model_dump())
    except HubError as e:
        raise HTTPException(status_code=e.status, detail={"msg": e.message, "upstream": e.payload})