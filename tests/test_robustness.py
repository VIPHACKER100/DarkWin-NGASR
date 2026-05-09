import pytest
import json
from core.agent_loop import AgenticLoop
from core.compliance.scope_enforcer import ScopeEnforcer

def test_robust_json_parsing():
    loop = AgenticLoop(target="example.com", scan_id=1)
    
    # Test case 1: Clean JSON
    clean_json = '{"plan": [{"step": "test"}]}'
    assert loop._robust_json_parse(clean_json) == {"plan": [{"step": "test"}]}
    
    # Test case 2: JSON with Markdown code blocks
    markdown_json = '```json\n{"plan": [{"step": "markdown"}]}\n```'
    assert loop._robust_json_parse(markdown_json) == {"plan": [{"step": "markdown"}]}
    
    # Test case 3: JSON with trailing garbage
    garbage_json = '{"plan": [{"step": "garbage"}]} Here is some extra text that might break things.'
    assert loop._robust_json_parse(garbage_json) == {"plan": [{"step": "garbage"}]}

def test_scope_enforcer_cidr(tmp_path):
    scope_file = tmp_path / "scope.json"
    scope_data = {
        "authorized_ips": ["192.168.1.0/24"],
        "excluded_ips": ["192.168.1.50"]
    }
    with open(scope_file, "w") as f:
        json.dump(scope_data, f)
        
    enforcer = ScopeEnforcer(str(scope_file))
    
    assert enforcer.is_in_scope("192.168.1.1") is True
    assert enforcer.is_in_scope("192.168.1.50") is False

    assert enforcer.is_in_scope("192.168.2.1") is False

def test_scope_enforcer_paths(tmp_path):
    scope_file = tmp_path / "scope.json"
    scope_data = {
        "authorized_domains": ["example.com"],
        "excluded_paths": ["/admin", "/login"]
    }
    with open(scope_file, "w") as f:
        json.dump(scope_data, f)
        
    enforcer = ScopeEnforcer(str(scope_file))
    
    assert enforcer.is_in_scope("https://example.com/blog") is True
    assert enforcer.is_in_scope("https://example.com/admin") is False
    assert enforcer.is_in_scope("https://example.com/admin/settings") is False

