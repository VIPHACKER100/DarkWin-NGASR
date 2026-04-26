import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from core.database import Base

class Target(Base):
    __tablename__ = "targets"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True, nullable=False)
    scope_confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    scans = relationship("Scan", back_populates="target")

class Scan(Base):
    __tablename__ = "scans"

    id = Column(String, primary_key=True, index=True) # UUID or custom ID
    target_id = Column(Integer, ForeignKey("targets.id"))
    scan_type = Column(String) # recon, full, bug-bounty
    status = Column(String, default="pending") # pending, running, completed, failed
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)

    target = relationship("Target", back_populates="scans")
    findings = relationship("Finding", back_populates="scan")
    screenshots = relationship("Screenshot", back_populates="scan")

class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String, ForeignKey("scans.id"))
    vuln_type = Column(String) # sqli, xss, etc.
    severity = Column(String) # Critical, High, Medium, Low, Info
    endpoint = Column(String)
    payload = Column(String)
    description = Column(String)
    cvss_score = Column(Float, nullable=True)
    false_positive = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    scan = relationship("Scan", back_populates="findings")

class Screenshot(Base):
    __tablename__ = "screenshots"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String, ForeignKey("scans.id"))
    url = Column(String)
    filepath = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    scan = relationship("Scan", back_populates="screenshots")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String, ForeignKey("scans.id"))
    format = Column(String) # html, pdf, md
    filepath = Column(String)
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)
