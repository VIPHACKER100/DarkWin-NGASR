"""DARKWIN Pipeline Execution Engine

Orchestrates sequential execution of vulnerability scanning modules,
manages scan state, captures findings, and handles failures gracefully.

Classes:
    PipelineStep: Represents a single step in a pipeline
    Pipeline: Orchestrates execution of multiple steps
    
Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Callable, Dict, Any, Optional

from core.logging_system import get_logger
from core.database import SessionLocal
from core.models import Scan, Finding

logger = get_logger("Pipeline")


@dataclass
class PipelineStep:
    """Represents a single step in a pipeline execution.
    
    Attributes:
        name: Human-readable step name
        module_fn: Callable function that executes the step
        args: Positional arguments to pass to module_fn
        kwargs: Keyword arguments to pass to module_fn
        timeout_seconds: Maximum execution time (default: 1 hour)
        required: Whether step failure aborts pipeline (default: True)
    """
    name: str
    module_fn: Callable
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 3600
    required: bool = True


class Pipeline:
    """Pipeline orchestrator for sequential vulnerability scanning.
    
    Manages execution of multiple scanning modules (steps), captures results,
    stores findings in database, and handles errors gracefully.
    
    Attributes:
        name: Pipeline name (e.g., "recon", "web_vuln", "full_hunt")
        steps: List of PipelineStep objects to execute
        logger: Logger instance for this pipeline
    """
    
    def __init__(self, name: str, steps: Optional[List[PipelineStep]] = None) -> None:
        """Initialize pipeline.
        
        Args:
            name: Pipeline name
            steps: Optional initial list of pipeline steps
        """
        self.name: str = name
        self.steps: List[PipelineStep] = steps or []
        self.logger = get_logger(f"Pipeline.{name}")

    def add_step(self, step: PipelineStep) -> None:
        """Add a step to the pipeline.
        
        Args:
            step: PipelineStep to add
        """
        self.steps.append(step)
        self.logger.debug(f"Added step: {step.name}")

    def run(self, target: str, scan_id: str) -> None:
        """Execute pipeline for a given target.
        
        Orchestrates sequential execution of all steps, captures findings,
        and updates scan status in database.
        
        Args:
            target: Target domain/IP to scan
            scan_id: Unique scan identifier
        """
        self.logger.info(
            f"🚀 Starting pipeline '{self.name}' for target: {target} "
            f"(Scan ID: {scan_id})"
        )
        
        with SessionLocal() as db:
            # Retrieve or verify scan exists
            scan: Optional[Scan] = db.query(Scan).filter(
                Scan.id == scan_id
            ).first()
            
            if not scan:
                self.logger.error(f"❌ Scan ID {scan_id} not found in database.")
                return
            
            # Mark as running
            scan.status = "running"
            db.commit()

            try:
                # Execute each step
                for step in self.steps:
                    self.logger.info(f"▶️  Executing step: {step.name}")
                    step_start_time: float = time.time()
                    
                    try:
                        # Execute module function
                        result: Any = step.module_fn(
                            *step.args, **step.kwargs
                        )
                        
                        # Persist findings if returned
                        if isinstance(result, list):
                            self._save_findings(db, scan_id, result, target)
                        
                        elapsed_time: float = time.time() - step_start_time
                        self.logger.info(
                            f"✅ Step '{step.name}' completed in {elapsed_time:.2f}s"
                        )
                        
                    except TimeoutError as e:
                        self.logger.error(
                            f"⏱️  Step '{step.name}' timed out: {e}"
                        )
                        if step.required:
                            self.logger.critical(
                                f"Required step '{step.name}' failed. Aborting."
                            )
                            scan.status = "failed"
                            db.commit()
                            return
                        else:
                            self.logger.warning(
                                f"Non-required step '{step.name}' failed. Continuing."
                            )
                            
                    except Exception as e:
                        self.logger.error(f"❌ Step '{step.name}' failed: {e}")
                        if step.required:
                            self.logger.critical(
                                f"Required step '{step.name}' failed. Aborting."
                            )
                            scan.status = "failed"
                            db.commit()
                            return
                        else:
                            self.logger.warning(
                                f"Non-required step '{step.name}' failed. Continuing."
                            )

                # Mark pipeline as completed
                scan.status = "completed"
                scan.finished_at = datetime.utcnow()
                db.commit()
                self.logger.info(
                    f"✨ Pipeline '{self.name}' completed successfully."
                )

            except Exception as e:
                self.logger.critical(
                    f"💥 Pipeline execution error: {e}", exc_info=True
                )
                scan.status = "failed"
                scan.finished_at = datetime.utcnow()
                db.commit()

    def _save_findings(
        self, db, scan_id: str, findings_list: List[Dict[str, Any]], target: str
    ) -> None:
        """Save discovered findings to database.
        
        Args:
            db: Database session
            scan_id: Associated scan ID
            findings_list: List of finding dictionaries from module
            target: Target that was scanned
        """
        for finding_data in findings_list:
            try:
                finding: Finding = Finding(
                    scan_id=scan_id,
                    vuln_type=finding_data.get(
                        "vuln_type", finding_data.get("type", "unknown")
                    ),
                    severity=finding_data.get("severity", "Info"),
                    description=finding_data.get(
                        "description", finding_data.get("detail", "")
                    ),
                    endpoint=finding_data.get("endpoint", target),
                    payload=finding_data.get("payload", ""),
                    cvss_score=finding_data.get("cvss_score"),
                )
                db.add(finding)
                self.logger.debug(
                    f"Found: {finding_data['vuln_type']} at {finding_data.get('endpoint', target)}"
                )
                
            except Exception as e:
                self.logger.error(f"Failed to save finding: {e}")
        
        db.commit()
        self.logger.info(f"💾 Saved {len(findings_list)} findings to database")
