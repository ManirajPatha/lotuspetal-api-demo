# app/clients/hub_client.py
import os
import httpx

HUB_URL = os.getenv("HUB_URL", "http://localhost:8080")
HUB_SHARED_TOKEN = os.getenv("HUB_SHARED_TOKEN")  # optional shared secret

def _headers():
    h = {"Content-Type": "application/json"}
    if HUB_SHARED_TOKEN:
        h["X-Internal-Token"] = HUB_SHARED_TOKEN   # must match hub if you secured it
    return h

async def hub_register_tables(tenant: str, tables: list[str]) -> dict:
    url = f"{HUB_URL}/tenants/{tenant}/connectors/d365/tables:register"
    async with httpx.AsyncClient(timeout=30) as cli:
        r = await cli.post(url, json={"tables": tables}, headers=_headers())
        r.raise_for_status()
        return r.json()

async def hub_list_tables(prefix: str | None = None) -> dict:
    url = f"{HUB_URL}/connectors/d365/tables"
    params = {"prefix": prefix} if prefix else None
    async with httpx.AsyncClient(timeout=30) as cli:
        r = await cli.get(url, params=params, headers=_headers())
        r.raise_for_status()
        return r.json()

async def hub_rows(tenant: str, logical: str, top: int = 50) -> dict:
    url = f"{HUB_URL}/tenants/{tenant}/connectors/d365/tables/{logical}/rows"
    params = {"$top": top}
    async with httpx.AsyncClient(timeout=30) as cli:
        r = await cli.get(url, params=params, headers=_headers())
        r.raise_for_status()
        return r.json()

async def hub_post(path: str, json: dict):
    async with httpx.AsyncClient(timeout=30) as cli:
        r = await cli.post(f"{HUB_URL}{path}", json=json)
        r.raise_for_status()
        return r.json()

async def hub_get(path: str, params: dict = None):
    async with httpx.AsyncClient(timeout=30) as cli:
        r = await cli.get(f"{HUB_URL}{path}", params=params)
        r.raise_for_status()
        return r.json()