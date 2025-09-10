from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
import os

DB_URL = os.getenv("LP_DB_URL", "sqlite:///lotuspetal.db")
engine = create_engine(DB_URL, echo=False)

class SourcingEvent(SQLModel, table=True):
    id: str = Field(primary_key=True)
    tenant_id: str
    title: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    due_at: Optional[str] = None
    platform: str = "d365"

def init_db():
    SQLModel.metadata.create_all(engine)

def upsert_events(events: list[dict]):
    with Session(engine) as s:
        for ev in events:
            obj = s.get(SourcingEvent, ev["id"])
            if obj:
                obj.title = ev.get("title")
                obj.status = ev.get("status")
                obj.created_at = ev.get("created_at")
                obj.due_at = ev.get("due_at")
                obj.tenant_id = ev.get("tenant_id")
            else:
                s.add(SourcingEvent(**ev))
        s.commit()

def list_events(tenant_id: str) -> list[SourcingEvent]:
    with Session(engine) as s:
        stmt = select(SourcingEvent).where(SourcingEvent.tenant_id == tenant_id)
        return list(s.exec(stmt))