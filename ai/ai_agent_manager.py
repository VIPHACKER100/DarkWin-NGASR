import httpx
from core.config_manager import get_config
from core.logging_system import get_logger

logger = get_logger("AI.AgentManager")

class AIAgentManager:
    def __init__(self):
        self.config = get_config()
        self.api_url = self.config.ai.local_llm_url
        self.api_key = self.config.ai.openai_api_key

    def ask_agent(self, prompt: str, system_prompt: str = "You are DARKWIN AI, an elite security researcher.") -> str:
        """
        Queries the configured LLM (OpenAI or Local) for analysis.
        """
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        payload = {
            "model": self.config.ai.openai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(self.api_url, json=payload, headers=headers)
                if response.status_code == 200:
                    return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"AI Agent query failed: {e}")
            return f"Error: {e}"
        
        return ""

def analyze_vulnerability(finding: dict):
    manager = AIAgentManager()
    prompt = f"Analyze this vulnerability: {finding}. Provide potential impact and exploitation vector."
    return manager.ask_agent(prompt)
