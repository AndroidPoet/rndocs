import re
import time
import urllib.request
from typing import Optional

from scrapling.fetchers import Fetcher

DOCS_BASE = "https://reactnative.dev"
SITEMAP_URL = f"{DOCS_BASE}/sitemap.xml"


def get_all_doc_urls() -> list[str]:
    """Fetch stable doc URLs from sitemap (no versioned or /next/ paths)."""
    with urllib.request.urlopen(SITEMAP_URL) as resp:
        content = resp.read().decode()
    urls = re.findall(r"https://reactnative\.dev/docs/[^<\s]+", content)
    return sorted({u for u in urls if not re.search(r"/docs/(next|\d+\.\d+)", u)})


def slug_from_url(url: str) -> str:
    match = re.search(r"/docs/(.+?)/?$", url)
    return match.group(1) if match else url.split("/")[-1]


def scrape_page(url: str, fetcher: Fetcher) -> Optional[tuple[str, str, str, str]]:
    """
    Returns (slug, title, section, content) or None on failure.
    """
    try:
        page = fetcher.get(url)
    except Exception as e:
        return None

    # Title
    h1 = page.css("h1").first
    title = h1.get_all_text().strip() if h1 else slug_from_url(url).replace("-", " ").title()

    # Section from breadcrumb (second-to-last crumb)
    section: Optional[str] = None
    crumbs = list(page.css("nav[aria-label='Breadcrumbs'] a, .breadcrumbs__list a"))
    if len(crumbs) >= 2:
        section = crumbs[-2].get_all_text().strip()
    elif len(crumbs) == 1:
        section = crumbs[0].get_all_text().strip()

    # Main content — prefer .theme-doc-markdown, fall back to article / main
    for selector in (".theme-doc-markdown", "article", "main"):
        container = page.css(selector).first
        if container:
            break

    content = container.get_all_text().strip() if container else ""
    content = re.sub(r"[ \t]+", " ", content)
    content = re.sub(r"\n{3,}", "\n\n", content)

    slug = slug_from_url(url)
    return slug, title, section, content


def sync(verbose: bool = True, delay: float = 0.25) -> tuple[int, int]:
    """Sync all RN docs to local SQLite. Returns (success, errors)."""
    from .db import init_db, upsert_doc

    conn = init_db()
    fetcher = Fetcher()

    if verbose:
        print("Fetching doc URLs from sitemap...")

    urls = get_all_doc_urls()

    if verbose:
        print(f"Found {len(urls)} pages. Scraping...\n")

    success, errors = 0, 0

    for i, url in enumerate(urls, 1):
        result = scrape_page(url, fetcher)
        if result:
            slug, title, section, content = result
            upsert_doc(conn, slug, title, content, section, url)
            success += 1
            if verbose:
                section_tag = f" [{section}]" if section else ""
                print(f"  [{i:3}/{len(urls)}]{section_tag} {title[:55]}")
        else:
            errors += 1
            if verbose:
                print(f"  [{i:3}/{len(urls)}] ERROR: {url}")

        if i < len(urls):
            time.sleep(delay)

    return success, errors
