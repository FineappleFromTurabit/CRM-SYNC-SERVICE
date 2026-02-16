# app/routes/sync.py
import json
import traceback
from fastapi import APIRouter, Body, HTTPException, Header, Query, Request
import httpx
from app.clients.hubspot_api import get_tickets_by_owner, update_hubspot_ticket_owner
from app.config import HUBSPOT_TOKEN
from app.models.hubspot import AssignTicketRequest, HubSpotContact, HubspotCustomerDirect
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
    



@router.get("/hubspot/assignees")
async def get_hubspot_assignees(authorization: str | None = Header(None)):
    
    if not HUBSPOT_TOKEN:
        return {"error": "HubSpot token not configured"}

    url = "https://api.hubapi.com/crm/v3/owners/"

    headers = {
        "Authorization": f"Bearer {HUBSPOT_TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != 200:
        return {
            "error": "Failed to fetch owners",
            "details": response.text
        }

    owners = response.json().get("results", [])

    assignees = [
        {
            "id": owner["id"],
            "email": owner.get("email"),
            "name": f'{owner.get("firstName","")} {owner.get("lastName","")}'.strip(),
            "role": owner.get("type")  # USER / TEAM
        }
        for owner in owners
    ]

    return {
        "total": len(assignees),
        "assignees": assignees
    }



@router.patch("/tickets/{hubspot_ticket_id}/assign")
async def assign_ticket(
    hubspot_ticket_id: str,
    payload: AssignTicketRequest,
    request: Request
):

    try:
        result = await update_hubspot_ticket_owner(
            hubspot_ticket_id,
            payload.assigned_to
        )

        return {
            "status": "SUCCESS",
            "message": f"Ticket assigned to agent {payload.assigned_to}",
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/agents/{agent_id}/workload")
async def agent_workload(agent_id: int):

    tickets = await get_tickets_by_owner(str(agent_id))

    return {
        "agent_id": agent_id,
        "total_tickets": len(tickets),
        "open": len([t for t in tickets if t["properties"].get("hs_pipeline_stage") == "1"]),
        "inprogress": len([t for t in tickets if t["properties"].get("hs_pipeline_stage") == "2"]),
        "closed": len([t for t in tickets if t["properties"].get("hs_pipeline_stage") == "4"]),

        "tickets": tickets
    }
