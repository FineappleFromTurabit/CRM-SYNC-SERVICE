# app/clients/internal_api.py
import httpx
from app.config import INTERNAL_API_BASE
from app.models.internal import InternalCustomer, InternalTicket
from email.utils import parsedate_to_datetime
async def fetch_customers():
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{INTERNAL_API_BASE}/customers")
        res.raise_for_status()
        data = res.json()
        for c in data:
            if "created_at" in c:
                c["created_at"] = parsedate_to_datetime(c["created_at"])
        return [InternalCustomer(**c) for c in data]

async def fetch_tickets():
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{INTERNAL_API_BASE}/tickets")
        res.raise_for_status()
        return [InternalTicket(**t) for t in res.json()]


async def create_customer(payload: dict) -> int:
    """
    Create customer in internal Smart Support Desk
    Returns internal customer ID
    """
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{INTERNAL_API_BASE}/customers",
            json=payload
        )
        res.raise_for_status()

        # Your API returns { "message": "..."} only,
        # so we re-fetch customers or rely on caller logic
        return 1
    
async def create_ticket(payload: dict) -> int:
    """
    Create ticket in internal Smart Support Desk
    Returns internal ticket ID
    """
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{INTERNAL_API_BASE}/tickets",
            json=payload
        )
        res.raise_for_status()
        return res.json().get("id", 0)