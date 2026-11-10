import ipaddress
import socket
from urllib.parse import urlparse

def is_safe_url(url: str) -> tuple[bool, str]:
    """
    Validates that a URL does not resolve to a private, loopback, or reserved IP.
    Prevents SSRF attacks (e.g., accessing localhost, 169.254.169.254 cloud metadata).
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False, "Only HTTP and HTTPS protocols are allowed."

        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid URL: missing hostname."

        # Resolve hostname to IPs (handles DNS rebinding to some extent)
        # We check ALL resolved IPs. If ANY are private, we block it.
        addr_info = socket.getaddrinfo(hostname, None)
        
        for info in addr_info:
            ip = info[4][0]
            ip_obj = ipaddress.ip_address(ip)
            if (ip_obj.is_private or ip_obj.is_loopback or 
                ip_obj.is_link_local or ip_obj.is_reserved or 
                ip_obj.is_multicast):
                return False, f"Blocked IP range: {ip}"

        return True, "OK"
    except Exception as e:
        return False, f"URL validation error: {str(e)}"
