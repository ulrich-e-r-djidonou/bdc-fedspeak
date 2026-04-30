"""
03b_lexicon_diagnostics.py

Aide à enrichir le lexique de ton en identifiant les termes les plus
discriminants entre les communiqués de hausse et de baisse de taux.

Méthode : pour chaque bigramme et trigramme, calcule le ratio de fréquence
relative entre communiqués hawkish (hausse de taux) et dovish (baisse).
Les termes avec ratio élevé sont des candidats hawkish, les bas dovish.

Sortie console : top 30 termes hawkish, top 30 dovish, et termes à fort
écart absolu (souvent les plus utiles).
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data" / "processed" / "boc_press_releases_clean.csv"


STOP_WORDS = {
    "the", "a", "an", "of", "to", "in", "on", "at", "for", "by", "and", "or",
    "but", "with", "as", "is", "are", "was", "were", "be", "been", "being",
    "this", "that", "these", "those", "it", "its", "from", "has", "have",
    "had", "will", "would", "should", "could", "may", "might", "than", "into",
    "more", "most", "less", "their", "they", "them", "we", "our", "us",
    "also", "since", "while", "which", "who", "what", "when", "where", "how",
    "such", "some", "any", "all", "both", "if", "now", "then", "year",
    "years", "quarter", "quarters", "today", "however", "remain", "remains",
    "remained", "continue", "continues", "continued", "expect", "expects",
    "expected", "growth", "rate", "bank", "banks", "canada", "canadian",
    "monetary", "policy", "rates", "us", "u", "s",
}


def tokens(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    return [t for t in text.split() if t not in STOP_WORDS and len(t) > 2]


def ngrams(tokens_: list[str], n: int) -> list[str]:
    return [" ".join(tokens_[i:i + n]) for i in range(len(tokens_) - n + 1)]


def main() -> None:
    df = pd.read_csv(INPUT, parse_dates=["date"])
    df["rate_pct"] = pd.to_numeric(df["rate_pct"], errors="coerce")
    df["rate_change"] = df["rate_pct"].diff()
    # première ligne sans variation : on l'écarte
    df = df.dropna(subset=["rate_change"]).copy()

    df["bucket"] = "hold"
    df.loc[df["rate_change"] >= 0.20, "bucket"] = "hike"
    df.loc[df["rate_change"] <= -0.20, "bucket"] = "cut"

    n_hike = (df["bucket"] == "hike").sum()
    n_cut = (df["bucket"] == "cut").sum()
    n_hold = (df["bucket"] == "hold").sum()
    print(f"Communiqués : {n_hike} hausses, {n_cut} baisses, {n_hold} holds")

    hike_text = " ".join(df.loc[df["bucket"] == "hike", "body_clean"].fillna(""))
    cut_text = " ".join(df.loc[df["bucket"] == "cut", "body_clean"].fillna(""))

    hike_tokens = tokens(hike_text)
    cut_tokens = tokens(cut_text)

    for n in [2, 3]:
        h_counts = Counter(ngrams(hike_tokens, n))
        c_counts = Counter(ngrams(cut_tokens, n))
        # normaliser par taille de corpus pour avoir des fréquences comparables
        h_total = sum(h_counts.values()) or 1
        c_total = sum(c_counts.values()) or 1
        # candidats : termes apparaissant au moins 3 fois dans une catégorie
        all_terms = set(t for t, c in h_counts.items() if c >= 3) | \
                    set(t for t, c in c_counts.items() if c >= 3)
        scored = []
        for t in all_terms:
            h_freq = h_counts.get(t, 0) / h_total * 1000
            c_freq = c_counts.get(t, 0) / c_total * 1000
            diff = h_freq - c_freq  # >0 hawkish, <0 dovish
            scored.append((t, h_counts.get(t, 0), c_counts.get(t, 0), h_freq, c_freq, diff))

        scored.sort(key=lambda x: x[5], reverse=True)
        print(f"\n=== Top 25 candidats HAWKISH ({n}-grammes, diff = freq hike - freq cut, ‰) ===")
        for term, hc, cc, hf, cf, d in scored[:25]:
            print(f"  {d:+.2f} | hike={hc:3d} ({hf:.2f}‰) | cut={cc:3d} ({cf:.2f}‰) | {term}")
        print(f"\n=== Top 25 candidats DOVISH ({n}-grammes) ===")
        for term, hc, cc, hf, cf, d in scored[-25:][::-1]:
            print(f"  {d:+.2f} | hike={hc:3d} ({hf:.2f}‰) | cut={cc:3d} ({cf:.2f}‰) | {term}")


if __name__ == "__main__":
    main()
