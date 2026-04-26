from ai.ai_agent_manager import AIAgentManager

class ReasoningEngine:
    def __init__(self):
        self.agent = AIAgentManager()

    def perform_reasoning(self, context: str):
        """
        Performs multi-step reasoning to plan next scan steps.
        """
        system_prompt = "You are a tactical reasoning engine for DARKWIN. Plan the next security research steps based on findings."
        prompt = f"Given the current context: {context}. What are the top 3 modules I should run next and why?"
        
        plan = self.agent.ask_agent(prompt, system_prompt=system_prompt)
        return plan
