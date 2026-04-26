import openai
from core.config_manager import get_config

config = get_config()

def is_false_positive(finding: dict, request_response_pair: dict) -> bool:
    """
    Uses AI to determine if a finding is a false positive by analyzing the HTTP traffic.
    """
    if not config.ai.api_key:
        return False
        
    client = openai.OpenAI(api_key=config.ai.api_key)
    
    prompt = f"""
    Evaluate if this security finding is a FALSE POSITIVE.
    
    Finding: {finding.get('vuln_type')}
    Payload: {finding.get('payload')}
    
    HTTP Request:
    {request_response_pair.get('request')}
    
    HTTP Response:
    {request_response_pair.get('response')}
    
    Return only 'TRUE' if it is a false positive, or 'FALSE' if it is a valid finding.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content.strip().upper()
        return "TRUE" in result
    except Exception:
        return False
