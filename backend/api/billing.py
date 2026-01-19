"""
OhmVision - Billing API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from core.database import get_db
from models.models import Invoice, Contract, Client, User
from api.auth import get_current_active_user, require_admin

router = APIRouter()

@router.get("/invoices")
async def list_invoices(
    client_id: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Liste les factures"""
    query = select(Invoice).join(Contract)
    
    if current_user.role not in ["admin", "support"]:
        query = query.where(Contract.client_id == current_user.client_id)
    elif client_id:
        query = query.where(Contract.client_id == client_id)
    
    if status:
        query = query.where(Invoice.status == status)
    
    result = await db.execute(query.order_by(Invoice.created_at.desc()))
    return result.scalars().all()

@router.get("/invoices/{invoice_id}")
async def get_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Récupère une facture"""
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()
    
    if not invoice:
        raise HTTPException(status_code=404, detail="Facture non trouvée")
    
    return invoice

@router.get("/mrr")
async def get_mrr(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Calcule le MRR (Monthly Recurring Revenue)"""
    from models.models import ContractStatus
    
    result = await db.execute(
        select(func.sum(Contract.price_monthly)).where(
            Contract.status == ContractStatus.ACTIVE
        )
    )
    mrr = result.scalar() or 0
    
    # Compte les clients actifs
    clients_result = await db.execute(
        select(func.count(func.distinct(Contract.client_id))).where(
            Contract.status == ContractStatus.ACTIVE
        )
    )
    active_clients = clients_result.scalar() or 0
    
    return {
        "mrr": round(mrr, 2),
        "arr": round(mrr * 12, 2),
        "active_clients": active_clients,
        "arpu": round(mrr / active_clients, 2) if active_clients > 0 else 0
    }

@router.get("/revenue-by-package")
async def get_revenue_by_package(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Revenue par package"""
    from models.models import ContractStatus
    
    result = await db.execute(
        select(Contract.package, func.sum(Contract.price_monthly), func.count(Contract.id))
        .where(Contract.status == ContractStatus.ACTIVE)
        .group_by(Contract.package)
    )
    
    data = {}
    for row in result.all():
        data[row[0].value] = {
            "mrr": round(row[1] or 0, 2),
            "count": row[2]
        }
    
    return data
