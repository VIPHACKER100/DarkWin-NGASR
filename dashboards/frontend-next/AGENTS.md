# DARKWIN Agentic Architecture

The DARKWIN dashboard utilizes a multi-agent orchestration pattern to visualize and manage autonomous security research.

## Agents & Sub-Systems

### 1. The Strategist (Agentic Loop)
*   **Role**: Tactical decision making.
*   **Location**: `core/agent_loop.py`
*   **Function**: Analyzes current findings and selects the next best module to execute.

### 2. The Watchtower (Mesh Manager)
*   **Role**: Infrastructure health & node discovery.
*   **Location**: `core/mesh_manager.py`
*   **Function**: Manages the heartbeat and registration of distributed scanning nodes.

### 3. The Cartographer (Neural Map)
*   **Role**: Attack surface visualization.
*   **Location**: `dashboards/frontend-next/src/components/AttackSurfaceGraph.tsx`
*   **Function**: Maps relational data between targets and findings in 3D space.

### 4. The Ghost (Stealth Engine)
*   **Role**: Anonymity & Evasion.
*   **Location**: `core/stealth.py`
*   **Function**: Obfuscates scanning signatures via fingerprinting and proxy rotation.

### 5. The Sentinel (Vulnerability Verifier)
*   **Role**: Quality Control & Verification.
*   **Location**: `core/vuln_verifier.py`
*   **Function**: Automatically verifies discovered vulnerabilities to eliminate false positives.

---

## Maintenance
Keep your agents up to date with the latest tactical definitions:
```bash
python core/darkwin.py update
```
