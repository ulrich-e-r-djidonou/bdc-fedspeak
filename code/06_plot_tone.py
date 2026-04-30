"""
06_plot_tone.py

Trace l'indice de ton hawkish/dovish de la BdC sur la période 2009-2026,
superposé au taux directeur. Annote les épisodes-clés.

Sortie : article/figures/tone_vs_rate.png
         article/figures/tone_episodes.png (zoom sur le cycle Macklem)
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TONE_PATH = ROOT / "data" / "processed" / "tone_index.csv"
MARKET_PATH = ROOT / "data" / "market" / "market_series_wide.csv"
FIG_DIR = ROOT / "article" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

EPISODES = [
    ("2008-10", "2009-12", "Crise financière"),
    ("2015-01", "2015-12", "Choc pétrolier"),
    ("2020-03", "2020-06", "COVID"),
    ("2022-03", "2023-07", "Resserrement Macklem"),
    ("2024-06", "2026-04", "Détente Macklem"),
]


def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    tone = pd.read_csv(TONE_PATH, parse_dates=["date"])
    market = pd.read_csv(MARKET_PATH, parse_dates=["date"])
    return tone, market


def plot_overview(tone: pd.DataFrame, market: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(12, 5))

    # bandes des épisodes en arrière-plan
    for start, end, label in EPISODES:
        ax.axvspan(pd.Timestamp(start), pd.Timestamp(end), alpha=0.10, color="gray")
        x_label = pd.Timestamp(start) + (pd.Timestamp(end) - pd.Timestamp(start)) / 2
        ax.text(x_label, 1.08, label, ha="center", fontsize=8, color="dimgray")

    # ligne d'origine
    ax.axhline(0, color="black", linewidth=0.6, alpha=0.6)

    # ton, par observation, coloré selon hawkish/dovish
    hawkish = tone[tone["tone_score_net"] > 0]
    dovish = tone[tone["tone_score_net"] < 0]
    neutral = tone[tone["tone_score_net"] == 0]

    ax.scatter(hawkish["date"], hawkish["tone_score_net"],
               s=18, color="#c0392b", label="Hawkish", zorder=3)
    ax.scatter(dovish["date"], dovish["tone_score_net"],
               s=18, color="#2c5dbd", label="Dovish", zorder=3)
    ax.scatter(neutral["date"], neutral["tone_score_net"],
               s=18, color="lightgray", label="Neutre", zorder=3)

    # taux directeur sur axe secondaire
    rate = market[["date", "OvernightTarget"]].dropna()
    ax2 = ax.twinx()
    ax2.plot(rate["date"], rate["OvernightTarget"],
             color="#5a5a5a", linewidth=1.2, alpha=0.7, label="Taux directeur (axe droit)")
    ax2.set_ylabel("Taux directeur (%)", color="#5a5a5a")
    ax2.tick_params(axis="y", labelcolor="#5a5a5a")
    ax2.set_ylim(-0.5, 6)

    ax.set_xlim(pd.Timestamp("2008-10-01"), pd.Timestamp("2026-06-01"))
    ax.set_ylim(-1.15, 1.15)
    ax.set_ylabel("Indice de ton (net hawkish - dovish)")
    ax.set_xlabel("")
    ax.set_title("Indice de ton des communiqués de la Banque du Canada (2009-2026)",
                 fontsize=12, pad=15)
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(loc="lower left", fontsize=8, framealpha=0.9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = FIG_DIR / "tone_vs_rate.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    return out


def plot_macklem_zoom(tone: pd.DataFrame, market: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(12, 5))

    sub = tone[(tone["date"] >= "2022-01-01") & (tone["date"] <= "2026-06-01")].copy()
    rate = market[(market["date"] >= "2022-01-01") & (market["date"] <= "2026-06-01")][["date", "OvernightTarget"]].dropna()

    # barres de ton
    colors = ["#c0392b" if v > 0 else ("#2c5dbd" if v < 0 else "lightgray")
              for v in sub["tone_score_net"]]
    ax.bar(sub["date"], sub["tone_score_net"], width=12, color=colors, alpha=0.85, label="_nolegend_")
    ax.axhline(0, color="black", linewidth=0.6, alpha=0.6)

    # taux directeur
    ax2 = ax.twinx()
    ax2.plot(rate["date"], rate["OvernightTarget"],
             color="black", linewidth=1.5, label="Taux directeur (axe droit)")
    ax2.set_ylabel("Taux directeur (%)")
    ax2.set_ylim(0, 6)

    # annotations sur changements de taux ≥ 25 bp
    big = sub[sub["rate_change_bp"].abs() >= 25].copy()
    for _, row in big.iterrows():
        sign = "+" if row["rate_change_bp"] > 0 else ""
        ax2.annotate(f"{sign}{int(row['rate_change_bp'])} bp",
                     xy=(row["date"], row["rate_pct"]),
                     xytext=(0, 8), textcoords="offset points",
                     fontsize=7, ha="center", color="black")

    ax.set_xlim(pd.Timestamp("2022-01-01"), pd.Timestamp("2026-06-01"))
    ax.set_ylim(-1.15, 1.15)
    ax.set_ylabel("Indice de ton")
    ax.set_xlabel("")
    ax.set_title("Cycle Macklem : ton des communiqués et trajectoire du taux directeur (2022-2026)",
                 fontsize=12, pad=15)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    out = FIG_DIR / "tone_episodes_macklem.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    return out


def main() -> None:
    tone, market = load()
    print(f"Ton : {len(tone)} obs, {tone['date'].min().date()} à {tone['date'].max().date()}")
    print(f"Marché : {len(market)} jours")

    p1 = plot_overview(tone, market)
    p2 = plot_macklem_zoom(tone, market)
    print(f"\nGraphiques écrits :")
    print(f"  {p1}")
    print(f"  {p2}")


if __name__ == "__main__":
    main()
