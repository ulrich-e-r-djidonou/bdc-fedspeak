# BdC Fedspeak

Article empirique court appliquant les méthodes de la littérature sur les communications de banques centrales aux communiqués de la Banque du Canada (BdC) sur la période 2009 à 2026 (couverture limitée par le pattern d'URL `fad-press-release` introduit en janvier 2009).

## Question de recherche

Les communications de la BdC contiennent-elles une information exploitable pour les marchés au-delà de la décision de taux elle-même, et dans quelles conditions cette information domine la réaction de marché ?

## Approche

1. Construction d'un indice de ton hawkish/dovish à partir d'un dictionnaire (Apel et Blix Grimaldi 2014, Picault et Renault 2017).
2. Étude d'événement avec fenêtre journalière sur les rendements obligataires GoC, le CAD/USD et le S&P/TSX.
3. Décomposition Jarociński et Karadi (2020) entre choc de politique monétaire pure et choc d'information de la banque centrale.
4. Étude de cas sur le cycle Macklem 2022 à 2026.

## Données

Toutes les données sont publiques :

- Communiqués BdC FAD (2009 à 2026), récupérés via le sitemap WordPress de bankofcanada.ca.
- API Valet de la BdC : `BD.CDN.2YR.DQ.YLD` (GoC 2 ans), `BD.CDN.5YR.DQ.YLD` (GoC 5 ans), `BD.CDN.10YR.DQ.YLD` (GoC 10 ans), `FXUSDCAD` (taux de change), `V39079` (taux directeur cible).
- Yahoo Finance : `^GSPTSE` (à brancher quand `yfinance` sera installé).

## Structure du dépôt

```
bdc-fedspeak/
├── data/
│   ├── raw/                              communiqués bruts scrapés
│   │   └── boc_press_releases.csv
│   ├── processed/                        textes nettoyés et métadonnées
│   │   ├── boc_press_releases_clean.csv
│   │   ├── tone_index.csv
│   │   └── tone_diagnostics.csv
│   └── market/                           séries Valet API
│       ├── market_series.csv
│       └── market_series_wide.csv
├── code/
│   ├── 01_scrape_boc.py                  scraping via sitemap WordPress
│   ├── 02_clean_text.py                  nettoyage du boilerplate
│   ├── 02b_merge_rates.py                jointure du taux directeur Valet
│   ├── 03_tone_index.py                  indice hawkish/dovish
│   ├── 03b_lexicon_diagnostics.py        bigrammes discriminants
│   ├── 04_market_data.py                 collecte Valet + Yahoo
│   ├── 06_plot_tone.py                   figures de visualisation
│   └── lexicon_tone.py                   lexique de ton EN+FR
├── article/
│   └── figures/                          figures générées
│       ├── tone_vs_rate.png
│       └── tone_episodes_macklem.png
├── lit-review/                           bibliographie (à venir)
└── .claude/
    └── session-logs/                     journal de sessions
```

## Reproductibilité

Python 3.11 ou supérieur. Dépendances listées dans `requirements.txt`.

```bash
pip install -r requirements.txt
python code/01_scrape_boc.py --mode full
python code/02_clean_text.py
python code/02b_merge_rates.py
python code/03_tone_index.py
python code/04_market_data.py
python code/06_plot_tone.py
```

## Licence

MIT.
