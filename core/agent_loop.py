"""DARKWIN Agentic Reasoning Loop

Autonomous execution engine that reasons about discoveries and 
dynamically plans the next research steps.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import json
import asyncio
import re
from typing import List, Dict, Any, Optional
from core.logging_system import get_logger
from ai.multi_step_reasoning import ReasoningEngine
from core.module_loader import get_module
from core.pipeline_engine import Pipeline, PipelineStep
from core.database import SessionLocal
from core.models import Scan, Finding

from core.tui_engine import DarkWinTUI
from rich.live import Live
from datetime import datetime

logger = get_logger("AgenticLoop")

class AgenticLoop:
    """Orchestrates an autonomous scanning loop based on AI reasoning.
    
    Attributes:
        target: Target domain or IP
        scan_id: UUID of the current scan
        max_steps: Maximum reasoning iterations to prevent infinite loops
    """
    
    def __init__(self, target: str, scan_id: str, max_steps: int = 5):
        self.target = target
        self.scan_id = scan_id
        self.reasoner = ReasoningEngine()
        self.max_steps = max_steps
        self.current_step = 0

    async def run(self):
        """Execute the agentic loop with real-time TUI."""
        tui = DarkWinTUI(self.target)
        tui.max_steps = self.max_steps
        
        with Live(tui.make_layout(), refresh_per_second=4) as live:
            tui.status = "Initializing..."
            live.update(tui.render())
            
            # 0. Initialize scan status
            with SessionLocal() as db:
                scan = db.query(Scan).filter(Scan.id == self.scan_id).first()
                if scan:
                    scan.status = "running"
                    db.commit()
            
            # Start notification
            from core.notification_manager import global_notifier
            asyncio.create_task(global_notifier.send_alert("Hunt Started", f"Autonomous research initialized for {self.target}"))

            # 1. Initial Step: Baseline Recon
            tui.status = "Baseline Recon"
            tui.reasoning = "Executing initial passive reconnaissance to seed the model..."
            live.update(tui.render())
            
            initial_modules = ["Subfinder", "crt.sh", "DNS Enum"]
            await self.execute_modules(initial_modules)
            
            # 2. Reasoning Loop
            while self.current_step < self.max_steps:
                self.current_step += 1
                tui.step = self.current_step
                tui.status = "Reasoning"
                live.update(tui.render())
                
                # A. Gather context (recent findings)
                context = self.gather_context()
                
                # B. Ask AI for next steps
                plan_json = self.reasoner.perform_reasoning(context)
                
                # C. Parse and extract modules
                try:
                    plan = self._robust_json_parse(plan_json)
                    
                    recommendations = plan.get("recommendations", [])
                    summary = plan.get("summary", "No summary provided")

                    
                    tui.reasoning = summary
                    tui.status = "Executing"
                    
                    # Update findings for UI
                    with SessionLocal() as db:
                        db_findings = db.query(Finding).filter(Finding.scan_id == self.scan_id).all()
                        tui.findings = [{
                            "time": f.created_at.strftime("%H:%M:%S"),
                            "severity": f.severity,
                            "type": f.vuln_type,
                            "endpoint": f.endpoint
                        } for f in db_findings]
                    
                    live.update(tui.render())
                    
                    if not recommendations:
                        tui.status = "Finished"
                        break
                    
                    module_names = [r["module_name"] for r in recommendations if r.get("module_name")]
                    await self.execute_modules(module_names)
                    
                except Exception as e:
                    logger.error(f"💥 Failed to parse AI plan: {e}\nRaw output: {plan_json}")
                    tui.status = "Parsing Error"
                    tui.reasoning = "AI returned malformed plan. Attempting to continue..."
                    live.update(tui.render())
                    await asyncio.sleep(2) # Give user time to see error
                    continue # Try next iteration or loop exit


            tui.status = "Completed"
            live.update(tui.render())
            
            # Finalize scan status
            with SessionLocal() as db:
                scan = db.query(Scan).filter(Scan.id == self.scan_id).first()
                if scan:
                    scan.status = "completed"
                    db.commit()
            
            # Final notification
            from core.notification_manager import global_notifier
            asyncio.create_task(global_notifier.send_alert("Hunt Completed", f"Autonomous scan for {self.target} has finished successfully."))

    def gather_context(self) -> str:
        """Collect all findings so far for the LLM."""
        with SessionLocal() as db:
            findings = db.query(Finding).filter(Finding.scan_id == self.scan_id).all()
            context = f"Target: {self.target}\n"
            context += f"Previous Steps Taken: {self.current_step}\n"
            context += "Findings discovered so far:\n"
            
            if not findings:
                context += "- No significant findings yet.\n"
            else:
                for f in findings:
                    context += f"- [{f.severity}] {f.vuln_type} at {f.endpoint}\n"
            
            return context

    async def execute_modules(self, module_names: List[str]):
        """Run a list of modules as a pipeline step."""
        pipeline = Pipeline(f"AgenticStep-{self.current_step}", [])
        
        for name in module_names:
            try:
                # Load module
                module = get_module(name)
                # Add to pipeline
                pipeline.add_step(PipelineStep(
                    name=name,
                    module_fn=module.run,
                    args=[self.target, self.scan_id, {}]
                ))
            except Exception as e:
                logger.warning(f"⚠️ [AGENT] Skipping module '{name}': {e}")
        
        if pipeline.steps:
            await pipeline.async_run(self.target, self.scan_id)
        else:
            logger.warning("⚠️ [AGENT] No valid modules to execute in this step.")

    def _robust_json_parse(self, raw_text: str) -> Dict[str, Any]:
        """Defensive multi-stage JSON parsing for LLM responses."""
        if not raw_text:
            return {}

        clean_text = raw_text.strip()
        
        # 1. Extract from Markdown code blocks
        if "```json" in clean_text:
            clean_text = clean_text.split("```json")[1].split("```")[0].strip()
        elif "```" in clean_text:
            clean_text = clean_text.split("```")[1].split("```")[0].strip()
        
        # 2. Fix common LLM syntax errors
        # Remove trailing commas in objects/arrays
        clean_text = re.sub(r',\s*([\]}])', r'\1', clean_text)
        # Fix common unquoted keys (optional, but helpful)
        # clean_text = re.sub(r'(\w+):', r'"\1":', clean_text)
        
        try:
            return json.loads(clean_text)
        except json.JSONDecodeError:
            # 3. Aggressive extraction (find first { and last })
            match = re.search(r'(\{.*\})', clean_text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except:
                    pass
            
            logger.error(f"❌ Failed to parse JSON even with aggressive cleaning: {raw_text[:100]}...")
            return {}

