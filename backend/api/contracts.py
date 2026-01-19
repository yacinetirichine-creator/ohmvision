"""
OhmVision - Contracts API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta

from core.database import get_db
from core.config import settings
from models.models import Contract, Client, User, PackageType, ContractStatus, DeploymentType
from api.auth import get_current_active_user, require_admin

router = APIRouter()

class ContractCreate(BaseModel):
    client_id: int
    package: PackageType
    deployment_type: DeploymentType = DeploymentType.CLOUD
    is_yearly: bool = False
    discount_percent: float = 0
    max_cameras: Optional[int] = None
    max_users: int = 5

class ContractUpdate(BaseModel):
    package: Optional[PackageType] = None
    status: Optional[ContractStatus] = None
    discount_percent: Optional[float] = None
    max_cameras: Optional[int] = None

@router.get("/")
async def list_contracts(
    client_id: Optional[int] = None,
    status: Optional[ContractStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Liste tous les contrats"""
    query = select(Contract)
    if client_id:
        query = query.where(Contract.client_id == client_id)
    if status:
        query = query.where(Contract.status == status)
    
    result = await db.execute(query.order_by(Contract.created_at.desc()))
    return result.scalars().all()

@router.post("/")
async def create_contract(
    data: ContractCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Crée un nouveau contrat"""
    # Récupère les infos du package
    package_info = settings.PACKAGES.get(data.package.value)
    if not package_info:
        raise HTTPException(status_code=400, detail="Package invalide")
    
    # Calcule le prix
    base_price = package_info["price_yearly"] if data.is_yearly else package_info["price_monthly"]
    final_price = base_price * (1 - data.discount_percent / 100)
    
    contract = Contract(
        client_id=data.client_id,
        package=data.package,
        deployment_type=data.deployment_type,
        price_monthly=final_price if not data.is_yearly else final_price / 12,
        price_yearly=final_price if data.is_yearly else final_price * 12,
        is_yearly=data.is_yearly,
        discount_percent=data.discount_percent,
        max_cameras=data.max_cameras or package_info["max_cameras"],
        max_users=data.max_users,
        features=package_info["features"],
        status=ContractStatus.TRIAL,
        trial_ends_at=datetime.utcnow() + timedelta(days=14)
    )
    
    db.add(contract)
    await db.commit()
    await db.refresh(contract)
    
    return contract

@router.get("/{contract_id}")
async def get_contract(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Récupère un contrat"""
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contrat non trouvé")
    return contract

@router.put("/{contract_id}")
async def update_contract(
    contract_id: int,
    data: ContractUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Met à jour un contrat"""
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contrat non trouvé")
    
    update_data = data.model_dump(exclude_unset=True)
    
    # Si changement de package, met à jour le prix
    if "package" in update_data:
        package_info = settings.PACKAGES.get(update_data["package"].value)
        contract.price_monthly = package_info["price_monthly"]
        contract.max_cameras = package_info["max_cameras"]
        contract.features = package_info["features"]
    
    for field, value in update_data.items():
        setattr(contract, field, value)
    
    await db.commit()
    await db.refresh(contract)
    
    return contract

@router.post("/{contract_id}/activate")
async def activate_contract(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Active un contrat"""
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contrat non trouvé")
    
    contract.status = ContractStatus.ACTIVE
    contract.start_date = datetime.utcnow()
    contract.next_billing_date = datetime.utcnow() + timedelta(days=30)
    
    await db.commit()
    
    return {"message": "Contrat activé", "contract": contract}

@router.post("/{contract_id}/cancel")
async def cancel_contract(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Annule un contrat"""
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contrat non trouvé")
    
    contract.status = ContractStatus.CANCELLED
    contract.end_date = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Contrat annulé"}
