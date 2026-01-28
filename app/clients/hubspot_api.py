# app/clients/hubspot_api.py
import httpx
from app.config import HUBSPOT_BASE_URL, HUBSPOT_TOKEN

HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}

async def create_contact(payload: dict) -> str:
    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.post(
            f"{HUBSPOT_BASE_URL}/crm/v3/objects/contacts",
            headers=HEADERS,
            json=payload
        )
        res.raise_for_status()
        return res.json()["id"]


async def create_ticket(payload: dict) -> str:
    """
    Create a ticket in HubSpot and return ticket ID
    """

    url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/tickets"

    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.post(
            url,
            headers=HEADERS,
            json=payload   # 🔥 SEND FULL PAYLOAD
        )

        if res.status_code >= 400:
            print("HUBSPOT ERROR:", res.status_code, res.text)

        if res.status_code == 409:
            print("Ticket already exists")
            return None

        res.raise_for_status()
        return res.json()["id"]
