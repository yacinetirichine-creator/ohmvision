"""
OhmVision - PDF Report Generator
Génération automatique de rapports professionnels
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether
)
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from io import BytesIO
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import base64
import logging

logger = logging.getLogger(__name__)


class ReportType(str, Enum):
    """Types de rapports disponibles"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    INCIDENT = "incident"
    COMPLIANCE = "compliance"
    EXECUTIVE = "executive"
    CUSTOM = "custom"


@dataclass
class ReportData:
    """Données pour la génération de rapport"""
    report_type: ReportType
    title: str
    period_start: datetime
    period_end: datetime
    
    # Métriques générales
    total_alerts: int = 0
    critical_alerts: int = 0
    cameras_online: int = 0
    cameras_total: int = 0
    
    # Détails par type d'alerte
    alerts_by_type: Dict[str, int] = None
    alerts_by_camera: Dict[str, int] = None
    alerts_by_hour: Dict[int, int] = None
    alerts_by_day: Dict[str, int] = None
    
    # Statistiques de comptage
    total_entries: int = 0
    total_exits: int = 0
    peak_occupancy: int = 0
    avg_occupancy: float = 0.0
    
    # Conformité (industrie)
    ppe_compliance_rate: float = 0.0
    safety_incidents: int = 0
    near_misses: int = 0
    
    # Liste des incidents majeurs
    major_incidents: List[Dict] = None
    
    # Images/Snapshots
    sample_snapshots: List[str] = None  # base64
    
    # Insights IA
    ai_insights: List[str] = None
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.alerts_by_type is None:
            self.alerts_by_type = {}
        if self.alerts_by_camera is None:
            self.alerts_by_camera = {}
        if self.alerts_by_hour is None:
            self.alerts_by_hour = {}
        if self.alerts_by_day is None:
            self.alerts_by_day = {}
        if self.major_incidents is None:
            self.major_incidents = []
        if self.sample_snapshots is None:
            self.sample_snapshots = []
        if self.ai_insights is None:
            self.ai_insights = []
        if self.recommendations is None:
            self.recommendations = []


class PDFReportGenerator:
    """
    Générateur de rapports PDF professionnels
    """
    
    # Couleurs OhmVision
    PRIMARY_COLOR = colors.HexColor('#6366f1')
    SECONDARY_COLOR = colors.HexColor('#8b5cf6')
    SUCCESS_COLOR = colors.HexColor('#22c55e')
    WARNING_COLOR = colors.HexColor('#f59e0b')
    DANGER_COLOR = colors.HexColor('#ef4444')
    DARK_COLOR = colors.HexColor('#1e293b')
    LIGHT_COLOR = colors.HexColor('#f1f5f9')
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Configure les styles personnalisés"""
        self.styles.add(ParagraphStyle(
            name='OhmTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.DARK_COLOR,
            spaceAfter=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='OhmHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.PRIMARY_COLOR,
            spaceAfter=12,
            spaceBefore=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='OhmSubHeading',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=self.DARK_COLOR,
            spaceAfter=8
        ))
        
        self.styles.add(ParagraphStyle(
            name='OhmBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.DARK_COLOR,
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='OhmInsight',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.PRIMARY_COLOR,
            leftIndent=20,
            spaceAfter=4
        ))
    
    def generate_report(self, data: ReportData, 
                        output_path: str = None) -> bytes:
        """
        Génère un rapport PDF
        
        Args:
            data: Données du rapport
            output_path: Chemin de sortie (optionnel)
        
        Returns:
            Contenu PDF en bytes
        """
        buffer = BytesIO()
        
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Construire le contenu
        story = []
        
        # En-tête
        story.extend(self._build_header(data))
        
        # Résumé exécutif
        story.extend(self._build_executive_summary(data))
        
        # Métriques clés
        story.extend(self._build_key_metrics(data))
        
        # Graphiques
        story.extend(self._build_charts(data))
        
        # Incidents majeurs
        if data.major_incidents:
            story.extend(self._build_incidents_section(data))
        
        # Insights IA
        if data.ai_insights:
            story.extend(self._build_insights_section(data))
        
        # Recommandations
        if data.recommendations:
            story.extend(self._build_recommendations(data))
        
        # Pied de page
        story.extend(self._build_footer(data))
        
        # Générer le PDF
        doc.build(story)
        
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Sauvegarder si chemin spécifié
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_content)
        
        return pdf_content
    
    def _build_header(self, data: ReportData) -> List:
        """Construit l'en-tête du rapport"""
        elements = []
        
        # Logo et titre
        elements.append(Paragraph(
            "🎥 OhmVision",
            self.styles['OhmTitle']
        ))
        
        elements.append(Paragraph(
            data.title,
            self.styles['OhmHeading']
        ))
        
        # Période
        period_text = f"Période: {data.period_start.strftime('%d/%m/%Y')} - {data.period_end.strftime('%d/%m/%Y')}"
        elements.append(Paragraph(period_text, self.styles['OhmBody']))
        
        elements.append(Paragraph(
            f"Généré le: {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
            self.styles['OhmBody']
        ))
        
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_executive_summary(self, data: ReportData) -> List:
        """Construit le résumé exécutif"""
        elements = []
        
        elements.append(Paragraph("Résumé Exécutif", self.styles['OhmHeading']))
        
        # Calculs
        uptime = (data.cameras_online / data.cameras_total * 100) if data.cameras_total > 0 else 0
        
        summary_text = f"""
        Durant cette période, le système OhmVision a surveillé <b>{data.cameras_total}</b> caméras 
        avec un taux de disponibilité de <b>{uptime:.1f}%</b>. 
        Au total, <b>{data.total_alerts}</b> alertes ont été détectées, 
        dont <b>{data.critical_alerts}</b> alertes critiques.
        """
        
        if data.total_entries > 0:
            summary_text += f"""
            <br/><br/>
            Le comptage a enregistré <b>{data.total_entries}</b> entrées et 
            <b>{data.total_exits}</b> sorties, avec un pic d'occupation de 
            <b>{data.peak_occupancy}</b> personnes.
            """
        
        if data.ppe_compliance_rate > 0:
            summary_text += f"""
            <br/><br/>
            Le taux de conformité EPI est de <b>{data.ppe_compliance_rate:.1f}%</b>.
            <b>{data.safety_incidents}</b> incidents de sécurité ont été enregistrés.
            """
        
        elements.append(Paragraph(summary_text, self.styles['OhmBody']))
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _build_key_metrics(self, data: ReportData) -> List:
        """Construit la section des métriques clés"""
        elements = []
        
        elements.append(Paragraph("Métriques Clés", self.styles['OhmHeading']))
        
        # Tableau des métriques
        metrics_data = [
            ['Métrique', 'Valeur', 'Tendance'],
            ['Alertes totales', str(data.total_alerts), '—'],
            ['Alertes critiques', str(data.critical_alerts), '—'],
            ['Caméras en ligne', f"{data.cameras_online}/{data.cameras_total}", '—'],
        ]
        
        if data.total_entries > 0:
            metrics_data.append(['Entrées', str(data.total_entries), '—'])
            metrics_data.append(['Sorties', str(data.total_exits), '—'])
            metrics_data.append(['Occupation moyenne', f"{data.avg_occupancy:.1f}", '—'])
        
        if data.ppe_compliance_rate > 0:
            metrics_data.append(['Conformité EPI', f"{data.ppe_compliance_rate:.1f}%", '—'])
            metrics_data.append(['Incidents sécurité', str(data.safety_incidents), '—'])
        
        table = Table(metrics_data, colWidths=[6*cm, 4*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.PRIMARY_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), self.LIGHT_COLOR),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.DARK_COLOR),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_charts(self, data: ReportData) -> List:
        """Construit les graphiques"""
        elements = []
        
        elements.append(Paragraph("Analyse Graphique", self.styles['OhmHeading']))
        
        # Graphique: Alertes par type (Pie Chart)
        if data.alerts_by_type:
            elements.append(Paragraph("Répartition des alertes par type", self.styles['OhmSubHeading']))
            
            drawing = Drawing(400, 200)
            pie = Pie()
            pie.x = 100
            pie.y = 25
            pie.width = 150
            pie.height = 150
            pie.data = list(data.alerts_by_type.values())
            pie.labels = list(data.alerts_by_type.keys())
            
            pie.slices.strokeWidth = 0.5
            
            # Couleurs
            colors_list = [self.PRIMARY_COLOR, self.SECONDARY_COLOR, 
                          self.SUCCESS_COLOR, self.WARNING_COLOR, self.DANGER_COLOR]
            for i, _ in enumerate(pie.data):
                pie.slices[i].fillColor = colors_list[i % len(colors_list)]
            
            drawing.add(pie)
            elements.append(drawing)
            elements.append(Spacer(1, 15))
        
        # Graphique: Alertes par heure (Bar Chart)
        if data.alerts_by_hour:
            elements.append(Paragraph("Distribution horaire des alertes", self.styles['OhmSubHeading']))
            
            drawing = Drawing(450, 180)
            chart = VerticalBarChart()
            chart.x = 50
            chart.y = 30
            chart.width = 380
            chart.height = 130
            
            hours = list(range(24))
            values = [data.alerts_by_hour.get(h, 0) for h in hours]
            chart.data = [values]
            chart.categoryAxis.categoryNames = [str(h) for h in hours]
            
            chart.bars[0].fillColor = self.PRIMARY_COLOR
            chart.valueAxis.valueMin = 0
            chart.categoryAxis.labels.fontSize = 8
            
            drawing.add(chart)
            elements.append(drawing)
            elements.append(Spacer(1, 15))
        
        return elements
    
    def _build_incidents_section(self, data: ReportData) -> List:
        """Construit la section des incidents majeurs"""
        elements = []
        
        elements.append(PageBreak())
        elements.append(Paragraph("Incidents Majeurs", self.styles['OhmHeading']))
        
        for i, incident in enumerate(data.major_incidents[:10], 1):
            incident_text = f"""
            <b>{i}. {incident.get('type', 'Incident').upper()}</b> - 
            {incident.get('camera', 'N/A')}<br/>
            <i>{incident.get('timestamp', '')}</i><br/>
            {incident.get('description', '')}
            """
            elements.append(Paragraph(incident_text, self.styles['OhmBody']))
            elements.append(Spacer(1, 10))
        
        return elements
    
    def _build_insights_section(self, data: ReportData) -> List:
        """Construit la section des insights IA"""
        elements = []
        
        elements.append(Paragraph("🤖 Insights Intelligence Artificielle", self.styles['OhmHeading']))
        
        for insight in data.ai_insights:
            elements.append(Paragraph(f"• {insight}", self.styles['OhmInsight']))
        
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _build_recommendations(self, data: ReportData) -> List:
        """Construit la section des recommandations"""
        elements = []
        
        elements.append(Paragraph("📋 Recommandations", self.styles['OhmHeading']))
        
        for i, rec in enumerate(data.recommendations, 1):
            elements.append(Paragraph(f"{i}. {rec}", self.styles['OhmBody']))
        
        elements.append(Spacer(1, 15))
        
        return elements
    
    def _build_footer(self, data: ReportData) -> List:
        """Construit le pied de page"""
        elements = []
        
        elements.append(Spacer(1, 30))
        
        footer_text = """
        <i>Ce rapport a été généré automatiquement par OhmVision.<br/>
        Pour toute question, contactez support@ohmvision.fr</i>
        """
        
        elements.append(Paragraph(footer_text, self.styles['OhmBody']))
        
        return elements
    
    # =========================================================================
    # Rapports Spécifiques
    # =========================================================================
    
    def generate_daily_report(self, 
                              date: datetime,
                              alerts: List[Dict],
                              cameras: List[Dict],
                              counting_data: Dict = None) -> bytes:
        """Génère un rapport journalier"""
        
        # Agréger les données
        alerts_by_type = {}
        alerts_by_hour = {h: 0 for h in range(24)}
        critical_count = 0
        
        for alert in alerts:
            alert_type = alert.get('type', 'unknown')
            alerts_by_type[alert_type] = alerts_by_type.get(alert_type, 0) + 1
            
            hour = datetime.fromisoformat(alert.get('timestamp', '')).hour if alert.get('timestamp') else 0
            alerts_by_hour[hour] += 1
            
            if alert.get('severity') == 'critical':
                critical_count += 1
        
        data = ReportData(
            report_type=ReportType.DAILY,
            title=f"Rapport Journalier - {date.strftime('%d/%m/%Y')}",
            period_start=date.replace(hour=0, minute=0),
            period_end=date.replace(hour=23, minute=59),
            total_alerts=len(alerts),
            critical_alerts=critical_count,
            cameras_online=len([c for c in cameras if c.get('is_online')]),
            cameras_total=len(cameras),
            alerts_by_type=alerts_by_type,
            alerts_by_hour=alerts_by_hour,
            total_entries=counting_data.get('entries', 0) if counting_data else 0,
            total_exits=counting_data.get('exits', 0) if counting_data else 0,
            peak_occupancy=counting_data.get('peak', 0) if counting_data else 0,
            ai_insights=[
                f"Pic d'alertes détecté à {max(alerts_by_hour, key=alerts_by_hour.get)}h",
                f"Type d'alerte le plus fréquent: {max(alerts_by_type, key=alerts_by_type.get) if alerts_by_type else 'N/A'}"
            ],
            recommendations=[
                "Vérifier les caméras hors ligne",
                "Analyser les causes des alertes récurrentes"
            ]
        )
        
        return self.generate_report(data)
    
    def generate_compliance_report(self,
                                   period_start: datetime,
                                   period_end: datetime,
                                   ppe_data: Dict,
                                   incidents: List[Dict]) -> bytes:
        """Génère un rapport de conformité sécurité"""
        
        data = ReportData(
            report_type=ReportType.COMPLIANCE,
            title=f"Rapport de Conformité Sécurité",
            period_start=period_start,
            period_end=period_end,
            ppe_compliance_rate=ppe_data.get('compliance_rate', 0),
            safety_incidents=len([i for i in incidents if i.get('type') == 'safety']),
            near_misses=len([i for i in incidents if i.get('type') == 'near_miss']),
            major_incidents=incidents[:10],
            ai_insights=[
                f"Taux de conformité casque: {ppe_data.get('helmet_rate', 0):.1f}%",
                f"Taux de conformité gilet: {ppe_data.get('vest_rate', 0):.1f}%",
                f"Zone la plus à risque: {ppe_data.get('risky_zone', 'N/A')}"
            ],
            recommendations=[
                "Renforcer les contrôles aux entrées" if ppe_data.get('compliance_rate', 100) < 95 else "Maintenir les bonnes pratiques",
                "Former les équipes sur les procédures de sécurité",
                "Installer des rappels visuels dans les zones à risque"
            ]
        )
        
        return self.generate_report(data)


# Instance globale
report_generator = PDFReportGenerator()
