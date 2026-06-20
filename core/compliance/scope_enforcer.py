"""DARKWIN Scope Enforcer compliance module.

Enforces scanning scope boundaries (domains, CIDR IP ranges, path exclusions)
to ensure legal and policy compliance.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import json
import ipaddress
import re
from pathlib import Path
from typing import List, Optional

from core.logging_system import get_logger

logger = get_logger("Compliance.ScopeEnforcer")


class ScopeEnforcer:
    """Enforces scanning scope boundaries to ensure legal compliance.

    Supports domain wildcards, CIDR IP ranges, and specific path exclusions.
    """

    def __init__(self, scope_file: str) -> None:
        self.scope_file = scope_file
        self.authorized_domains: List[str] = []
        self.authorized_ips: List[ipaddress.IPv4Network] = []
        self.excluded_ips: List[ipaddress.IPv4Network] = []
        self.excluded_paths: List[str] = []
        self.load_scope()

    def load_scope(self) -> None:
        """Load scope definitions from a JSON file."""
        try:
            data = json.loads(Path(self.scope_file).read_text(encoding="utf-8"))
            self.authorized_domains = data.get("authorized_domains", [])

            for ip_str in data.get("authorized_ips", []):
                try:
                    self.authorized_ips.append(ipaddress.ip_network(ip_str, strict=False))
                except ValueError:
                    logger.error(f"Invalid authorized IP/CIDR in scope: {ip_str}")

            for ip_str in data.get("excluded_ips", []):
                try:
                    self.excluded_ips.append(ipaddress.ip_network(ip_str, strict=False))
                except ValueError:
                    logger.error(f"Invalid excluded IP/CIDR in scope: {ip_str}")

            self.excluded_paths = data.get("excluded_paths", [])
            logger.info(
                f"Loaded scope: {len(self.authorized_domains)} domains, "
                f"{len(self.authorized_ips)} IP ranges, "
                f"{len(self.excluded_ips)} excluded IPs"
            )

        except FileNotFoundError:
            logger.warning(f"Scope file not found: {self.scope_file}. Defaulting to empty scope.")
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Failed to load scope file: {e}")

    def is_in_scope(self, target: str) -> bool:
        """Checks if a target (domain, IP, or URL) is within the authorized scope."""
        # 1. Check if specific path is excluded (if target is a URL)
        if "://" in target and self.is_path_excluded(target):
            return False

        # 2. Check if it's an IP/CIDR
        try:
            ip_obj = ipaddress.ip_address(target)
            
            if self.excluded_ips:
                for ex_network in self.excluded_ips:
                    if ip_obj in ex_network:
                        logger.warning(f"BLOCKED: IP '{target}' is specifically EXCLUDED.")
                        return False

            for network in self.authorized_ips:
                if ip_obj in network:
                    return True
        except ValueError:
            # Not an IP, treat as domain or URL
            pass

        # 3. Check domains
        target_domain = target.split("://")[-1].split("/")[0].split(":")[0]
        
        for auth_domain in self.authorized_domains:
            if auth_domain == target_domain:
                return True
            
            # Wildcard support (*.example.com)
            if auth_domain.startswith("*."):
                suffix = auth_domain[1:] # .example.com
                if target_domain.endswith(suffix):
                    return True
            
            # Regex support (if defined in scope as /regex/)
            if auth_domain.startswith("/") and auth_domain.endswith("/"):
                pattern = auth_domain[1:-1]
                if re.search(pattern, target_domain):
                    return True

        logger.warning(f"BLOCKED: Target '{target}' is NOT in authorized scope.")
        return False

    def is_path_excluded(self, url: str) -> bool:
        """Check if a URL path is excluded from scanning."""
        for path in self.excluded_paths:
            if path in url:
                logger.info(f"PATH EXCLUDED: URL '{url}' contains excluded path '{path}'")
                return True
        return False

