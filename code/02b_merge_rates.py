"""
02b_merge_rates.py

Récupère le taux directeur officiel via l'API Valet de la BdC (série V39079)
et l'attache à chaque communiqué FAD pour calculer la vraie variation de taux.

V39079 : Target for the overnight rate, daily, depuis 2009-04-21.
Pour les 3 communiqués antérieurs au 2009-04-21 (jan/mar 2009), on
complète manuellement à partir des annonces officielles.

Entrée : data/processed/boc_press_releases_clean.csv
Sortie : data/processed/boc_press_releases_clean.csv (rate_pct écrasé, rate_change_bp ajouté)
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
INPUT = ROOT / "data" / "processed" / "boc_press_releases_clean.csv"

# valeurs officielles pour les communiqués pré-2009-04-21 (source : page historique BdC)
EARLY_RATES = {
    "2009-01-20": 1.00,
    "2009-03-03": 0.50,
    # 2009-04-21 sera couvert par Valet (= 0,25 %)
}


def fetch_overnight_rate() -> pd.DataFrame:
    url = "https://www.bankofcanada.ca/valet/observations/V39079/json"
    params = {"start_date": "2009-04-21", "end_date": "2026-12-31"}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    rows = []
    for o in r.json().get("observations", []):
        d = o.get("d")
        v = o.get("V39079", {}).get("v") if isinstance(o.get("V39079"), dict) else None
        if v is not None:
            rows.append({"date": d, "rate": float(v)})
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date").reset_index(drop=True)


def main() -> None:
    df = pd.read_csv(INPUT, parse_dates=["date"])
    rates = fetch_overnight_rate()
    print(f"V39079 : {len(rates)} observations quotidiennes")

    # joindre sur la date du communiqué
    df = df.merge(rates, on="date", how="left")

    # compléter les valeurs manquantes pour les premiers communiqués
    for d, val in EARLY_RATES.items():
        mask = df["date"] == pd.Timestamp(d)
        df.loc[mask, "rate"] = val

    # cas particulier : si un FAD tombe un jour férié, prendre le taux de la veille ouvrable
    if df["rate"].isna().any():
        rates_indexed = rates.set_index("date")["rate"]
        rates_indexed = rates_indexed.reindex(
            pd.date_range(rates["date"].min(), pd.Timestamp("2026-12-31"), freq="D"),
            method="ffill",
        )
        df.loc[df["rate"].isna(), "rate"] = df.loc[df["rate"].isna(), "date"].map(rates_indexed)

    n_missing = df["rate"].isna().sum()
    print(f"Valeurs manquantes après jointure : {n_missing}")
    if n_missing:
        print(df.loc[df["rate"].isna(), ["date", "title"]].head())

    df = df.sort_values("date").reset_index(drop=True)
    df["rate_pct"] = df["rate"]
    df["rate_change_bp"] = (df["rate"].diff() * 100).round(0)
    df = df.drop(columns=["rate"])

    df.to_csv(INPUT, index=False, encoding="utf-8")
    print(f"\nÉcrit : {INPUT}")
    print("\nDistribution des variations de taux (bp) :")
    print(df["rate_change_bp"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
