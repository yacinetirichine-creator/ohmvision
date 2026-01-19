"""
OhmVision - Multi-Channel Notification System
Notifications via Email, Telegram, Discord, SMS, Push, Webhook
"""

import asyncio
import aiohttp
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json
import logging
import base64

logger = logging.getLogger(__name__)


class NotificationChannel(str, Enum):
    """Canaux de notification disponibles"""
    EMAIL = "email"
    TELEGRAM = "telegram"
    DISCORD = "discord"
    SMS = "sms"
    WEBHOOK = "webhook"
    PUSH = "push"
    SLACK = "slack"
    TEAMS = "teams"


class AlertSeverity(str, Enum):
    """Niveaux de sévérité des alertes"""
    INFO = "info"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class NotificationConfig:
    """Configuration d'un canal de notification"""
    channel: NotificationChannel
    enabled: bool = True
    config: Dict[str, Any] = None
    
    # Filtres
    min_severity: AlertSeverity = AlertSeverity.INFO
    alert_types: List[str] = None  # None = tous
    cameras: List[int] = None  # None = toutes
    
    # Rate limiting
    cooldown_seconds: int = 60  # Temps minimum entre 2 notifs
    max_per_hour: int = 30


@dataclass
class Alert:
    """Structure d'une alerte"""
    id: str
    camera_id: int
    camera_name: str
    alert_type: str  # fall, fire, intrusion, ppe_violation, etc.
    severity: AlertSeverity
    message: str
    timestamp: datetime
    snapshot_base64: Optional[str] = None
    video_clip_url: Optional[str] = None
    metadata: Dict[str, Any] = None


class NotificationManager:
    """
    Gestionnaire de notifications multi-canal
    Envoie des alertes sur tous les canaux configurés
    """
    
    def __init__(self):
        self.channels: Dict[str, NotificationConfig] = {}
        self.last_notification: Dict[str, datetime] = {}
        self.notification_count: Dict[str, int] = {}
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Récupère ou crée la session HTTP"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self):
        """Ferme la session HTTP"""
        if self._session:
            await self._session.close()
    
    def add_channel(self, name: str, config: NotificationConfig):
        """Ajoute un canal de notification"""
        self.channels[name] = config
        logger.info(f"Channel added: {name} ({config.channel})")
    
    def remove_channel(self, name: str):
        """Supprime un canal de notification"""
        if name in self.channels:
            del self.channels[name]
    
    async def send_alert(self, alert: Alert) -> Dict[str, bool]:
        """
        Envoie une alerte sur tous les canaux configurés
        
        Returns:
            Dict avec le statut d'envoi par canal
        """
        results = {}
        
        for name, config in self.channels.items():
            if not config.enabled:
                continue
            
            # Vérifier les filtres
            if not self._should_send(name, config, alert):
                continue
            
            try:
                success = await self._send_to_channel(config, alert)
                results[name] = success
                
                if success:
                    self.last_notification[name] = datetime.now()
                    self.notification_count[name] = self.notification_count.get(name, 0) + 1
                    
            except Exception as e:
                logger.error(f"Error sending to {name}: {e}")
                results[name] = False
        
        return results
    
    def _should_send(self, name: str, config: NotificationConfig, alert: Alert) -> bool:
        """Vérifie si l'alerte doit être envoyée sur ce canal"""
        
        # Vérifier la sévérité minimale
        severity_order = {
            AlertSeverity.INFO: 0,
            AlertSeverity.WARNING: 1,
            AlertSeverity.HIGH: 2,
            AlertSeverity.CRITICAL: 3
        }
        
        if severity_order[alert.severity] < severity_order[config.min_severity]:
            return False
        
        # Vérifier le type d'alerte
        if config.alert_types and alert.alert_type not in config.alert_types:
            return False
        
        # Vérifier la caméra
        if config.cameras and alert.camera_id not in config.cameras:
            return False
        
        # Vérifier le cooldown
        if name in self.last_notification:
            elapsed = (datetime.now() - self.last_notification[name]).total_seconds()
            if elapsed < config.cooldown_seconds:
                return False
        
        # Vérifier le rate limit horaire
        # (simplifié, en production utiliser une fenêtre glissante)
        if self.notification_count.get(name, 0) >= config.max_per_hour:
            return False
        
        return True
    
    async def _send_to_channel(self, config: NotificationConfig, alert: Alert) -> bool:
        """Envoie une alerte sur un canal spécifique"""
        
        if config.channel == NotificationChannel.EMAIL:
            return await self._send_email(config, alert)
        elif config.channel == NotificationChannel.TELEGRAM:
            return await self._send_telegram(config, alert)
        elif config.channel == NotificationChannel.DISCORD:
            return await self._send_discord(config, alert)
        elif config.channel == NotificationChannel.SMS:
            return await self._send_sms(config, alert)
        elif config.channel == NotificationChannel.WEBHOOK:
            return await self._send_webhook(config, alert)
        elif config.channel == NotificationChannel.SLACK:
            return await self._send_slack(config, alert)
        elif config.channel == NotificationChannel.TEAMS:
            return await self._send_teams(config, alert)
        else:
            logger.warning(f"Unknown channel: {config.channel}")
            return False
    
    # =========================================================================
    # Implémentations par canal
    # =========================================================================
    
    async def _send_email(self, config: NotificationConfig, alert: Alert) -> bool:
        """Envoie un email"""
        try:
            cfg = config.config or {}
            
            msg = MIMEMultipart()
            msg['From'] = cfg.get('from_email', 'alerts@ohmvision.local')
            msg['To'] = cfg.get('to_email', '')
            msg['Subject'] = f"🚨 OhmVision Alert: {alert.alert_type.upper()} - {alert.camera_name}"
            
            # Corps HTML
            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <h2 style="color: {'#dc2626' if alert.severity == AlertSeverity.CRITICAL else '#f59e0b'};">
                    🚨 {alert.alert_type.upper()}
                </h2>
                <p><strong>Caméra:</strong> {alert.camera_name}</p>
                <p><strong>Message:</strong> {alert.message}</p>
                <p><strong>Heure:</strong> {alert.timestamp.strftime('%d/%m/%Y %H:%M:%S')}</p>
                <p><strong>Sévérité:</strong> {alert.severity.value.upper()}</p>
                
                {'<img src="cid:snapshot" style="max-width: 640px; border-radius: 8px;">' if alert.snapshot_base64 else ''}
                
                <hr>
                <p style="color: #666; font-size: 12px;">
                    OhmVision - Vidéosurveillance Intelligente
                </p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(html, 'html'))
            
            # Joindre l'image si disponible
            if alert.snapshot_base64:
                img_data = base64.b64decode(alert.snapshot_base64)
                img = MIMEImage(img_data)
                img.add_header('Content-ID', '<snapshot>')
                msg.attach(img)
            
            # Envoyer
            smtp_host = cfg.get('smtp_host', 'localhost')
            smtp_port = cfg.get('smtp_port', 587)
            smtp_user = cfg.get('smtp_user', '')
            smtp_pass = cfg.get('smtp_password', '')
            
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                if smtp_user:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                server.send_message(msg)
            
            logger.info(f"Email sent for alert {alert.id}")
            return True
            
        except Exception as e:
            logger.error(f"Email error: {e}")
            return False
    
    async def _send_telegram(self, config: NotificationConfig, alert: Alert) -> bool:
        """Envoie un message Telegram"""
        try:
            cfg = config.config or {}
            bot_token = cfg.get('bot_token', '')
            chat_id = cfg.get('chat_id', '')
            
            if not bot_token or not chat_id:
                logger.error("Telegram: missing bot_token or chat_id")
                return False
            
            session = await self._get_session()
            
            # Formater le message
            severity_emoji = {
                AlertSeverity.INFO: "ℹ️",
                AlertSeverity.WARNING: "⚠️",
                AlertSeverity.HIGH: "🔴",
                AlertSeverity.CRITICAL: "🚨"
            }
            
            message = f"""
{severity_emoji.get(alert.severity, '📢')} *{alert.alert_type.upper()}*

📹 *Caméra:* {alert.camera_name}
📝 *Message:* {alert.message}
🕐 *Heure:* {alert.timestamp.strftime('%d/%m/%Y %H:%M:%S')}
⚡ *Sévérité:* {alert.severity.value.upper()}
"""
            
            # Envoyer le message
            if alert.snapshot_base64:
                # Envoyer avec photo
                url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
                
                # Décoder l'image
                img_data = base64.b64decode(alert.snapshot_base64)
                
                data = aiohttp.FormData()
                data.add_field('chat_id', chat_id)
                data.add_field('caption', message)
                data.add_field('parse_mode', 'Markdown')
                data.add_field('photo', img_data, filename='alert.jpg', content_type='image/jpeg')
                
                async with session.post(url, data=data) as resp:
                    return resp.status == 200
            else:
                # Envoyer texte seul
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                payload = {
                    'chat_id': chat_id,
                    'text': message,
                    'parse_mode': 'Markdown'
                }
                
                async with session.post(url, json=payload) as resp:
                    return resp.status == 200
                    
        except Exception as e:
            logger.error(f"Telegram error: {e}")
            return False
    
    async def _send_discord(self, config: NotificationConfig, alert: Alert) -> bool:
        """Envoie un message Discord via webhook"""
        try:
            cfg = config.config or {}
            webhook_url = cfg.get('webhook_url', '')
            
            if not webhook_url:
                logger.error("Discord: missing webhook_url")
                return False
            
            session = await self._get_session()
            
            # Couleur selon sévérité
            colors = {
                AlertSeverity.INFO: 0x3498db,      # Bleu
                AlertSeverity.WARNING: 0xf1c40f,   # Jaune
                AlertSeverity.HIGH: 0xe67e22,      # Orange
                AlertSeverity.CRITICAL: 0xe74c3c   # Rouge
            }
            
            embed = {
                "title": f"🚨 {alert.alert_type.upper()}",
                "description": alert.message,
                "color": colors.get(alert.severity, 0x3498db),
                "fields": [
                    {"name": "📹 Caméra", "value": alert.camera_name, "inline": True},
                    {"name": "⚡ Sévérité", "value": alert.severity.value.upper(), "inline": True},
                    {"name": "🕐 Heure", "value": alert.timestamp.strftime('%d/%m/%Y %H:%M:%S'), "inline": True}
                ],
                "footer": {"text": "OhmVision - Vidéosurveillance Intelligente"},
                "timestamp": alert.timestamp.isoformat()
            }
            
            # Ajouter l'image si disponible
            if alert.snapshot_base64:
                # Discord ne supporte pas le base64 direct, on utilise une URL
                # En production, uploader l'image quelque part et utiliser l'URL
                pass
            
            payload = {
                "embeds": [embed],
                "username": "OhmVision Alerts"
            }
            
            async with session.post(webhook_url, json=payload) as resp:
                return resp.status in [200, 204]
                
        except Exception as e:
            logger.error(f"Discord error: {e}")
            return False
    
    async def _send_sms(self, config: NotificationConfig, alert: Alert) -> bool:
        """Envoie un SMS via Twilio ou autre provider"""
        try:
            cfg = config.config or {}
            provider = cfg.get('provider', 'twilio')
            
            if provider == 'twilio':
                account_sid = cfg.get('account_sid', '')
                auth_token = cfg.get('auth_token', '')
                from_number = cfg.get('from_number', '')
                to_number = cfg.get('to_number', '')
                
                if not all([account_sid, auth_token, from_number, to_number]):
                    logger.error("SMS: missing Twilio credentials")
                    return False
                
                session = await self._get_session()
                
                message = f"🚨 OhmVision: {alert.alert_type.upper()} sur {alert.camera_name}. {alert.message}"
                
                url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
                
                auth = aiohttp.BasicAuth(account_sid, auth_token)
                data = {
                    'From': from_number,
                    'To': to_number,
                    'Body': message[:160]  # Limite SMS
                }
                
                async with session.post(url, auth=auth, data=data) as resp:
                    return resp.status == 201
            
            else:
                logger.error(f"SMS provider not supported: {provider}")
                return False
                
        except Exception as e:
            logger.error(f"SMS error: {e}")
            return False
    
    async def _send_webhook(self, config: NotificationConfig, alert: Alert) -> bool:
        """Envoie vers un webhook générique"""
        try:
            cfg = config.config or {}
            url = cfg.get('url', '')
            headers = cfg.get('headers', {})
            method = cfg.get('method', 'POST').upper()
            
            if not url:
                logger.error("Webhook: missing url")
                return False
            
            session = await self._get_session()
            
            payload = {
                "alert_id": alert.id,
                "camera_id": alert.camera_id,
                "camera_name": alert.camera_name,
                "alert_type": alert.alert_type,
                "severity": alert.severity.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "metadata": alert.metadata,
                "snapshot": alert.snapshot_base64 if cfg.get('include_snapshot', False) else None
            }
            
            if method == 'POST':
                async with session.post(url, json=payload, headers=headers) as resp:
                    return 200 <= resp.status < 300
            elif method == 'PUT':
                async with session.put(url, json=payload, headers=headers) as resp:
                    return 200 <= resp.status < 300
            else:
                logger.error(f"Webhook: unsupported method {method}")
                return False
                
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return False
    
    async def _send_slack(self, config: NotificationConfig, alert: Alert) -> bool:
        """Envoie un message Slack"""
        try:
            cfg = config.config or {}
            webhook_url = cfg.get('webhook_url', '')
            
            if not webhook_url:
                logger.error("Slack: missing webhook_url")
                return False
            
            session = await self._get_session()
            
            # Couleur selon sévérité
            colors = {
                AlertSeverity.INFO: "#36a64f",
                AlertSeverity.WARNING: "#daa038",
                AlertSeverity.HIGH: "#cc4400",
                AlertSeverity.CRITICAL: "#cc0000"
            }
            
            payload = {
                "attachments": [{
                    "color": colors.get(alert.severity, "#36a64f"),
                    "title": f"🚨 {alert.alert_type.upper()}",
                    "text": alert.message,
                    "fields": [
                        {"title": "Caméra", "value": alert.camera_name, "short": True},
                        {"title": "Sévérité", "value": alert.severity.value.upper(), "short": True},
                        {"title": "Heure", "value": alert.timestamp.strftime('%d/%m/%Y %H:%M:%S'), "short": True}
                    ],
                    "footer": "OhmVision",
                    "ts": int(alert.timestamp.timestamp())
                }]
            }
            
            async with session.post(webhook_url, json=payload) as resp:
                return resp.status == 200
                
        except Exception as e:
            logger.error(f"Slack error: {e}")
            return False
    
    async def _send_teams(self, config: NotificationConfig, alert: Alert) -> bool:
        """Envoie un message Microsoft Teams"""
        try:
            cfg = config.config or {}
            webhook_url = cfg.get('webhook_url', '')
            
            if not webhook_url:
                logger.error("Teams: missing webhook_url")
                return False
            
            session = await self._get_session()
            
            # Couleur selon sévérité
            colors = {
                AlertSeverity.INFO: "0078D7",
                AlertSeverity.WARNING: "FFC107",
                AlertSeverity.HIGH: "FF5722",
                AlertSeverity.CRITICAL: "D32F2F"
            }
            
            payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": colors.get(alert.severity, "0078D7"),
                "summary": f"OhmVision Alert: {alert.alert_type}",
                "sections": [{
                    "activityTitle": f"🚨 {alert.alert_type.upper()}",
                    "facts": [
                        {"name": "Caméra", "value": alert.camera_name},
                        {"name": "Message", "value": alert.message},
                        {"name": "Sévérité", "value": alert.severity.value.upper()},
                        {"name": "Heure", "value": alert.timestamp.strftime('%d/%m/%Y %H:%M:%S')}
                    ],
                    "markdown": True
                }]
            }
            
            async with session.post(webhook_url, json=payload) as resp:
                return resp.status == 200
                
        except Exception as e:
            logger.error(f"Teams error: {e}")
            return False


# Instance globale
notification_manager = NotificationManager()


# ============================================================================
# API Helper Functions
# ============================================================================

async def send_alert_notification(
    camera_id: int,
    camera_name: str,
    alert_type: str,
    severity: str,
    message: str,
    snapshot_base64: str = None
) -> Dict[str, bool]:
    """
    Fonction helper pour envoyer une notification d'alerte
    """
    alert = Alert(
        id=f"alert_{datetime.now().timestamp()}",
        camera_id=camera_id,
        camera_name=camera_name,
        alert_type=alert_type,
        severity=AlertSeverity(severity),
        message=message,
        timestamp=datetime.now(),
        snapshot_base64=snapshot_base64
    )
    
    return await notification_manager.send_alert(alert)
