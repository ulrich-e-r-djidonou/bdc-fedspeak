"""
01_scrape_boc.py

Scrape les communiqués de presse de décision de taux directeur (FAD,
Fixed Announcement Dates) de la Banque du Canada.

URL pattern : https://www.bankofcanada.ca/YYYY/MM/fad-press-release-YYYY-MM-DD/
Source de la liste : sitemap WordPress de bankofcanada.ca (couverture 2009 à présent).

Usage :
    python 01_scrape_boc.py --mode test          # 5 communiqués récents
    python 01_scrape_boc.py --mode full          # tous les communiqués FAD du sitemap

Sortie :
    data/raw/boc_press_releases.csv
"""

from __future__ import annotations

import argparse
import csv
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
DATA_RAW.mkdir(parents=True, exist_ok=True)

SITEMAP_PATTERN = "https://www.bankofcanada.ca/wp-sitemap-posts-post-{n}.xml"
USER_AGENT = (
    "Mozilla/5.0 (academic-research; bdc-fedspeak; "
    "contact: ulrich.djidonou@gmail.com)"
)
HEADERS = {"User-Agent": USER_AGENT}
SLEEP_BETWEEN = 0.6  # secondes, pour rester poli avec le serveur BdC

FAD_URL_RE = re.compile(
    r"https://www\.bankofcanada\.ca/\d{4}/\d{2}/fad-press-release-\d{4}-\d{2}-\d{2}/"
)


def fetch_all_fad_urls() -> list[str]:
    """Parcourt les sitemaps de posts de la BdC et extrait les URLs de communiqués FAD."""
    urls: set[str] = set()
    for n in range(1, 20):  # arrêt automatique sur 404
        url = SITEMAP_PATTERN.format(n=n)
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.status_code == 404:
            break
        r.raise_for_status()
        urls.update(FAD_URL_RE.findall(r.text))
        time.sleep(SLEEP_BETWEEN)
    # tri chronologique via la date dans l'URL
    return sorted(urls, key=lambda u: re.search(r"(\d{4})-(\d{2})-(\d{2})/$", u).group(0))


def parse_release(url: str) -> dict:
    """Extrait date, titre, corps et taux du communiqué."""
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    title_el = soup.find("h1")
    title = title_el.get_text(strip=True) if title_el else ""

    # tentative date via balise <time> ou via meta
    date_iso = ""
    time_el = soup.find("time")
    if time_el and time_el.has_attr("datetime"):
        date_iso = time_el["datetime"][:10]
    if not date_iso:
        # fallback : extraire de l'URL (pattern fad-press-release-YYYY-MM-DD)
        m = re.search(r"fad-press-release-(\d{4})-(\d{2})-(\d{2})", url)
        if m:
            date_iso = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

    # corps : article ou main
    body_el = (
        soup.find("article")
        or soup.find("main")
        or soup.find("div", class_="page-content")
    )
    if body_el:
        # nettoyer les éléments non textuels usuels
        for tag in body_el.find_all(["script", "style", "nav", "aside", "footer"]):
            tag.decompose()
        body = body_el.get_text(" ", strip=True)
    else:
        body = ""

    # tentative d'extraction du taux directeur dans le texte
    rate = ""
    m_rate = re.search(r"(?:overnight rate|taux du financement)[^.]{0,80}?(\d+(?:[.,]\d+)?)\s*%", body, re.I)
    if m_rate:
        rate = m_rate.group(1).replace(",", ".")

    return {
        "url": url,
        "date": date_iso,
        "title": title,
        "rate_pct": rate,
        "body": body,
        "body_len": len(body),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["test", "full"], default="test")
    p.add_argument("--limit", type=int, default=5, help="mode test : nombre de communiqués")
    args = p.parse_args()

    print("Récupération de la liste des communiqués FAD via sitemap...")
    all_urls = fetch_all_fad_urls()
    print(f"{len(all_urls)} URLs FAD trouvées (couverture {all_urls[0][-11:-1]} à {all_urls[-1][-11:-1]})")

    if args.mode == "test":
        # 5 communiqués récents
        urls = all_urls[-args.limit:]
        out_name = "boc_press_releases_sample.csv"
    else:
        urls = all_urls
        out_name = "boc_press_releases.csv"

    print(f"{len(urls)} URLs à parser")

    rows = []
    for url in tqdm(urls, desc="parse"):
        try:
            rows.append(parse_release(url))
        except Exception as e:
            print(f"\nerreur {url} : {e}")
        time.sleep(SLEEP_BETWEEN)

    out_path = DATA_RAW / out_name
    fields = ["url", "date", "title", "rate_pct", "body_len", "body"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nÉcrit {len(rows)} lignes dans {out_path}")
    if rows:
        print("\nAperçu :")
        for r in rows[:5]:
            print(f"  {r['date']} | {r['title'][:70]} | taux={r['rate_pct']}% | {r['body_len']} car.")


if __name__ == "__main__":
    main()
