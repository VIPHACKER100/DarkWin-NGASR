import dns.resolver
from typing import List, Dict

MODULE_META = {
    "name": "DNS Enumerator",
    "category": "Reconnaissance",
    "description": "Performs standard DNS record lookups (A, AAAA, MX, NS, TXT, CNAME, SOA)",
    "version": "1.0.0"
}

def run(target: str, scan_id: str, config: dict) -> List[Dict]:
    """
    Performs DNS lookups for common record types.
    """
    records = []
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
    
    resolver = dns.resolver.Resolver()
    resolver.timeout = 5
    resolver.lifetime = 5

    for r_type in record_types:
        try:
            answers = resolver.resolve(target, r_type)
            for rdata in answers:
                records.append({
                    "type": r_type,
                    "value": str(rdata),
                    "scan_id": scan_id
                })
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.Timeout):
            continue
        except Exception:
            continue
            
    return records
