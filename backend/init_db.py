"""
OhmVision - Database Initialization Script
==========================================
Creates initial admin user and sample data
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from passlib.context import CryptContext

# Import models
import sys
sys.path.append('.')
from models.models import Base, User, Client, Contract, Camera, UserRole, PackageType, ContractStatus, DeploymentType
from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def init_db():
    """Initialize database with default data"""
    
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check if admin exists
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.email == "admin@ohmvision.fr")
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print("✅ Admin user already exists")
            return
        
        # Create admin user
        admin = User(
            email="admin@ohmvision.fr",
            hashed_password=pwd_context.hash("admin123"),
            first_name="Admin",
            last_name="OhmVision",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        session.add(admin)
        
        # Create demo client
        demo_client = Client(
            name="Entreprise Demo",
            company_name="Demo SARL",
            email="demo@entreprise.fr",
            phone="+33 1 23 45 67 89",
            address="123 Rue de la Démo",
            city="Paris",
            postal_code="75001",
            country="France",
            siret="12345678901234",
            is_active=True
        )
        session.add(demo_client)
        await session.flush()
        
        # Create demo user for client
        demo_user = User(
            email="demo@client.fr",
            hashed_password=pwd_context.hash("demo123"),
            first_name="Jean",
            last_name="Demo",
            role=UserRole.CLIENT_ADMIN,
            client_id=demo_client.id,
            is_active=True,
            is_verified=True
        )
        session.add(demo_user)
        
        # Create demo contract
        demo_contract = Contract(
            client_id=demo_client.id,
            package=PackageType.BUSINESS,
            deployment_type=DeploymentType.CLOUD,
            price_monthly=149.0,
            price_yearly=1490.0,
            is_yearly=False,
            max_cameras=20,
            max_users=5,
            features=["person_detection", "counting", "fall_detection", "ppe_detection", "alerts_all", "reports"],
            status=ContractStatus.ACTIVE
        )
        session.add(demo_contract)
        
        # Create demo cameras
        cameras = [
            Camera(
                client_id=demo_client.id,
                name="Caméra Entrée",
                description="Caméra principale à l'entrée du bâtiment",
                location="Entrée principale",
                ip_address="192.168.1.100",
                rtsp_url="rtsp://192.168.1.100:554/stream1",
                is_active=True,
                is_online=True,
                resolution_width=1920,
                resolution_height=1080,
                fps=15,
                detection_config={
                    "person_detection": True,
                    "counting": True,
                    "fall_detection": False,
                    "ppe_detection": False,
                    "fire_detection": False
                }
            ),
            Camera(
                client_id=demo_client.id,
                name="Caméra Entrepôt",
                description="Surveillance de la zone de stockage",
                location="Entrepôt A",
                ip_address="192.168.1.101",
                rtsp_url="rtsp://192.168.1.101:554/stream1",
                is_active=True,
                is_online=True,
                resolution_width=1920,
                resolution_height=1080,
                fps=15,
                detection_config={
                    "person_detection": True,
                    "counting": False,
                    "fall_detection": True,
                    "ppe_detection": True,
                    "fire_detection": True
                }
            ),
            Camera(
                client_id=demo_client.id,
                name="Caméra Parking",
                description="Surveillance du parking",
                location="Parking extérieur",
                ip_address="192.168.1.102",
                rtsp_url="rtsp://192.168.1.102:554/stream1",
                is_active=True,
                is_online=False,
                resolution_width=1920,
                resolution_height=1080,
                fps=10,
                detection_config={
                    "person_detection": True,
                    "counting": False,
                    "fall_detection": False,
                    "ppe_detection": False,
                    "vehicle_detection": True
                }
            ),
        ]
        
        for camera in cameras:
            session.add(camera)
        
        await session.commit()
        
        print("✅ Database initialized with:")
        print(f"   - Admin user: admin@ohmvision.fr / admin123")
        print(f"   - Demo user: demo@client.fr / demo123")
        print(f"   - Demo client: Entreprise Demo")
        print(f"   - Demo contract: Business (149€/mois)")
        print(f"   - {len(cameras)} cameras")

if __name__ == "__main__":
    print("🚀 Initializing OhmVision database...")
    asyncio.run(init_db())
    print("✅ Done!")
