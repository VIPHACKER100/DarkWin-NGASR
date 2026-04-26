import time
import datetime
from dataclasses import dataclass, field
from typing import List, Callable, Dict, Any, Optional
from core.logging_system import get_logger
from core.database import SessionLocal
from core.models import Scan

@dataclass
class PipelineStep:
    name: str
    module_fn: Callable
    args: List[Any] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 3600
    required: bool = True

class Pipeline:
    def __init__(self, name: str, steps: List[PipelineStep] = None):
        self.name = name
        self.steps = steps or []
        self.logger = get_logger(f"Pipeline.{name}")

    def add_step(self, step: PipelineStep):
        self.steps.append(step)

    def run(self, target: str, scan_id: str):
        self.logger.info(f"Starting pipeline '{self.name}' for target: {target}")
        
        with SessionLocal() as db:
            scan = db.query(Scan).filter(Scan.id == scan_id).first()
            if not scan:
                self.logger.error(f"Scan ID {scan_id} not found in database.")
                return
            
            scan.status = "running"
            db.commit()

            try:
                for step in self.steps:
                    self.logger.info(f"Executing step: {step.name}")
                    step_start_time = time.time()
                    
                    try:
                        # In a real implementation, we might use subprocess or the module's run()
                        # For now, we assume module_fn is the entry point
                        result = step.module_fn(*step.args, **step.kwargs)
                        
                        # Persist results if module returned findings
                        if isinstance(result, list):
                            from core.models import Finding
                            for f_data in result:
                                try:
                                    finding = Finding(
                                        scan_id=scan_id,
                                        vuln_type=f_data.get("vuln_type", f_data.get("type", "unknown")),
                                        severity=f_data.get("severity", "Info"),
                                        description=f_data.get("description", f_data.get("detail", "")),
                                        endpoint=f_data.get("endpoint", target),
                                        payload=f_data.get("payload", ""),
                                        remediation=f_data.get("remediation", "")
                                    )
                                    db.add(finding)
                                except Exception as fe:
                                    self.logger.error(f"Failed to save finding: {fe}")
                            db.commit()
                        
                        self.logger.info(f"Step '{step.name}' completed in {time.time() - step_start_time:.2f}s")
                        
                    except Exception as e:
                        self.logger.error(f"Step '{step.name}' failed: {e}")
                        if step.required:
                            self.logger.critical(f"Required step '{step.name}' failed. Aborting pipeline.")
                            scan.status = "failed"
                            db.commit()
                            return
                        else:
                            self.logger.warning(f"Non-required step '{step.name}' failed. Continuing.")

                scan.status = "completed"
                scan.finished_at = datetime.datetime.utcnow()
                db.commit()
                self.logger.info(f"Pipeline '{self.name}' completed successfully.")

            except Exception as e:
                self.logger.error(f"Pipeline execution error: {e}")
                scan.status = "failed"
                db.commit()
