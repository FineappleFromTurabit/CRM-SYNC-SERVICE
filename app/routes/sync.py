# app/routes/sync.py
import json
import traceback
from fastapi import APIRouter, Body, HTTPException, Query
from app.models.internal import CreateTicketDirectRequest
from app.services.customer_sync import sync_customers, sync_single_customer
from app.services.ticket_sync import delete_hubspot_ticket_only, sync_single_ticket, sync_single_ticket_direct, sync_tickets,get_tickets_from_hubspot, update_hubspot_ticket_only

router = APIRouter()

@router.post("/customers")
async def sync_customers_endpoint():
    try:
        return await sync_customers()
    except Exception as e:
        traceback.print_exc()   # ← PRINTS FULL STACKTRACE
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/tickets")
async def sync_tickets_endpoint():
    try:
        return await sync_tickets()
    except Exception as e:
        traceback.print_exc()   # ← PRINTS FULL STACKTRACE
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/customers/create")
async def create_customer_sync(
    customer_id: int = Query(..., description="Internal customer ID")
):
    result = await sync_single_customer(customer_id)
    if not result:
        raise HTTPException(status_code=400, detail="Customer sync failed")
    return result

@router.post("/tickets/create")
async def create_ticket_sync(
    ticket_id: int = Query(..., description="Internal ticket ID")
):
    result = await sync_single_ticket(ticket_id)
    if not result:
        raise HTTPException(status_code=400, detail="Ticket sync failed")
    return result

@router.post("/tickets/create/direct")
async def create_ticket_direct(ticket: CreateTicketDirectRequest):
    try:
        return await sync_single_ticket_direct(ticket.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/tickets/hubspot")
async def fetch_tickets_from_hubspot():
    return await get_tickets_from_hubspot()

@router.patch("/tickets/{hubspot_ticket_id}")
async def update_ticket_hubspot(
    hubspot_ticket_id: str,
    payload: dict = Body(...)
):
    """
    Update HubSpot ticket only
    """
    return await update_hubspot_ticket_only(
        hubspot_ticket_id=hubspot_ticket_id,
        title=payload.get("title"),
        description=payload.get("description"),
        priority=payload.get("priority"),
        status_stage=payload.get("status_stage")
    )

@router.delete("/tickets/{hubspot_ticket_id}")
async def delete_ticket_endpoint(hubspot_ticket_id: str):
    """
    Delete ticket from HubSpot only
    """
    try:
        return await delete_hubspot_ticket_only(hubspot_ticket_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))