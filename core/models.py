"""DARKWIN SQLAlchemy ORM Models

Defines data models for storing scan results, findings, targets, and reports.
Each model represents a database table with relationships for data integrity.

Models:
    Target: Security target (domain/IP) for scanning
    Scan: Individual scan execution record
    Finding: Discovered vulnerability or security issue
    Screenshot: Captured evidence from web scanning
    Report: Generated security report
    
Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship

from core.database import Base


class Target(Base):
    """Security scanning target (domain or IP address).
    
    Attributes:
        id: Primary key, auto-increment integer
        domain: Target domain or IP address (unique)
        scope_confirmed: Whether target is authorized for scanning
        created_at: Timestamp of target creation
        scans: Relationship to associated Scan records
    """
    __tablename__ = "targets"

    id: int = Column(Integer, primary_key=True, index=True)
    domain: str = Column(String, unique=True, index=True, nullable=False)
    scope_confirmed: bool = Column(Boolean, default=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    # Relationships
    scans: List['Scan'] = relationship("Scan", back_populates="target")


class Scan(Base):
    """Security scan execution record.
    
    Attributes:
        id: Primary key, UUID or custom scan ID
        target_id: Foreign key to Target
        scan_type: Type of scan (recon, full, bug-bounty)
        status: Current scan status (pending, running, completed, failed)
        started_at: Scan start timestamp
        finished_at: Scan completion timestamp
        target: Relationship to Target
        findings: Relationship to Finding records
        screenshots: Relationship to Screenshot records
    """
    __tablename__ = "scans"

    id: str = Column(String, primary_key=True, index=True)
    target_id: int = Column(Integer, ForeignKey("targets.id"), nullable=False)
    scan_type: Optional[str] = Column(String, nullable=True)
    status: str = Column(String, default="pending", index=True)
    started_at: datetime = Column(DateTime, default=datetime.utcnow)
    finished_at: Optional[datetime] = Column(DateTime, nullable=True)

    # Relationships
    target: Target = relationship("Target", back_populates="scans")
    findings: List['Finding'] = relationship("Finding", back_populates="scan")
    screenshots: List['Screenshot'] = relationship("Screenshot", back_populates="scan")


class Finding(Base):
    """Discovered vulnerability or security issue.
    
    Attributes:
        id: Primary key, auto-increment
        scan_id: Foreign key to Scan
        vuln_type: Vulnerability type (sqli, xss, rce, etc.)
        severity: Severity level (Critical, High, Medium, Low, Info)
        endpoint: Affected endpoint or URL
        payload: Payload or attack vector used
        description: Detailed finding description
        cvss_score: CVSS severity score (optional)
        false_positive: Whether finding is confirmed as false positive
        created_at: Finding discovery timestamp
        scan: Relationship to parent Scan
    """
    __tablename__ = "findings"

    id: int = Column(Integer, primary_key=True, index=True)
    scan_id: str = Column(String, ForeignKey("scans.id"), nullable=False, index=True)
    vuln_type: str = Column(String, nullable=False, index=True)
    severity: str = Column(String, nullable=False, index=True)
    endpoint: str = Column(String, nullable=True)
    payload: str = Column(String, nullable=True)
    description: str = Column(String, nullable=True)
    cvss_score: Optional[float] = Column(Float, nullable=True)
    false_positive: bool = Column(Boolean, default=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    scan: Scan = relationship("Scan", back_populates="findings")


class Screenshot(Base):
    """Captured evidence from web scanning.
    
    Attributes:
        id: Primary key, auto-increment
        scan_id: Foreign key to Scan
        url: URL of captured page
        filepath: Local file path to screenshot
        created_at: Screenshot capture timestamp
        scan: Relationship to parent Scan
    """
    __tablename__ = "screenshots"

    id: int = Column(Integer, primary_key=True, index=True)
    scan_id: str = Column(String, ForeignKey("scans.id"), nullable=False, index=True)
    url: str = Column(String, nullable=False)
    filepath: str = Column(String, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    # Relationships
    scan: Scan = relationship("Scan", back_populates="screenshots")


class Report(Base):
    """Generated security report.
    
    Attributes:
        id: Primary key, auto-increment
        scan_id: Foreign key to Scan
        format: Report format (html, pdf, md)
        filepath: Local file path to generated report
        generated_at: Report generation timestamp
    """
    __tablename__ = "reports"

    id: int = Column(Integer, primary_key=True, index=True)
    scan_id: str = Column(String, ForeignKey("scans.id"), nullable=False, index=True)
    format: str = Column(String, nullable=False)
    filepath: str = Column(String, nullable=False)
    generated_at: datetime = Column(DateTime, default=datetime.utcnow)
