import httpx
import re
import socket
import ipaddress
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse
from datetime import datetime
from app.core.config import settings
from app.normalization.schema_models import ExternalLinkItem

logger = logging.getLogger(__name__)

GITHUB_REPO_REGEX = r"github\.com/([a-zA-Z0-9_-]+)/([a-zA-Z0-9_.-]+)"
GITHUB_USER_REGEX = r"github\.com/([a-zA-Z0-9_-]+)/?"

# Concurrency rate-limiting semaphore
CONCURRENCY_LIMIT = 5
_semaphore: Optional[asyncio.Semaphore] = None

def get_semaphore() -> asyncio.Semaphore:
    global _semaphore
    if _semaphore is None:
        _semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    return _semaphore

def is_safe_external_url(url: str) -> Tuple[bool, str]:
    """Validates URL to block SSRF attacks against localhost, cloud metadata, and RFC1918 private IPs."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ["http", "https"]:
            return False, f"Invalid URL scheme '{parsed.scheme}'. Only http/https allowed."

        hostname = parsed.hostname
        if not hostname:
            return False, "Missing hostname in URL."

        # Block well-known localhost / metadata names
        hostname_lower = hostname.lower()
        if hostname_lower in ["localhost", "127.0.0.1", "0.0.0.0", "instance-data", "metadata.google.internal"]:
            return False, f"Access to local or metadata host '{hostname}' is blocked."

        # Resolve IP and verify not in private / loopback / link-local ranges
        try:
            ip_str = socket.gethostbyname(hostname)
            ip = ipaddress.ip_address(ip_str)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
                return False, f"URL resolves to private/restricted IP address {ip_str}."
        except socket.gaierror:
            # Domain cannot be resolved
            return False, f"Domain '{hostname}' could not be resolved."

        return True, "Safe"
    except Exception as e:
        return False, f"URL validation failed: {str(e)}"


async def check_url_liveness(link: ExternalLinkItem) -> ExternalLinkItem:
    """Checks URL liveness with SSRF protection, rate-limiting, GITHUB_TOKEN auth, and 403/429 handling."""
    url = link.url
    if not url.startswith("http"):
        url = "https://" + url

    # SSRF Validation Check
    is_safe, reason = is_safe_external_url(url)
    if not is_safe:
        logger.warning(f"SSRF filter blocked URL '{url}': {reason}")
        link.verified = False
        link.status_code = 403
        link.metadata = {"blocked": True, "reason": reason}
        return link

    headers = {
        "User-Agent": "SmartResumeScreener/1.0 (Evidence Verification Engine)"
    }
    if settings.GITHUB_TOKEN and "github.com" in url:
        headers["Authorization"] = f"Bearer {settings.GITHUB_TOKEN}"

    sem = get_semaphore()
    async with sem:
        try:
            async with httpx.AsyncClient(timeout=4.0, follow_redirects=True) as client:
                gh_repo_match = re.search(GITHUB_REPO_REGEX, url)
                gh_user_match = re.search(GITHUB_USER_REGEX, url)

                if "github.com" in url:
                    link.link_type = "github"
                    if gh_repo_match and gh_repo_match.group(2) not in ["", "followers", "repositories"]:
                        owner, repo = gh_repo_match.group(1), gh_repo_match.group(2).rstrip("/")
                        api_url = f"https://api.github.com/repos/{owner}/{repo}"
                        res = await client.get(api_url, headers=headers)
                        link.status_code = res.status_code
                        if res.status_code == 200:
                            data = res.json()
                            link.verified = True
                            link.last_active = data.get("pushed_at", "")[:7] if data.get("pushed_at") else datetime.utcnow().strftime("%Y-%m")
                            link.metadata = {
                                "type": "repository",
                                "stars": data.get("stargazers_count", 0),
                                "language": data.get("language", "Unknown"),
                                "forks": data.get("forks_count", 0),
                                "description": data.get("description", "")
                            }
                            return link
                        elif res.status_code in [403, 429]:
                            link.verified = None
                            link.metadata = {"rate_limited": True, "notice": "GitHub API rate limit reached"}
                            return link
                        else:
                            link.verified = False
                            return link

                    elif gh_user_match:
                        user = gh_user_match.group(1)
                        api_url = f"https://api.github.com/users/{user}"
                        res = await client.get(api_url, headers=headers)
                        link.status_code = res.status_code
                        if res.status_code == 200:
                            data = res.json()
                            link.verified = True
                            link.last_active = data.get("updated_at", "")[:7] if data.get("updated_at") else datetime.utcnow().strftime("%Y-%m")
                            link.metadata = {
                                "type": "user_profile",
                                "public_repos": data.get("public_repos", 0),
                                "followers": data.get("followers", 0),
                                "bio": data.get("bio", "")
                            }
                            return link
                        elif res.status_code in [403, 429]:
                            link.verified = None
                            link.metadata = {"rate_limited": True, "notice": "GitHub API rate limit reached"}
                            return link
                        else:
                            link.verified = False
                            return link

                # Generic non-GitHub URL check
                res = await client.get(url, headers=headers)
                link.status_code = res.status_code
                if res.status_code in [403, 429]:
                    link.verified = None
                    link.metadata = {"rate_limited": True}
                else:
                    link.verified = (res.status_code >= 200 and res.status_code < 400)
                if link.verified and not link.last_active:
                    link.last_active = datetime.utcnow().strftime("%Y-%m")

        except Exception as e:
            link.verified = False
            link.status_code = 500
            link.metadata = {"error": str(e)}

    return link

async def verify_candidate_links(links: List[ExternalLinkItem]) -> List[ExternalLinkItem]:
    if not links:
        return []
    tasks = [check_url_liveness(l) for l in links]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    return list(results)
