"""DARKWIN Advanced Reporting Engine

Generates professional security reports with AI-powered executive 
summaries and detailed finding breakdowns.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import os
from datetime import datetime, timezone
from typing import List, Dict, Any
from pathlib import Path

from core.logging_system import get_logger
from core.database import SessionLocal
from core.models import Scan, Finding, Report
from ai.ai_agent_manager import AIAgentManager

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

logger = get_logger("ReportingEngine")

class ReportingEngine:
    """Engine for generating multi-format security reports."""
    
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.ai = AIAgentManager()

    def generate_report(self, scan_id: str, format: str = "md") -> str:
        """Generate a report for a specific scan.
        
        Args:
            scan_id: UUID of the scan
            format: Output format ('md', 'html')
            
        Returns:
            Path to the generated report file.
        """
        logger.info(f"📄 Generating {format.upper()} report for Scan ID: {scan_id}")
        
        with SessionLocal() as db:
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            if not scan:
                raise ValueError(f"Scan ID {scan_id} not found")
            
            findings = db.query(Finding).filter(Finding.scan_id == scan_id).all()
            
            # 1. Generate AI Executive Summary
            summary = self._generate_ai_summary(scan, findings)
            
            # 2. Compile Report Content
            if format == "md":
                content = self._build_markdown(scan, findings, summary)
            elif format == "html":
                content = self._build_html(scan, findings, summary)
            elif format == "pdf":
                if not FPDF:
                    raise ValueError("FPDF library not installed. PDF generation unavailable.")
                return self._build_pdf(scan, findings, summary, scan_id)
            elif format == "docx":
                try:
                    from integrations.docx_generator import DocxReportGenerator
                    generator = DocxReportGenerator(scan.target.domain, scan_id)
                    findings_data = [
                        {
                            'severity': f.severity,
                            'vuln_type': f.vuln_type,
                            'url': f.endpoint,
                            'description': f.description
                        } for f in findings
                    ]
                    return generator.generate(findings_data, summary)
                except ImportError:
                    raise ValueError("python-docx library not installed. DOCX generation unavailable.")
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            # 3. Save to File
            filename = f"report_{scan.target.domain}_{scan_id[:8]}.{format}"
            filepath = self.output_dir / filename
            
            try:
                filepath.write_text(content, encoding='utf-8')
            except UnicodeEncodeError:
                # Fallback for Windows charmap issues
                safe_content = content.encode('ascii', 'ignore').decode('ascii')
                filepath.write_text(safe_content, encoding='utf-8')
            
            # 4. Record in Database
            new_report = Report(
                scan_id=scan_id,
                format=format,
                filepath=str(filepath)
            )
            db.add(new_report)
            db.commit()
            
            logger.info(f"✅ Report saved to: {filepath}")
            return str(filepath)

    def _generate_ai_summary(self, scan: Scan, findings: List[Finding]) -> str:
        """Use AI to synthesize an executive summary of the scan."""
        findings_text = "\n".join([
            f"- [{f.severity}] {f.vuln_type} at {f.endpoint}" for f in findings
        ])
        
        prompt = f"""
        Generate an executive summary for a security scan.
        Target: {scan.target.domain}
        Total Findings: {len(findings)}
        
        Findings List:
        {findings_text}
        
        Provide:
        1. A high-level risk assessment (Critical/High/Medium/Low).
        2. Top 3 most critical issues.
        3. Strategic recommendations for the management team.
        
        Keep it professional, concise, and focused on business risk.
        """
        
        try:
            return self.ai.ask_agent(prompt, system_prompt="You are a Senior Security Consultant.")
        except Exception as e:
            logger.error(f"AI summary generation failed: {e}")
            return "AI summary generation failed. Please review detailed findings below."

    def _build_markdown(self, scan: Scan, findings: List[Finding], summary: str) -> str:
        """Construct a professional Markdown report."""
        md = f"# DARKWIN Security Assessment Report\n\n"
        md += f"**Target:** {scan.target.domain}  \n"
        md += f"**Scan ID:** `{scan.id}`  \n"
        md += f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}  \n\n"
        
        md += "## 1. Executive Summary\n"
        md += f"{summary}\n\n"
        
        md += "## 2. Technical Findings\n"
        if not findings:
            md += "No vulnerabilities were identified during this assessment.\n"
        else:
            for i, f in enumerate(findings, 1):
                md += f"### {i}. {f.vuln_type}\n"
                md += f"- **Severity:** {self._colorize_severity(f.severity)}\n"
                md += f"- **Endpoint:** `{f.endpoint}`\n"
                md += f"- **Description:** {f.description or 'N/A'}\n"
                if f.payload:
                    md += f"- **PoC/Payload:** `{f.payload}`\n"
                md += "\n"
        
        md += "---\n"
        md += "*Generated by DARKWIN-NGASR — Advanced Security Research Platform*\n"
        return md

    def _build_html(self, scan: Scan, findings: List[Finding], summary: str) -> str:
        """Construct a modern HTML report (minimal styling for now)."""
        # In a real app, use a Jinja2 template
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 40px auto; }}
                .critical {{ color: #dc3545; font-weight: bold; }}
                .high {{ color: #fd7e14; font-weight: bold; }}
                .medium {{ color: #ffc107; font-weight: bold; }}
                .header {{ border-bottom: 2px solid #000; padding-bottom: 10px; margin-bottom: 20px; }}
                .finding {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 5px solid #ccc; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>DARKWIN Assessment Report</h1>
                <p>Target: <strong>{scan.target.domain}</strong></p>
                <p>Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}</p>
            </div>
            
            <h2>1. Executive Summary</h2>
            <div style="white-space: pre-wrap;">{summary}</div>
            
            <h2>2. Technical Findings</h2>
        """
        
        for f in findings:
            sev_class = f.severity.lower()
            html += f"""
            <div class="finding" style="border-left-color: {self._get_severity_color(f.severity)};">
                <h3>{f.vuln_type} <span class="{sev_class}">[{f.severity}]</span></h3>
                <p><strong>Endpoint:</strong> {f.endpoint}</p>
                <p>{f.description or 'No description provided.'}</p>
                {f'<p><strong>Payload:</strong> <code>{f.payload}</code></p>' if f.payload else ''}
            </div>
            """
            
        html += """
        </body>
        </html>
        """
        return html

    def _build_pdf(self, scan: Scan, findings: List[Finding], summary: str, scan_id: str) -> str:
        """Construct a professional PDF report."""
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font("helvetica", 'B', 16)
        pdf.cell(190, 10, "DARKWIN Security Assessment Report", ln=True, align='C')
        pdf.ln(10)
        
        # Meta Info
        pdf.set_font("helvetica", '', 10)
        pdf.cell(40, 7, f"Target:", 0)
        pdf.set_font("helvetica", 'B', 10)
        pdf.cell(150, 7, scan.target.domain, ln=True)
        
        pdf.set_font("helvetica", '', 10)
        pdf.cell(40, 7, f"Scan ID:", 0)
        pdf.cell(150, 7, scan.id, ln=True)
        
        pdf.cell(40, 7, f"Date:", 0)
        pdf.cell(150, 7, datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S'), ln=True)
        pdf.ln(10)
        
        # Executive Summary
        pdf.set_font("Arial", 'B', 14)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(190, 10, "1. Executive Summary", ln=True, fill=True)
        pdf.ln(5)
        
        pdf.set_font("helvetica", '', 11)
        # Attempt to handle unicode via 'fpdf2' compatibility or fallback
        try:
            pdf.multi_cell(190, 6, summary)
        except (UnicodeEncodeError, AttributeError):
            pdf.multi_cell(190, 6, summary.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(10)
        
        # Technical Findings
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(190, 10, "2. Technical Findings", ln=True, fill=True)
        pdf.ln(5)
        
        for i, f in enumerate(findings, 1):
            pdf.set_font("helvetica", 'B', 12)
            pdf.cell(190, 8, f"{i}. {f.vuln_type} [{f.severity}]", ln=True)
            
            pdf.set_font("helvetica", '', 10)
            pdf.cell(30, 6, "Endpoint:", 0)
            pdf.set_font("helvetica", 'I', 10)
            pdf.cell(160, 6, str(f.endpoint), ln=True)
            
            pdf.set_font("helvetica", '', 10)
            pdf.cell(30, 6, "Description:", 0)
            desc = f.description or "N/A"
            try:
                pdf.multi_cell(160, 6, desc)
            except (UnicodeEncodeError, AttributeError):
                pdf.multi_cell(160, 6, desc.encode('latin-1', 'replace').decode('latin-1'))
            
            if f.payload:
                pdf.cell(30, 6, "Payload:", 0)
                pdf.set_font("courier", '', 9)
                try:
                    pdf.multi_cell(160, 6, f.payload)
                except (UnicodeEncodeError, AttributeError):
                    pdf.multi_cell(160, 6, f.payload.encode('latin-1', 'replace').decode('latin-1'))
            
            pdf.ln(5)
        
        # Save
        filename = f"report_{scan.target.domain}_{scan_id[:8]}.pdf"
        filepath = self.output_dir / filename
        pdf.output(str(filepath))
        
        # Record in DB
        with SessionLocal() as db:
            new_report = Report(scan_id=scan_id, format="pdf", filepath=str(filepath))
            db.add(new_report)
            db.commit()
            
        return str(filepath)

    def _colorize_severity(self, severity: str) -> str:
        colors = {
            "Critical": "🔴 **Critical**",
            "High": "🟠 **High**",
            "Medium": "🟡 **Medium**",
            "Low": "🟢 **Low**",
            "Info": "🔵 **Info**"
        }
        return colors.get(severity, severity)

    def _get_severity_color(self, severity: str) -> str:
        colors = {
            "Critical": "#dc3545",
            "High": "#fd7e14",
            "Medium": "#ffc107",
            "Low": "#28a745",
            "Info": "#17a2b8"
        }
        return colors.get(severity, "#ccc")
