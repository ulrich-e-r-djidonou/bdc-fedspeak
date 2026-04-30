"""
03_tone_index.py

Construit un indice de ton hawkish/dovish à partir des communiqués nettoyés.

Méthodologie :
  - matching de n-grammes contre les lexiques HAWKISH et DOVISH (Apel-Blix Grimaldi 2014,
    Picault-Renault 2017, adaptés au vocabulaire BdC).
  - score net = (n_hawkish - n_dovish) / (n_hawkish + n_dovish)
  - score normalisé = (n_hawkish - n_dovish) / n_mots_total * 1000

Entrée  : data/processed/boc_press_releases_clean.csv
Sortie  : data/processed/tone_index.csv (date, scores, comptes par lexique)
          data/processed/tone_diagnostics.csv (matches détaillés pour validation)
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from lexicon_tone import get_lexicons

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data" / "processed" / "boc_press_releases_clean.csv"
OUT_INDEX = ROOT / "data" / "processed" / "tone_index.csv"
OUT_DIAG = ROOT / "data" / "processed" / "tone_diagnostics.csv"


def count_matches(text_lower: str, terms: set[str]) -> tuple[int, dict]:
    """Compte les occurrences de chaque terme dans le texte. Retourne (total, par_terme)."""
    total = 0
    detail = {}
    for term in terms:
        # mot complet pour les termes simples, sous-chaîne pour les n-grammes
        if " " in term:
            n = text_lower.count(term)
        else:
            # frontière de mot
            n = len(re.findall(rf"\b{re.escape(term)}\b", text_lower))
        if n > 0:
            detail[term] = n
            total += n
    return total, detail


def score_release(text: str, hawkish: set[str], dovish: set[str]) -> dict:
    text_lower = text.lower() if isinstance(text, str) else ""
    n_words = len(re.findall(r"\b\w+\b", text_lower))
    h_total, h_detail = count_matches(text_lower, hawkish)
    d_total, d_detail = count_matches(text_lower, dovish)
    denom = h_total + d_total
    score_net = (h_total - d_total) / denom if denom > 0 else 0.0
    score_norm = (h_total - d_total) / n_words * 1000 if n_words > 0 else 0.0
    return {
        "n_words": n_words,
        "n_hawkish": h_total,
        "n_dovish": d_total,
        "tone_score_net": score_net,
        "tone_score_per_kw": score_norm,
        "hawkish_terms": "; ".join(f"{t}({n})" for t, n in sorted(h_detail.items(), key=lambda x: -x[1])[:8]),
        "dovish_terms": "; ".join(f"{t}({n})" for t, n in sorted(d_detail.items(), key=lambda x: -x[1])[:8]),
    }


def main() -> None:
    if not INPUT.exists():
        raise SystemExit(f"Fichier introuvable : {INPUT}. Lance 02_clean_text.py d'abord.")
    df = pd.read_csv(INPUT, parse_dates=["date"])
    print(f"{len(df)} communiqués chargés")

    hawkish, dovish = get_lexicons()
    print(f"Lexique : {len(hawkish)} hawkish, {len(dovish)} dovish")

    scores = df["body_clean"].fillna("").map(lambda t: score_release(t, hawkish, dovish))
    score_df = pd.DataFrame(scores.tolist())
    out = pd.concat([df[["date", "url", "title", "rate_pct"]], score_df], axis=1)
    out = out.sort_values("date").reset_index(drop=True)

    # variation de taux directeur observée à cette annonce
    out["rate_pct"] = pd.to_numeric(out["rate_pct"], errors="coerce")
    out["rate_change_bp"] = (out["rate_pct"].diff() * 100).round(0)

    diag_cols = ["date", "title", "n_words", "n_hawkish", "n_dovish",
                 "tone_score_net", "tone_score_per_kw",
                 "hawkish_terms", "dovish_terms"]
    out[diag_cols].to_csv(OUT_DIAG, index=False, encoding="utf-8")

    keep_cols = ["date", "url", "title", "rate_pct", "rate_change_bp",
                 "n_words", "n_hawkish", "n_dovish",
                 "tone_score_net", "tone_score_per_kw"]
    out[keep_cols].to_csv(OUT_INDEX, index=False, encoding="utf-8")

    print(f"\nÉcrit indice : {OUT_INDEX}")
    print(f"Écrit diagnostics : {OUT_DIAG}")

    # sanity check : corrélation entre ton et changement de taux
    valid = out.dropna(subset=["tone_score_net", "rate_change_bp"])
    if len(valid) > 5:
        corr = valid[["tone_score_net", "rate_change_bp"]].corr().iloc[0, 1]
        print(f"\nCorrélation (ton, variation de taux en bp) : {corr:.3f}")
        print("Attendu : positif (ton hawkish associé à des hausses de taux).")

    print("\nAperçu période récente :")
    print(out.tail(10)[["date", "rate_pct", "rate_change_bp",
                        "n_hawkish", "n_dovish", "tone_score_net"]].to_string(index=False))


if __name__ == "__main__":
    main()
