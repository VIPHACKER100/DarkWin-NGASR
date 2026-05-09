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

from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column

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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    domain: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    scope_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    scans: Mapped[List['Scan']] = relationship("Scan", back_populates="target")


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

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    target_id: Mapped[int] = mapped_column(Integer, ForeignKey("targets.id"), nullable=False)
    scan_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending", index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    target: Mapped[Target] = relationship("Target", back_populates="scans")
    findings: Mapped[List['Finding']] = relationship("Finding", back_populates="scan")
    screenshots: Mapped[List['Screenshot']] = relationship("Screenshot", back_populates="scan")


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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scan_id: Mapped[str] = mapped_column(String, ForeignKey("scans.id"), nullable=False, index=True)
    vuln_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    severity: Mapped[str] = mapped_column(String, nullable=False, index=True)
    endpoint: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    payload: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cvss_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    false_positive: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    # Relationships
    scan: Mapped[Scan] = relationship("Scan", back_populates="findings")


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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scan_id: Mapped[str] = mapped_column(String, ForeignKey("scans.id"), nullable=False, index=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    filepath: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    scan: Mapped[Scan] = relationship("Scan", back_populates="screenshots")


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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    scan_id: Mapped[str] = mapped_column(String, ForeignKey("scans.id"), nullable=False, index=True)
    format: Mapped[str] = mapped_column(String, nullable=False)
    filepath: Mapped[str] = mapped_column(String, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
