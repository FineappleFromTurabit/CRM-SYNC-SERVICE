from fastapi import HTTPException
import requests
import httpx
from app.clients.internal_api import fetch_tickets
from app.clients.hubspot_api import create_ticket, delete_ticket, fetch_hubspot_tickets, update_ticket
from app.redis_client import get_value, set_value
from app.config import HUBSPOT_BASE_URL, HUBSPOT_TOKEN, INTERNAL_API_BASE

HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}
# =========================
# Sync ALL tickets
# =========================
async def sync_tickets():
    tickets = await fetch_tickets()
    results = []

    for t in tickets:
        # Skip already synced tickets
        existing = await get_value(f"ticket:{t.id}")
        if existing:
            results.append({
                "internal_id": t.id,
                "hubspot_id": existing,
                
                "reason": "Already synced"
            })
            continue

        # Customer mapping check
        hubspot_customer_id = await get_value(f"customer:{t.customer_id}")
        if not hubspot_customer_id:
            results.append({
                "internal_id": t.id,
                "status": "SKIPPED",
                "reason": "Customer not synced"
            })
            continue
        
        payload = {
            "properties": {
                "subject": t.title,
                "content": t.description or "",
                "hs_ticket_priority": t.priority.upper(),
                "hs_pipeline_stage": t.status.upper(),
                "hs_pipeline": "0",
                # "hs_pipeline_stage": "1"
            },
            "associations": [
                {
                    "to": {"id": hubspot_customer_id},
                    "types": [
                        {
                            "associationCategory": "HUBSPOT_DEFINED",
                            "associationTypeId": 16
                        }
                    ]
                }
            ]
        }

        hubspot_ticket_id = await create_ticket(payload)
        await set_value(f"ticket:{t.id}", hubspot_ticket_id)

        results.append({
            "internal_id": t.id,
            "hubspot_id": hubspot_ticket_id,
            "status": "SYNCED"
        })

    return {
        "synced": len([r for r in results if r["status"] == "SYNCED"]),
        "results": results
    }


# =========================
# Sync SINGLE ticket
# =========================
async def sync_single_ticket(ticket_id: int):
    tickets = await fetch_tickets()
    ticket = next((t for t in tickets if t.id == ticket_id), None)

    if not ticket:
        return {"status": "NOT_FOUND"}

    # Already synced?
    existing = await get_value(f"ticket:{ticket.id}")
    if existing:
        return {
            "internal_id": ticket.id,
            "hubspot_id": existing,
            "status": "ALREADY_SYNCED"
        }

    # Customer mapping check
    hubspot_customer_id = await get_value(f"customer:{ticket.customer_id}")
    if not hubspot_customer_id:
        return {
            "internal_id": ticket.id,
            "status": "SKIPPED",
            "reason": "Customer not synced"
        }

    payload = {
        "properties": {
            "subject": ticket.title,
            "content": ticket.description or "",
            "hs_ticket_priority": ticket.priority.upper(),
            "hs_pipeline_stage": 1,
            "hs_pipeline": "0",
            # "hs_pipeline_stage": "1"
        },
        "associations": [
            {
                "to": {"id": hubspot_customer_id},
                "types": [
                    {
                        "associationCategory": "HUBSPOT_DEFINED",
                        "associationTypeId": 16
                    }
                ]
            }
        ]
    }

    hubspot_ticket_id = await create_ticket(payload)
    await set_value(f"ticket:{ticket.id}", hubspot_ticket_id)

    return {
        "internal_id": ticket.id,
        "hubspot_id": hubspot_ticket_id,
        "status": "SYNCED"
    }
async def sync_single_ticket_direct(ticket: dict):

    customer_mail = ticket.get("customer_mail")

    # ---------------- CUSTOMER LOOKUP ----------------
    try:

        
        res =requests.get(
            f"{INTERNAL_API_BASE}/customers/mail",
            params={"customer_mail": customer_mail}
        )


        res.raise_for_status()
        customers = res.json()

    except Exception as e:
        return {
            "status": "FAILED",
            "reason": f"Customer lookup failed: {e}"
        }


    if not customers:
        return {
            "status": "SKIPPED",
            "reason": "Customer not found"
        }

    customer_id = customers[0].get("id")

    if not customer_id:
        return {
            "status": "FAILED",
            "reason": "Customer ID missing"
        }

    # ---------------- REDIS MAPPING ----------------
    hubspot_customer_id = await get_value(f"customer:{customer_id}")

    if not hubspot_customer_id:
        return {
            "status": "SKIPPED",
            "reason": "Customer not synced to HubSpot"
        }

    # ---------------- BUILD HUBSPOT PAYLOAD ----------------
    properties = {
        "subject": ticket.get("title"),
        "content": ticket.get("description") or "",
        "hs_pipeline_stage": "1",   # MUST be string
        "hs_pipeline": "0",
    }

    if ticket.get("priority"):
        properties["hs_ticket_priority"] = ticket["priority"].upper()

    payload = {
        "properties": properties,
        "associations": [
            {
                "to": {"id": hubspot_customer_id},
                "types": [
                    {
                        "associationCategory": "HUBSPOT_DEFINED",
                        "associationTypeId": 16
                    }
                ]
            }
        ]
    }


    # ---------------- HUBSPOT CREATE ----------------
    try:
        hubspot_ticket_id = await create_ticket(payload)

    except Exception as e:
        return {
            "status": "FAILED",
            "reason": "HubSpot ticket creation failed"
        }

    return {
        "hubspot_id": hubspot_ticket_id,
        "status": "SYNCED"
    }




async def get_tickets_from_hubspot():
    try:
        data = await fetch_hubspot_tickets()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"HubSpot API error: {str(e)}")

    tickets = []
    for t in data.get("results", []):
        tickets.append({
            "hubspot_id": t["id"],
            "title": t["properties"].get("subject"),
            "description": t["properties"].get("content"),
            "priority": t["properties"].get("hs_ticket_priority"),
            "status": t["properties"].get("hs_pipeline_stage"),
            "created_at": t["properties"].get("createdate"),
            "customer_mail": t['properties'].get('hs_all_associated_contact_emails')  # Get first associated contact ID
        })

    return {
        "source": "hubspot",
        "count": len(tickets),
        "tickets": tickets
    }

async def update_hubspot_ticket_only(
    hubspot_ticket_id: str,
    title: str | None = None,
    description: str | None = None,
    priority: str | None = None,
    status_stage: str | None = None
):
    properties = {}

    if title:
        properties["subject"] = title

    if description:
        properties["content"] = description

    if priority:
        properties["hs_ticket_priority"] = priority.upper()

    stage_map = {
            "open": "1",
            "inprogress": "2",
            "closed": "4"
        }

    if status_stage:
        mapped_stage = stage_map.get(status_stage.lower(), status_stage)
        properties["hs_pipeline_stage"] = mapped_stage

    if not properties:
        return {"status": "SKIPPED", "reason": "No fields to update"}

    updated = await update_ticket(hubspot_ticket_id, properties)

    return {
        "hubspot_id": hubspot_ticket_id,
        "status": "UPDATED",
        "updated_fields": list(properties.keys())
    }

async def delete_hubspot_ticket_only(hubspot_ticket_id: str):

    deleted = await delete_ticket(hubspot_ticket_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Ticket {hubspot_ticket_id} not found"
        )
    return {
        "hubspot_id": hubspot_ticket_id,
        "status": "DELETED"
    }