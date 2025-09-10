# app/services/integration_hub_client.py
import os
import httpx
from typing import Any, Dict

HUB = os.getenv("INTEGRATION_HUB_BASE", "http://localhost:8080")
HUB_TOKEN = os.getenv("INTEGRATION_HUB_TOKEN")  # optional shared secret
TIMEOUT = 30


class HubError(Exception):
    def __init__(self, status: int, message: str, payload: dict | None = None):
        self.status = status
        self.message = message
        self.payload = payload or {}
        super().__init__(f"{status} {message}")


def _headers() -> Dict[str, str]:
    h = {"Accept": "application/json"}
    if HUB_TOKEN:
        h["Authorization"] = f"Bearer {HUB_TOKEN}"
    return h


async def _post(path: str, json: dict | None = None) -> Dict[str, Any]:
    url = f"{HUB}{path}"
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, headers=_headers()) as cli:
            r = await cli.post(url, json=json)
        if r.status_code >= 400:
            try:
                details = r.json()
            except Exception:
                details = {}
            raise HubError(r.status_code, details.get("detail") or r.text, details)
        return r.json()
    except httpx.ConnectError as e:
        raise HubError(502, f"Cannot reach integration-hub at {url}") from e
    except httpx.ReadTimeout as e:
        raise HubError(504, f"Integration-hub timed out at {url}") from e


async def _get(path: str, params: dict | None = None) -> Dict[str, Any]:
    url = f"{HUB}{path}"
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, headers=_headers()) as cli:
            r = await cli.get(url, params=params)
        if r.status_code >= 400:
            try:
                details = r.json()
            except Exception:
                details = {}
            raise HubError(r.status_code, details.get("detail") or r.text, details)
        return r.json()
    except httpx.ConnectError as e:
        raise HubError(502, f"Cannot reach integration-hub at {url}") from e
    except httpx.ReadTimeout as e:
        raise HubError(504, f"Integration-hub timed out at {url}") from e


# ---- public client functions ----
async def hub_test(tenant_id: str) -> Dict[str, Any]:
    return await _post(f"/tenants/{tenant_id}/connectors/d365:test")


async def hub_poll(
    tenant_id: str,
    tables: list[str] | None = None,
    force_full: bool = False,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    if tables:
        payload["tables"] = tables
    if force_full:
        payload["force_full"] = True
    return await _post(f"/tenants/{tenant_id}/connectors/d365:poll", json=payload or None)


async def hub_submit(tenant_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    return await _post(f"/tenants/{tenant_id}/connectors/d365/submit", json=payload)


async def hub_list_tables(prefix: str | None = None):
    params = {"prefix": prefix} if prefix else {}
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as cli:
        r = await cli.get(f"{HUB}/connectors/d365/tables", params=params)
        if r.status_code >= 400:
            # bubble up hub error details for debugging
            return {"ok": False, "status": r.status_code, "error": r.text}
        return r.json()


async def hub_register_tables(tenant_id: str, tables: list[str]) -> Dict[str, Any]:
    return await _post(f"/tenants/{tenant_id}/connectors/d365/tables:register",
                       json={"tables": tables})


async def hub_read_rows(tenant_id: str, table: str, top: int = 50, skip: int = 0) -> Dict[str, Any]:
    return await _get(f"/tenants/{tenant_id}/connectors/d365/tables/{table}/rows",
                      params={"top": top, "skip": skip})


# Optional explicit export list (avoids name confusion)
__all__ = [
    "HubError",
    "hub_test",
    "hub_poll",
    "hub_submit",
    "hub_list_tables",
    "hub_register_tables",
    "hub_read_rows",
]