"""DARKWIN Base Module Class

Defines the interface and common functionality for all security
research modules.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: MIT
"""

import asyncio
from typing import Dict, Any, List, Optional
from core.database import SessionLocal
from core.models import Finding
from core.logging_system import get_logger

class BaseModule:
    """Base class for all DARKWIN modules."""

    def __init__(self, target: str, scan_id: str) -> None:
        self.target = target
        self.scan_id = scan_id
        self.logger = get_logger(self.__class__.__name__, scan_id=scan_id)

    def log(self, msg: str) -> None:
        """Log an info message with the module logger."""
        self.logger.info(msg)

    def add_finding(self, vuln_type: str, severity: str, endpoint: str,
                    description: str, payload: Optional[str] = None) -> None:
        """Record a security finding and trigger automated verification.

        Args:
            vuln_type: Type of vulnerability (e.g. "xss", "sqli").
            severity: Severity level (Critical, High, Medium, Low).
            endpoint: The URL or endpoint where the finding was discovered.
            description: Human-readable description.
            payload: Optional proof-of-concept payload.
        """
        with SessionLocal() as db:
            finding = Finding(
                scan_id=self.scan_id,
                vuln_type=vuln_type,
                severity=severity,
                endpoint=endpoint,
                description=description,
                payload=payload
            )
            db.add(finding)
            db.commit()
            self.logger.info(f"New Finding: [{severity}] {vuln_type}")

            # Trigger background verification
            asyncio.create_task(self._verify_finding(finding.id, vuln_type, endpoint, payload))

    async def _verify_finding(self, finding_id: int, vuln_type: str, endpoint: str, payload: Optional[str]) -> None:
        """Internal helper to run verification and notify on confirmed findings."""
        from core.vuln_verifier import VulnVerifier
        verifier = VulnVerifier()
        is_verified = await verifier.verify(vuln_type, endpoint, payload or "")

        if is_verified:
            with SessionLocal() as db:
                f = db.query(Finding).filter(Finding.id == finding_id).first()
                if f:
                    f.verified = True
                    db.commit()
                    self.logger.info(f"Verified Finding ID {finding_id}: {vuln_type}")

                    if f.severity in ["Critical", "High"]:
                        from core.notification_manager import global_notifier
                        msg = f"Verified {f.vuln_type} found on {f.endpoint}\nDescription: {f.description}"
                        asyncio.create_task(global_notifier.send_alert(f.vuln_type, msg, f.severity))

    async def run(self, *args: Any, **kwargs: Any) -> None:
        """Main execution logic to be implemented by child modules."""
        raise NotImplementedError("Module must implement run() method.")
