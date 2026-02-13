# app/services/customer_sync.py
from app.clients.internal_api import fetch_customers
from app.clients.hubspot_api import create_contact
from app.models.hubspot import HubSpotContact, HubspotCustomerDirect
from app.redis_client import get_value,set_value

async def sync_customers():
    customers = await fetch_customers()
    results = []

    for c in customers:
        contact = HubSpotContact.from_internal(c)
        hubspot_id = await create_contact(contact.dict())

        await set_value(f"customer:{c.id}", hubspot_id)

        results.append({
            "internal_id": c.id,
            "hubspot_id": hubspot_id,
            "status": "SYNCED"
        })

    return results

async def sync_single_customer(customer_id: int):
    customers = await fetch_customers()
    customer = next((c for c in customers if c.id == customer_id), None)

    if not customer:
        return None

    # Skip if already synced
    existing = await get_value(f"customer:{customer.id}")
    if existing:
        return {
            "internal_id": customer.id,
            "hubspot_id": existing,
            "status": "ALREADY_SYNCED"
        }

    payload = {
        "properties": {
            "email": customer.email,
            "firstname": customer.name,
            "company": customer.company or ""
        }
    }

    hubspot_id = await create_contact(payload)
    await set_value(f"customer:{customer.id}", hubspot_id)

    return {
        "internal_id": customer.id,
        "hubspot_id": hubspot_id,
        "status": "SYNCED"
    }


async def create_customer_direct(customer : HubspotCustomerDirect):
    
    payload = {
        "properties": {
            "email": customer.email,
            "firstname": customer.name,
            "company": customer.company or ""
        }
    }
    hubspot_id = await create_contact(payload)

    return {
        "hubspot_id": hubspot_id,
        "status": "Created"
    }