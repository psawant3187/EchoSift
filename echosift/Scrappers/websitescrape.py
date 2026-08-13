import random
import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse

import requests
import tldextract
from bs4 import BeautifulSoup
from goose3 import Goose
from langdetect import DetectorFactory, detect

from config import (
    INDIAN_LANG_CODES,
    SCRAPE_MAX_DEPTH,
    SCRAPE_MAX_LINKS_PER_PAGE,
    SCRAPE_MAX_WORKERS,
    SCRAPE_TIMEOUT_SECONDS,
    USER_AGENTS,
)

DetectorFactory.seed = 0


def _random_agent() -> str:
    return random.choice(USER_AGENTS)


def _is_internal_link(base_url: str, link: str) -> bool:
    base = tldextract.extract(base_url)
    target = tldextract.extract(link)
    return base.domain == target.domain and base.suffix == target.suffix


def _detect_language(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "unknown"


def _scrape_page(url: str, depth: int, session: requests.Session) -> dict:
    try:
        headers = {"User-Agent": _random_agent()}
        t0 = time.time()
        response = session.get(url, headers=headers, timeout=SCRAPE_TIMEOUT_SECONDS)
        elapsed = round(time.time() - t0, 4)

        soup = BeautifulSoup(response.text, "html.parser")
        title = (
            soup.title.string.strip()
            if soup.title and soup.title.string
            else "No Title Found"
        )

        g = Goose()
        article = g.extract(raw_html=response.text)
        content = article.cleaned_text or soup.get_text(separator="\n", strip=True)

        detected_lang = _detect_language(content)

        links = [urljoin(url, a["href"]) for a in soup.find_all("a", href=True)]
        images = [urljoin(url, img["src"]) for img in soup.find_all("img", src=True)]

        try:
            ip = socket.gethostbyname(urlparse(url).hostname)
        except Exception:
            ip = "Unavailable"

        return {
            "title": title,
            "content": content,
            "metadata": {
                "Title": title,
                "URL": url,
                "Detected Language": detected_lang,
                "Is Indian Language": detected_lang in INDIAN_LANG_CODES,
                "Server": response.headers.get("Server", "N/A"),
                "Last Modified": response.headers.get("Last-Modified", "N/A"),
                "Status Code": response.status_code,
                "Response Time (s)": elapsed,
                "Content Length": len(response.content),
                "Depth": depth,
                "Cache Control": response.headers.get("Cache-Control", "N/A"),
                "ETag": response.headers.get("ETag", "N/A"),
                "IP Address": ip,
                "User Agent": headers["User-Agent"],
            },
            "response_data": {
                "Status Code": response.status_code,
                "Content-Type": response.headers.get("Content-Type"),
                "Content-Length": response.headers.get("Content-Length"),
                "Encoding": response.encoding,
                "URL": response.url,
            },
            "images": images,
            "links": links,
        }
    except Exception as e:
        return {"error": str(e), "url": url}


def scrape_website(
    base_url: str,
    max_depth: int = SCRAPE_MAX_DEPTH,
    max_links_per_page: int = SCRAPE_MAX_LINKS_PER_PAGE,
    max_workers: int = SCRAPE_MAX_WORKERS,
) -> list[dict]:
    """Recursively scrape a website up to max_depth, returning a list of page results."""
    visited: set[str] = set()
    results: list[dict] = []

    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    def _scrape(url: str, depth: int):
        if depth > max_depth or url in visited:
            return None
        visited.add(url)
        return _scrape_page(url, depth, session)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        pending = {executor.submit(_scrape, base_url, 1): base_url}
        while pending:
            for future in list(as_completed(pending)):
                pending.pop(future, None)
                result = future.result()
                if not result or "error" in result:
                    continue
                results.append(result)
                for link in result.get("links", [])[:max_links_per_page]:
                    if _is_internal_link(base_url, link) and link not in visited:
                        depth = result["metadata"]["Depth"] + 1
                        pending[executor.submit(_scrape, link, depth)] = link

    return results