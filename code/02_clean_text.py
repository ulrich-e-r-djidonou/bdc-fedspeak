"""
02_clean_text.py

Nettoie les communiqués bruts de la BdC :
  1. supprime le boilerplate de partage social
  2. tronque après le bloc "Content Type(s)" (métadonnées de fin)
  3. supprime les répétitions et les espaces multiples
  4. ajoute des stats : nb mots, nb phrases, longueur après nettoyage

Entrée  : data/raw/boc_press_releases.csv
Sortie  : data/processed/boc_press_releases_clean.csv
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "boc_press_releases.csv"
OUT = ROOT / "data" / "processed" / "boc_press_releases_clean.csv"
OUT.parent.mkdir(parents=True, exist_ok=True)


SHARE_BLOCK_RE = re.compile(
    r"(Share this page (?:on Facebook|on X|on LinkedIn|by email)\s*)+",
    re.I,
)
END_MARKER_RE = re.compile(
    r"\bContent Type\(s\)\s*:.*$",
    re.I | re.S,
)
START_MARKERS = [
    "The Bank of Canada today",
    "La Banque du Canada a annoncé",
    "Today, the Bank of Canada",
]


def find_start(text: str) -> int:
    """Indice du premier marqueur de début connu, sinon 0."""
    for marker in START_MARKERS:
        idx = text.find(marker)
        if idx >= 0:
            return idx
    return 0


def clean_one(raw: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        return ""
    text = raw

    # 1. supprimer le bloc de boutons de partage social
    text = SHARE_BLOCK_RE.sub(" ", text)

    # 2. tronquer après "Content Type(s)"
    text = END_MARKER_RE.sub("", text)

    # 3. couper le boilerplate de tête : démarrer au premier marqueur de fond
    start = find_start(text)
    if start > 0:
        text = text[start:]

    # 4. normaliser les espaces
    text = re.sub(r"\s+", " ", text).strip()
    return text


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def sentence_count(text: str) -> int:
    if not text:
        return 0
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return len([s for s in sentences if len(s.strip()) > 5])


def main() -> None:
    if not RAW.exists():
        raise SystemExit(f"Fichier introuvable : {RAW}. Lance d'abord 01_scrape_boc.py.")
    df = pd.read_csv(RAW)
    print(f"{len(df)} communiqués bruts chargés")

    df["body_clean"] = df["body"].fillna("").map(clean_one)
    df["clean_len"] = df["body_clean"].str.len()
    df["word_count"] = df["body_clean"].map(word_count)
    df["sentence_count"] = df["body_clean"].map(sentence_count)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # filtrer : garder uniquement les communiqués avec contenu substantiel
    df_kept = df[df["word_count"] >= 100].sort_values("date").reset_index(drop=True)
    n_dropped = len(df) - len(df_kept)
    if n_dropped:
        print(f"Filtrés : {n_dropped} communiqués avec < 100 mots après nettoyage")

    cols = ["date", "url", "title", "rate_pct", "word_count", "sentence_count", "clean_len", "body_clean"]
    df_kept[cols].to_csv(OUT, index=False, encoding="utf-8")
    print(f"Écrit {len(df_kept)} lignes nettoyées dans {OUT}")

    # diagnostics
    print("\n=== Statistiques ===")
    print(f"  Période : {df_kept['date'].min().date()} à {df_kept['date'].max().date()}")
    print(f"  Mots : médiane {df_kept['word_count'].median():.0f}, "
          f"min {df_kept['word_count'].min()}, max {df_kept['word_count'].max()}")
    print(f"  Phrases : médiane {df_kept['sentence_count'].median():.0f}")

    print("\n=== Aperçu nettoyé (1er communiqué) ===")
    print(df_kept.iloc[0]["body_clean"][:400])
    print("\n=== Aperçu nettoyé (dernier communiqué) ===")
    print(df_kept.iloc[-1]["body_clean"][:400])


if __name__ == "__main__":
    main()
