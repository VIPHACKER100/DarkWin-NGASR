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
import asyncio
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
        """Synchronous wrapper for running the pipeline."""
        asyncio.run(self.async_run(target, scan_id))

    async def async_run(self, target: str, scan_id: str) -> None:
        """Execute pipeline for a given target asynchronously.
        
        Orchestrates parallel execution of non-dependent steps, captures findings,
        and updates scan status in database.
        """
        self.logger.info(
            f"🚀 Starting async pipeline '{self.name}' for target: {target} "
            f"(Scan ID: {scan_id})"
        )
        
        with SessionLocal() as db:
            scan: Optional[Scan] = db.query(Scan).filter(Scan.id == scan_id).first()
            if not scan:
                self.logger.error(f"❌ Scan ID {scan_id} not found in database.")
                return
            
            scan.status = "running"
            db.commit()

            try:
                # For now, we'll run all steps in parallel if they are independent
                # In the future, we could add dependency tracking
                tasks = []
                for step in self.steps:
                    tasks.append(self._execute_step(step, db, scan_id, target))
                
                await asyncio.gather(*tasks)

                scan.status = "completed"
                scan.finished_at = datetime.utcnow()
                db.commit()
                self.logger.info(f"✨ Pipeline '{self.name}' completed successfully.")

            except Exception as e:
                self.logger.critical(f"💥 Pipeline execution error: {e}", exc_info=True)
                scan.status = "failed"
                scan.finished_at = datetime.utcnow()
                db.commit()

    async def _execute_step(self, step: PipelineStep, db, scan_id: str, target: str) -> None:
        """Execute a single step asynchronously."""
        self.logger.info(f"▶️  Executing step: {step.name}")
        step_start_time = time.time()
        
        try:
            # Check if the module function is a coroutine or regular function
            import inspect
            if inspect.iscoroutinefunction(step.module_fn):
                result = await step.module_fn(*step.args, **step.kwargs)
            else:
                # Run blocking sync modules in a thread pool
                result = await asyncio.to_thread(step.module_fn, *step.args, **step.kwargs)
            
            if isinstance(result, list):
                # Save findings (synchronous DB operation, but small enough or could be wrapped)
                self._save_findings(db, scan_id, result, target)
            
            elapsed_time = time.time() - step_start_time
            self.logger.info(f"✅ Step '{step.name}' completed in {elapsed_time:.2f}s")
            
        except Exception as e:
            self.logger.error(f"❌ Step '{step.name}' failed: {e}")
            if step.required:
                raise # Re-raise to be caught by async_run

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
