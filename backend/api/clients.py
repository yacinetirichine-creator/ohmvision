"""
OhmVision - Clients API
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

from core.database import get_db
from models.models import Client, Contract, Camera, User, PackageType, ContractStatus
from api.auth import get_current_active_user, require_admin

router = APIRouter()

# Schemas
class ClientCreate(BaseModel):
    name: str
    company_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    siret: Optional[str] = None

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    siret: Optional[str] = None
    is_active: Optional[bool] = None

class ClientResponse(BaseModel):
    id: int
    name: str
    company_name: Optional[str]
    email: str
    phone: Optional[str]
    city: Optional[str]
    is_active: bool
    created_at: datetime
    
    # Stats
    cameras_count: Optional[int] = 0
    active_contract: Optional[str] = None
    mrr: Optional[float] = 0
    
    class Config:
        from_attributes = True

class ClientListResponse(BaseModel):
    items: List[ClientResponse]
    total: int
    page: int
    pages: int

# Routes
@router.get("/", response_model=ClientListResponse)
async def list_clients(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Liste tous les clients (admin only)"""
    query = select(Client)
    
    # Filtres
    if search:
        query = query.where(
            (Client.name.ilike(f"%{search}%")) |
            (Client.company_name.ilike(f"%{search}%")) |
            (Client.email.ilike(f"%{search}%"))
        )
    
    if status == "active":
        query = query.where(Client.is_active == True)
    elif status == "inactive":
        query = query.where(Client.is_active == False)
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(Client.created_at.desc())
    
    result = await db.execute(query)
    clients = result.scalars().all()
    
    # Enrichir avec les stats
    client_responses = []
    for client in clients:
        # Compte les caméras
        cam_result = await db.execute(
            select(func.count()).where(Camera.client_id == client.id)
        )
        cameras_count = cam_result.scalar()
        
        # Contrat actif
        contract_result = await db.execute(
            select(Contract).where(
                (Contract.client_id == client.id) &
                (Contract.status == ContractStatus.ACTIVE)
            )
        )
        contract = contract_result.scalar_one_or_none()
        
        client_responses.append(ClientResponse(
            id=client.id,
            name=client.name,
            company_name=client.company_name,
            email=client.email,
            phone=client.phone,
            city=client.city,
            is_active=client.is_active,
            created_at=client.created_at,
            cameras_count=cameras_count,
            active_contract=contract.package.value if contract else None,
            mrr=contract.price_monthly if contract else 0
        ))
    
    return ClientListResponse(
        items=client_responses,
        total=total,
        page=page,
        pages=(total + limit - 1) // limit
    )

@router.post("/", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Crée un nouveau client"""
    # Vérifie si l'email existe
    existing = await db.execute(select(Client).where(Client.email == client_data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    client = Client(**client_data.model_dump())
    db.add(client)
    await db.commit()
    await db.refresh(client)
    
    return ClientResponse(
        id=client.id,
        name=client.name,
        company_name=client.company_name,
        email=client.email,
        phone=client.phone,
        city=client.city,
        is_active=client.is_active,
        created_at=client.created_at,
        cameras_count=0,
        active_contract=None,
        mrr=0
    )

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Récupère un client"""
    # Vérifie les permissions
    if current_user.role not in ["admin", "support"] and current_user.client_id != client_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    # Stats
    cam_result = await db.execute(
        select(func.count()).where(Camera.client_id == client.id)
    )
    cameras_count = cam_result.scalar()
    
    contract_result = await db.execute(
        select(Contract).where(
            (Contract.client_id == client.id) &
            (Contract.status == ContractStatus.ACTIVE)
        )
    )
    contract = contract_result.scalar_one_or_none()
    
    return ClientResponse(
        id=client.id,
        name=client.name,
        company_name=client.company_name,
        email=client.email,
        phone=client.phone,
        city=client.city,
        is_active=client.is_active,
        created_at=client.created_at,
        cameras_count=cameras_count,
        active_contract=contract.package.value if contract else None,
        mrr=contract.price_monthly if contract else 0
    )

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Met à jour un client"""
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    # Met à jour les champs
    update_data = client_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    await db.commit()
    await db.refresh(client)
    
    return ClientResponse(
        id=client.id,
        name=client.name,
        company_name=client.company_name,
        email=client.email,
        phone=client.phone,
        city=client.city,
        is_active=client.is_active,
        created_at=client.created_at
    )

@router.delete("/{client_id}")
async def delete_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Supprime un client (soft delete)"""
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    client.is_active = False
    await db.commit()
    
    return {"message": "Client désactivé"}

@router.get("/{client_id}/stats")
async def get_client_stats(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Récupère les statistiques d'un client"""
    # Vérifie les permissions
    if current_user.role not in ["admin", "support"] and current_user.client_id != client_id:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Compte caméras
    cam_result = await db.execute(
        select(func.count()).where(Camera.client_id == client_id)
    )
    total_cameras = cam_result.scalar()
    
    # Caméras en ligne
    online_result = await db.execute(
        select(func.count()).where(
            (Camera.client_id == client_id) & (Camera.is_online == True)
        )
    )
    online_cameras = online_result.scalar()
    
    # Alertes du jour
    from datetime import date
    from models.models import Alert
    
    alerts_result = await db.execute(
        select(func.count()).select_from(Alert).join(Camera).where(
            (Camera.client_id == client_id) &
            (func.date(Alert.created_at) == date.today())
        )
    )
    today_alerts = alerts_result.scalar()
    
    return {
        "total_cameras": total_cameras,
        "online_cameras": online_cameras,
        "offline_cameras": total_cameras - online_cameras,
        "today_alerts": today_alerts,
        "uptime": round(online_cameras / total_cameras * 100, 1) if total_cameras > 0 else 100
    }
