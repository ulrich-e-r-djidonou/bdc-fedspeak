# BdC Fedspeak

Article empirique court appliquant les méthodes de la littérature sur les communications de banques centrales aux communiqués de la Banque du Canada (BdC) sur la période 1994 à 2026.

## Question de recherche

Les communications de la BdC contiennent-elles une information exploitable pour les marchés au-delà de la décision de taux elle-même, et dans quelles conditions cette information domine la réaction de marché ?

## Approche

1. Construction d'un indice de ton hawkish/dovish à partir d'un dictionnaire (Apel et Blix Grimaldi 2014, Picault et Renault 2017).
2. Étude d'événement avec fenêtre journalière sur les rendements obligataires GoC, le CAD/USD et le S&P/TSX.
3. Décomposition Jarociński et Karadi (2020) entre choc de politique monétaire pure et choc d'information de la banque centrale.
4. Étude de cas sur le cycle Macklem 2022 à 2026.

## Données

Toutes les données sont publiques :

- Communiqués BdC (1994 à 2026), Rapports sur la politique monétaire (1995 à 2026), Résumé des délibérations (2023 à 2026), discours du Gouverneur (2003 à 2026).
- API Valet de la BdC : V39051 (rendement GoC 2 ans), V39055 (rendement GoC 10 ans), FXUSDCAD.
- Yahoo Finance : ^GSPTSE.

## Structure du dépôt

```
bdc-fedspeak/
├── data/
│   ├── raw/             communiqués bruts scrapés
│   ├── processed/       textes nettoyés et métadonnées
│   └── market/          séries Valet API et Yahoo Finance
├── code/
│   ├── 01_scrape_boc.py
│   ├── 02_clean_text.py
│   ├── 03_tone_index.py
│   ├── 04_market_data.py
│   └── 05_event_study.py
├── lit-review/
│   └── references.bib
└── article/
    └── article_v1.md
```

## Reproductibilité

Python 3.11 ou supérieur. Dépendances listées dans `requirements.txt` (à venir).

## Licence

MIT.
