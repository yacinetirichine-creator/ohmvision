"""
Migration Script - Add Multi-Channel Support to Cameras
========================================================
Ajoute les nouveaux champs pour le support multi-canal

IMPORTANT: Cette migration est ADDITIVE (ajoute seulement des colonnes)
Les données existantes ne sont PAS modifiées
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Révision ID
revision = 'multi_channel_v1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Ajoute les colonnes pour le support multi-canal"""
    
    # Créer les enums
    connection_type_enum = postgresql.ENUM(
        'rtsp', 'rtmp', 'onvif', 'http_mjpeg', 'https', 
        'webrtc', 'hls', 'cloud_api', 'webhook', 'nvr_dvr', 
        'usb', 'file',
        name='connectiontype'
    )
    connection_type_enum.create(op.get_bind(), checkfirst=True)
    
    manufacturer_enum = postgresql.ENUM(
        'hikvision', 'dahua', 'axis', 'foscam', 'vivotek',
        'bosch', 'samsung', 'sony', 'panasonic', 'mobotix',
        'avigilon', 'hanwha', 'uniview', 'tplink', 'xiaomi',
        'nest', 'ring', 'arlo', 'wyze', 'reolink',
        'generic', 'other',
        name='cameramanufacturer'
    )
    manufacturer_enum.create(op.get_bind(), checkfirst=True)
    
    # Ajouter les colonnes manufacturer info
    op.add_column('cameras', 
        sa.Column('manufacturer', manufacturer_enum, nullable=True, server_default='generic')
    )
    op.add_column('cameras', 
        sa.Column('model', sa.String(100), nullable=True)
    )
    op.add_column('cameras', 
        sa.Column('firmware_version', sa.String(50), nullable=True)
    )
    op.add_column('cameras', 
        sa.Column('serial_number', sa.String(100), nullable=True)
    )
    
    # Ajouter les colonnes connection type
    op.add_column('cameras', 
        sa.Column('connection_type', connection_type_enum, nullable=True, server_default='rtsp')
    )
    op.add_column('cameras', 
        sa.Column('primary_stream_url', sa.String(500), nullable=True)
    )
    op.add_column('cameras', 
        sa.Column('secondary_stream_url', sa.String(500), nullable=True)
    )
    op.add_column('cameras', 
        sa.Column('snapshot_url', sa.String(500), nullable=True)
    )
    
    # Ajouter les colonnes de configuration
    op.add_column('cameras', 
        sa.Column('connection_config', postgresql.JSON(astext_type=sa.Text()), 
                 nullable=True,
                 server_default=sa.text("'{\"protocol\": \"rtsp\", \"transport\": \"tcp\", \"timeout\": 5}'::json"))
    )
    op.add_column('cameras', 
        sa.Column('cloud_config', postgresql.JSON(astext_type=sa.Text()), 
                 nullable=True,
                 server_default=sa.text("'{}'::json"))
    )
    
    # Ajouter les colonnes de health monitoring
    op.add_column('cameras', 
        sa.Column('connection_health', sa.String(20), nullable=True, server_default='unknown')
    )
    op.add_column('cameras', 
        sa.Column('last_health_check', sa.DateTime(), nullable=True)
    )
    op.add_column('cameras', 
        sa.Column('uptime_percentage', sa.Float(), nullable=True, server_default='0.0')
    )
    op.add_column('cameras', 
        sa.Column('failed_connection_attempts', sa.Integer(), nullable=True, server_default='0')
    )
    op.add_column('cameras', 
        sa.Column('last_error_message', sa.Text(), nullable=True)
    )
    
    print("✅ Migration réussie : Colonnes multi-canal ajoutées")
    print("📝 Note : Les caméras existantes conservent leurs URLs RTSP dans 'rtsp_url'")
    print("🔄 Exécutez le script de migration des données si nécessaire")


def downgrade():
    """Supprime les colonnes multi-canal"""
    
    # Supprimer les colonnes health monitoring
    op.drop_column('cameras', 'last_error_message')
    op.drop_column('cameras', 'failed_connection_attempts')
    op.drop_column('cameras', 'uptime_percentage')
    op.drop_column('cameras', 'last_health_check')
    op.drop_column('cameras', 'connection_health')
    
    # Supprimer les colonnes de configuration
    op.drop_column('cameras', 'cloud_config')
    op.drop_column('cameras', 'connection_config')
    
    # Supprimer les colonnes connection type
    op.drop_column('cameras', 'snapshot_url')
    op.drop_column('cameras', 'secondary_stream_url')
    op.drop_column('cameras', 'primary_stream_url')
    op.drop_column('cameras', 'connection_type')
    
    # Supprimer les colonnes manufacturer
    op.drop_column('cameras', 'serial_number')
    op.drop_column('cameras', 'firmware_version')
    op.drop_column('cameras', 'model')
    op.drop_column('cameras', 'manufacturer')
    
    # Supprimer les enums
    op.execute('DROP TYPE IF EXISTS cameramanufacturer CASCADE')
    op.execute('DROP TYPE IF EXISTS connectiontype CASCADE')
    
    print("✅ Rollback réussi : Colonnes multi-canal supprimées")
