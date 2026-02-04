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


async def fetch_hubspot_tickets(limit: int = 50):
    url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/tickets"

    params = {
        "limit": limit,
        "properties": [
            "subject",
            "content",
            "hs_ticket_priority",
            "hs_pipeline_stage",
            "createdate"
        ]
    }

    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.get(url, headers=HEADERS, params=params)
        res.raise_for_status()
        return res.json()
    

async def update_ticket(hubspot_ticket_id: str, properties: dict):
    """
    Update an existing HubSpot ticket
    """
    url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/tickets/{hubspot_ticket_id}"

    payload = {
        "properties": properties
    }

    async with httpx.AsyncClient(timeout=20) as client:
        res = await client.patch(url, headers=HEADERS, json=payload)

        if res.status_code >= 400:
            print("HUBSPOT UPDATE ERROR:", res.status_code, res.text)

        res.raise_for_status()
        return res.json()
    
async def delete_ticket(hubspot_ticket_id: str):
    """
    Delete a ticket from HubSpot
    """
    url = f"{HUBSPOT_BASE_URL}/crm/v3/objects/tickets/{hubspot_ticket_id}"

    async with httpx.AsyncClient(timeout=15) as client:
        res = await client.delete(url, headers=HEADERS)

        if res.status_code >= 400:
            print("HUBSPOT DELETE ERROR:", res.status_code, res.text)

        res.raise_for_status()
        return True