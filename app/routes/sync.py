# app/routes/sync.py
import json
import traceback
from fastapi import APIRouter, Body, HTTPException, Query, Request
from app.models.hubspot import HubSpotContact, HubspotCustomerDirect
from app.models.internal import CreateTicketDirectRequest
from app.services.customer_sync import create_customer_direct, sync_customers, sync_single_customer
from app.services.ticket_sync import delete_hubspot_ticket_only, sync_single_ticket, sync_single_ticket_direct, sync_tickets,get_tickets_from_hubspot, update_hubspot_ticket_only
from app.auth_middleware import admin_required, auth_required

router = APIRouter()

@router.post("/customers")
async def sync_customers_endpoint():
    try:
        return await sync_customers()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/tickets")
async def sync_tickets_endpoint():
    try:
        return await sync_tickets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/customers/create")
async def create_customer_sync(
    customer_id: int = Query(..., description="Internal customer ID")
):
    result = await sync_single_customer(customer_id)
    if not result:
        raise HTTPException(status_code=400, detail="Customer sync failed")
    return result

@router.post("/customers/create/direct")
async def create_direct_customer(request:Request):
    body = await request.json()

    customer = HubspotCustomerDirect(**body)


    try:
        return await create_customer_direct(
            customer=customer
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/tickets/create")
async def create_ticket_sync(
    ticket_id: int = Query(..., description="Internal ticket ID")
):
    result = await sync_single_ticket(ticket_id)
    if not result:
        raise HTTPException(status_code=400, detail="Ticket sync failed")
    return result

@router.post("/tickets/create/direct")
@auth_required
async def create_ticket_direct(ticket: CreateTicketDirectRequest,request : Request):
    try:
        return await sync_single_ticket_direct(ticket.dict())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.get("/tickets/hubspot")
@auth_required
async def fetch_tickets_from_hubspot(request : Request):
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
@admin_required
async def delete_ticket_endpoint(hubspot_ticket_id: str,request : Request):
    """
    Delete ticket from HubSpot only
    """
    try:
        return await delete_hubspot_ticket_only(hubspot_ticket_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))