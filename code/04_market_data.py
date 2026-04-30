"""
04_market_data.py

Récupère les séries de marché pour l'étude d'événement :
  - rendement obligation GoC 2 ans
  - rendement obligation GoC 10 ans
  - taux de change USD/CAD
  - indice S&P/TSX (via Yahoo Finance)

Source principale : API Valet de la Banque du Canada (gratuite, sans clé).
  Documentation : https://www.bankofcanada.ca/valet/docs

Sortie : data/market/market_series.csv (format long : date, series, value)
         data/market/market_series_wide.csv (format wide pivoté)
"""

from __future__ import annotations

import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "market"
OUT_DIR.mkdir(parents=True, exist_ok=True)

VALET_BASE = "https://www.bankofcanada.ca/valet"

# Séries Valet visées (les V-series sont les codes CANSIM historiques, repris par Valet)
VALET_SERIES = {
    "GoC_2Y": "BD.CDN.2YR.DQ.YLD",   # rendement obligation gouvernement Canada 2 ans
    "GoC_10Y": "BD.CDN.10YR.DQ.YLD", # rendement obligation gouvernement Canada 10 ans
    "USDCAD": "FXUSDCAD",            # taux de change quotidien USD/CAD
}

# Séries de fallback en cas d'échec (anciens identifiants V-)
VALET_FALLBACK = {
    "GoC_2Y": "V39051",
    "GoC_10Y": "V39055",
    "USDCAD": "FXUSDCAD",
}

START_DATE = "1994-01-01"
END_DATE = date.today().isoformat()


def fetch_series(series_id: str, start: str = START_DATE, end: str = END_DATE) -> pd.DataFrame:
    url = f"{VALET_BASE}/observations/{series_id}/json"
    params = {"start_date": start, "end_date": end}
    r = requests.get(url, params=params, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code} pour {series_id} : {r.text[:200]}")
    payload = r.json()
    obs = payload.get("observations", [])
    if not obs:
        raise RuntimeError(f"Pas d'observations pour {series_id}")
    rows = []
    for o in obs:
        d = o.get("d")
        # la valeur est sous la clé du series_id
        val = o.get(series_id, {})
        if isinstance(val, dict):
            v = val.get("v")
        else:
            v = val
        rows.append({"date": d, "value": v})
    df = pd.DataFrame(rows)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df.dropna(subset=["date"]).reset_index(drop=True)


def fetch_with_fallback(label: str, primary: str, fallback: str) -> pd.DataFrame:
    try:
        df = fetch_series(primary)
        print(f"  {label} : {len(df)} obs via {primary}")
        return df
    except Exception as e:
        print(f"  {label} : échec {primary} ({e}), tentative {fallback}")
        df = fetch_series(fallback)
        print(f"  {label} : {len(df)} obs via {fallback}")
        return df


def main() -> None:
    print(f"Récupération des séries Valet ({START_DATE} à {END_DATE})")
    long_frames = []
    for label, primary in VALET_SERIES.items():
        fallback = VALET_FALLBACK.get(label, primary)
        df = fetch_with_fallback(label, primary, fallback)
        df["series"] = label
        long_frames.append(df[["date", "series", "value"]])
        time.sleep(0.5)

    # TSX via Yahoo Finance (yfinance ou pandas-datareader si installé)
    try:
        import yfinance as yf
        print("  TSX : récupération via yfinance")
        tsx = yf.Ticker("^GSPTSE").history(start=START_DATE, end=END_DATE, auto_adjust=False)
        if not tsx.empty:
            tsx_df = tsx.reset_index()[["Date", "Close"]].rename(columns={"Date": "date", "Close": "value"})
            tsx_df["date"] = pd.to_datetime(tsx_df["date"]).dt.tz_localize(None)
            tsx_df["series"] = "TSX"
            long_frames.append(tsx_df[["date", "series", "value"]])
            print(f"  TSX : {len(tsx_df)} obs")
    except ImportError:
        print("  TSX : yfinance non installé, à ajouter à requirements.txt si voulu")

    long = pd.concat(long_frames, ignore_index=True).sort_values(["series", "date"])
    long_path = OUT_DIR / "market_series.csv"
    long.to_csv(long_path, index=False, encoding="utf-8")
    print(f"\nÉcrit format long : {long_path} ({len(long)} lignes)")

    wide = long.pivot(index="date", columns="series", values="value").reset_index()
    wide_path = OUT_DIR / "market_series_wide.csv"
    wide.to_csv(wide_path, index=False, encoding="utf-8")
    print(f"Écrit format wide : {wide_path} ({len(wide)} lignes, {len(wide.columns)-1} séries)")

    print("\nAperçu :")
    print(wide.tail(5).to_string(index=False))


if __name__ == "__main__":
    main()
