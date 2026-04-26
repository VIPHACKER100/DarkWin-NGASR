from ai.ai_agent_manager import AIAgentManager

def suggest_remediation(finding: dict):
    """
    Uses AI to generate code-level remediation advice.
    """
    agent = AIAgentManager()
    prompt = f"Vulnerability: {finding.get('vuln_type')}. Context: {finding.get('description')}. Provide a secure code snippet to fix this."
    
    return agent.ask_agent(prompt)
