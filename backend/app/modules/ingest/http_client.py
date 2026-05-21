from __future__ import annotations

import sys
from functools import lru_cache

import httpx

_DEFAULT_HEADERS = {
    "User-Agent": "IntelHub/0.1 (+https://github.com/intel-hub)",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}


@lru_cache(maxsize=1)
def resolve_http_proxy() -> str | None:
    """Use explicit env proxy first, else Windows IE/system proxy (e.g. Clash 7890)."""
    import os

    for key in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy", "ALL_PROXY", "all_proxy"):
        value = os.environ.get(key, "").strip()
        if value:
            return value

    if sys.platform != "win32":
        return None

    try:
        import winreg

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
        ) as key:
            enabled, _ = winreg.QueryValueEx(key, "ProxyEnable")
            if not enabled:
                return None
            server, _ = winreg.QueryValueEx(key, "ProxyServer")
    except OSError:
        return None

    server = str(server).strip()
    if not server or server.lower().startswith("socks"):
        return None
    if "://" in server:
        return server
    return f"http://{server}"


def fetch_url(url: str, *, timeout: float = 20.0) -> httpx.Response:
    from app.config import settings

    proxy = resolve_http_proxy()
    with httpx.Client(
        timeout=timeout,
        follow_redirects=True,
        headers=_DEFAULT_HEADERS,
        proxy=proxy,
        trust_env=True,
        verify=settings.http_ssl_verify,
    ) as client:
        response = client.get(url)
        response.raise_for_status()
        return response
