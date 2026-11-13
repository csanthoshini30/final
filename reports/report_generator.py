"""
PDF Report Generation Module
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
from pathlib import Path
from config.config import REPORTS_DIR

class ReportGenerator:
    """Generate PDF reports for maintenance assessments"""

    def __init__(self):
        self.reports_dir = REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='Heading1_Custom',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=30,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='Heading2_Custom',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#003366'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='Normal_Custom',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6
        ))

    def generate_maintenance_report(self, coordinator_result, subsystem_results, filename=None):
        """Generate comprehensive maintenance report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.reports_dir / f"Maintenance_Report_{timestamp}.pdf"
        else:
            filename = self.reports_dir / filename

        doc = SimpleDocTemplate(str(filename), pagesize=letter)
        story = []

        # Title Page
        story.append(Paragraph("AIRCRAFT PREDICTIVE MAINTENANCE SYSTEM", self.styles['Heading1_Custom']))
        story.append(Paragraph("Maintenance Assessment Report", self.styles['Heading2_Custom']))
        story.append(Spacer(1, 0.3*inch))

        # Report Info
        report_info = [
            ['Report Date:', datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ['Overall Health Score:', f"{coordinator_result['overall_health']}%"],
            ['Overall Risk Level:', coordinator_result['overall_risk']],
            ['Priority Action:', coordinator_result['priority']]
        ]

        info_table = Table(report_info, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#0066cc')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(info_table)
        story.append(Spacer(1, 0.5*inch))

        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['Heading2_Custom']))

        summary_text = f"""
        This report provides a comprehensive assessment of aircraft system health and maintenance
        recommendations. The overall health score of {coordinator_result['overall_health']}% indicates
        {self._get_health_summary(coordinator_result['overall_health'])}.
        The {coordinator_result['priority']} subsystem requires immediate attention.
        """
        story.append(Paragraph(summary_text, self.styles['Normal_Custom']))
        story.append(Spacer(1, 0.3*inch))

        # Subsystem Analysis
        story.append(Paragraph("Subsystem Health Analysis", self.styles['Heading2_Custom']))

        for subsystem_name, subsystem_data in subsystem_results.items():
            story.append(Paragraph(f"{subsystem_name.title()} System", self.styles['Heading2_Custom']))

            subsystem_info = [
                ['Health Score:', f"{subsystem_data['health_score']}%"],
                ['Fault Type:', subsystem_data['fault']],
                ['Risk Level:', subsystem_data['risk']],
                ['RUL Prediction:', f"{subsystem_data['rul']} hours"],
                ['Anomaly Detected:', 'Yes' if subsystem_data['anomaly'] else 'No'],
                ['System Status:', subsystem_data['status']]
            ]

            subsys_table = Table(subsystem_info, colWidths=[2*inch, 4*inch])
            subsys_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#003366')),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey)
            ]))

            story.append(subsys_table)
            story.append(Spacer(1, 0.2*inch))

        story.append(PageBreak())

        # Maintenance Recommendations
        story.append(Paragraph("Maintenance Recommendations", self.styles['Heading2_Custom']))

        if coordinator_result['recommendations']:
            for i, rec in enumerate(coordinator_result['recommendations'], 1):
                rec_text = f"""
                <b>{i}. [{rec['priority']}] {rec['subsystem']}</b><br/>
                Action: {rec['action']}<br/>
                """
                if rec.get('rul_warning'):
                    rec_text += f"Note: {rec['rul_warning']}<br/>"

                story.append(Paragraph(rec_text, self.styles['Normal_Custom']))
                story.append(Spacer(1, 0.1*inch))
        else:
            story.append(Paragraph("No immediate maintenance actions required.", self.styles['Normal_Custom']))

        story.append(Spacer(1, 0.3*inch))

        # Quality Assurance
        story.append(Paragraph("Next Steps", self.styles['Heading2_Custom']))

        next_steps = [
            ['Action', 'Timeline', 'Responsibility'],
            ['Verify findings with manual inspection', '24 hours', 'Maintenance Team'],
            ['Schedule system maintenance', '48 hours', 'Operations'],
            ['Monitor system metrics', 'Continuous', 'Monitoring System'],
            ['Follow-up assessment', '7 days', 'Predictive Maintenance']
        ]

        next_steps_table = Table(next_steps, colWidths=[2.5*inch, 1.5*inch, 2.5*inch])
        next_steps_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))

        story.append(next_steps_table)
        story.append(Spacer(1, 0.5*inch))

        # Footer
        story.append(Paragraph(
            f"Generated by Aircraft Predictive Maintenance System | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['Normal_Custom']
        ))

        # Build PDF
        doc.build(story)

        return str(filename)

    def _get_health_summary(self, health_score):
        """Get health summary text"""
        if health_score >= 80:
            return "the system is in good operating condition"
        elif health_score >= 60:
            return "the system shows signs of degradation"
        else:
            return "the system requires immediate maintenance"

    def generate_summary_report(self, assessment_data):
        """Generate quick summary report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.reports_dir / f"Summary_Report_{timestamp}.txt"

        with open(filename, 'w') as f:
            f.write("AIRCRAFT MAINTENANCE ASSESSMENT SUMMARY\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Overall Health: {assessment_data['overall_health']}%\n")
            f.write(f"Risk Level: {assessment_data['overall_risk']}\n")
            f.write(f"Priority: {assessment_data['priority']}\n\n")

            f.write("SUBSYSTEM STATUS:\n")
            f.write("-" * 60 + "\n")

            for name, data in assessment_data['subsystem_results'].items():
                f.write(f"\n{name.upper()}:\n")
                f.write(f"  Health: {data['health_score']}%\n")
                f.write(f"  Fault: {data['fault']}\n")
                f.write(f"  Risk: {data['risk']}\n")
                f.write(f"  RUL: {data['rul']} hours\n")

            f.write("\n" + "=" * 60 + "\n")
            f.write("RECOMMENDATIONS:\n")
            f.write("-" * 60 + "\n")

            for rec in assessment_data['recommendations']:
                f.write(f"[{rec['priority']}] {rec['subsystem']}: {rec['action']}\n")

        return str(filename)
