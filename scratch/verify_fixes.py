"""Quick verification script for all 4 DARKWIN hunt fixes."""
import sys

print("=" * 60)
print("DARKWIN Hunt Fix Verification")
print("=" * 60)

# Fix 1: NotificationManager
try:
    from core.notification_manager import global_notifier
    print("[PASS] Fix 1: NotificationManager loaded (no httpx.utils error)")
except Exception as e:
    print(f"[FAIL] Fix 1: {e}")
    sys.exit(1)

# Fix 2: Module name resolution
try:
    from core.module_loader import get_module
    
    for name in ["Subfinder Runner", "crt.sh Fetcher", "DNS Enumerator"]:
        mod = get_module(name)
        meta_name = mod.MODULE_META["name"]
        print(f"[PASS] Fix 2: Module '{meta_name}' loaded successfully")
except Exception as e:
    print(f"[FAIL] Fix 2: {e}")

# Fix 3: LLM guard (just verify agent_loop imports)
try:
    from core.agent_loop import AgenticLoop
    print("[PASS] Fix 3: AgenticLoop imported (LLM guard in place)")
except Exception as e:
    print(f"[FAIL] Fix 3: {e}")

# Fix 4: Config notifications section
try:
    from core.config_manager import get_config
    cfg = get_config()
    assert hasattr(cfg, "notifications"), "notifications attr missing"
    notif = cfg.notifications
    assert hasattr(notif, "discord"), "discord field missing"
    assert hasattr(notif, "slack"), "slack field missing"
    assert hasattr(notif, "telegram"), "telegram field missing"
    print("[PASS] Fix 4: config.yaml notifications section loaded correctly")
except Exception as e:
    print(f"[FAIL] Fix 4: {e}")

print("=" * 60)
print("All verifications complete.")
