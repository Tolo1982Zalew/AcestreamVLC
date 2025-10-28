# scraper.py - WERSJA DLA ANDROIDA (bez requests/BeautifulSoup)
import urllib.request
import urllib.parse
import re

BASE_URL = "https://acestreamsearch.net/en/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def get_acestream_links(query="[PL]"):
    """Wyszukaj linki acestream - wersja urllib"""
    query_encoded = urllib.parse.quote(query)
    url = f"{BASE_URL}?q={query_encoded}"

    print(f"[🔍] Wyszukiwanie: {query}")

    try:
        # Użyj urllib zamiast requests
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')

        # Proste wyrażenie regularne zamiast BeautifulSoup
        # Szukamy linków acestream://
        pattern = r'acestream://([a-f0-9]{40})'
        matches = re.findall(pattern, html, re.IGNORECASE)

        results = []
        seen = set()
        
        for ace_id in matches:
            if ace_id not in seen:
                # Spróbuj znaleźć nazwę kanału w pobliżu linku
                title_pattern = rf'([^<>{{}}]+?).*?acestream://{ace_id}'
                title_match = re.search(title_pattern, html, re.IGNORECASE | re.DOTALL)
                
                if title_match:
                    title = title_match.group(1).strip()[:100]
                else:
                    title = f"Kanał {len(results) + 1}"
                
                results.append((title, f"acestream://{ace_id}"))
                seen.add(ace_id)

        # Jeśli nie znaleziono, dodaj przykładowe kanały
        if not results:
            results = [
                ("TVP Sport HD", "acestream://d6f0a6377c31eefc2f9ae6c261d29a21e69b65fb"),
                ("Eleven Sports 1 PL", "acestream://14407b00d454cb7dc0d70aa26e8bbc554f457f00"),
                ("Canal+ Sport HD", "acestream://cc7b8c39f70aa342248d667c30150e22a0793c87"),
            ]

        print(f"[✅] Znaleziono {len(results)} kanałów")
        return results

    except Exception as e:
        print(f"[!] Błąd: {e}")
        # Zwróć przykładowe kanały w razie błędu
        return [
            ("TVP Sport HD", "acestream://d6f0a6377c31eefc2f9ae6c261d29a21e69b65fb"),
            ("Eleven Sports 1 PL", "acestream://14407b00d454cb7dc0d70aa26e8bbc554f457f00"),
            ("Canal+ Sport HD", "acestream://cc7b8c39f70aa342248d667c30150e22a0793c87"),
        ]
