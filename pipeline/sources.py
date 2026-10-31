"""Fetch and normalise rows from the watched pages.

The pages are chosen to be boring on purpose: server-rendered, no login,
stable markup. If a source starts misbehaving, the pipeline just logs fewer
rows; it never crashes.
"""

import re
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")

# Each site embeds the listing id, title and price in nearby markup.
# One loose regex per site keeps this readable; see the "sources" notes in
# the README when a pattern stops matching.
PRICE_BLOCK = re.compile(
    r'data-listing-id="(?P<id>[^"]+)"[\s\S]{0,400}?'
    r'title="(?P<title>[^"]+)"[\s\S]{0,400}?'
    r'"price":\s*"(?P<price>[\d.,]+)"',
    re.IGNORECASE,
)


def _get(url: str, timeout: int = 20) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept-Language": "en"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def fetch(url: str) -> list:
    """Return normalised rows for one watched URL."""
    try:
        html = _get(url)
    except Exception as e:
        print(f"  fetch error: {e}")
        return []

    rows = []
    for m in PRICE_BLOCK.finditer(html):
        price = None
        if m["price"]:
            price = float(m["price"].replace(".", "").replace(",", "."))
        rows.append({
            "id": m["id"],
            "title": m["title"],
            "price": price,
            "currency": "EUR",
            "url": url,
        })
    return rows
