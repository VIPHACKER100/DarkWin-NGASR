import dns.resolver
import os
from typing import List, Dict

MODULE_META = {
    "name": "DNS Bruteforcer",
    "category": "Reconnaissance",
    "description": "Bruteforces subdomains using a wordlist",
    "version": "1.0.0"
}

def run(target: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Bruteforces subdomains using wordlists/subdomains.txt.
    """
    subdomains = []
    wordlist_path = os.path.join("wordlists", "subdomains.txt")
    
    if not os.path.exists(wordlist_path):
        return []

    resolver = dns.resolver.Resolver()
    resolver.timeout = 2
    resolver.lifetime = 2

    try:
        with open(wordlist_path, 'r') as f:
            for line in f:
                sub = line.strip()
                if not sub: continue
                full_domain = f"{sub}.{target}"
                try:
                    answers = resolver.resolve(full_domain, 'A')
                    ips = [str(rdata) for rdata in answers]
                    subdomains.append({
                        "subdomain": full_domain,
                        "ips": ips,
                        "source": "bruteforce",
                        "scan_id": scan_id
                    })
                except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
                    continue
    except Exception as e:
        pass
    
    return subdomains
