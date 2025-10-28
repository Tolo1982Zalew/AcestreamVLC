# scraper.py
import requests
import urllib.parse
from bs4 import BeautifulSoup

BASE_URL = "https://acestreamsearch.net/en/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get_acestream_links(query="[PL]"):
    """Wyszukaj linki acestream"""
    query_encoded = urllib.parse.quote(query)
    url = f"{BASE_URL}?q={query_encoded}"

    print(f"[🔍] Wyszukiwanie: {query}")

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        results = []
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            if href.startswith("acestream://"):
                title = a.get_text(strip=True) or "Bez nazwy"
                results.append((title, href))

        print(f"[✅] Znaleziono {len(results)} kanałów")
        return results

    except Exception as e:
        print(f"[!] Błąd: {e}")
        return []
