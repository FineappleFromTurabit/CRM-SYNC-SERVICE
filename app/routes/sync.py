# app/routes/sync.py
import traceback
from fastapi import APIRouter, HTTPException, Query
from app.services.customer_sync import sync_customers, sync_single_customer
from app.services.ticket_sync import sync_single_ticket, sync_tickets

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