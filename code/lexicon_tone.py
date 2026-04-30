"""
lexicon_tone.py

Lexique de ton hawkish (restrictif) / dovish (accommodant) pour l'analyse
des communiqués de banques centrales. Inspiré de :
  - Apel et Blix Grimaldi (2014), Review of Economics 65(1)
  - Picault et Renault (2017), JIMF 79
  - Adapté au vocabulaire de la Banque du Canada (anglais et français).

Convention de score :
  hawkish = +1   (signale un resserrement ou une inquiétude inflationniste)
  dovish  = -1   (signale un assouplissement ou une inquiétude croissance)

Usage prévu :
  - tokeniser le communiqué
  - matcher les n-grammes contre HAWKISH et DOVISH
  - score brut = (#hawkish - #dovish) / (#hawkish + #dovish)
  - score normalisé = (#hawkish - #dovish) / nb_mots_total
"""

# ---------- ANGLAIS ----------

HAWKISH_EN = {
    # actions de resserrement
    "raise rates", "raising target", "increase rates", "increased target",
    "hike", "tighten", "tightening", "tightened", "quantitative tightening",
    "remove accommodation", "reduce stimulus", "withdraw stimulus",
    "higher interest rates", "higher interest rate",
    # vocabulaire d'inflation
    "inflation pressure", "inflation pressures", "inflationary pressure",
    "inflationary pressures", "above target", "elevated inflation",
    "persistent inflation", "broad-based price increases", "broad-based inflation",
    "overheating", "excess demand", "capacity pressures",
    "supply disruptions", "supply chain disruptions",
    "inflation becomes entrenched", "entrenched inflation",
    "price pressures", "wage pressures", "wage growth strong",
    # croissance forte
    "strong growth", "robust growth", "solid expansion",
    "tight labour market", "tight labor market", "labour markets tight",
    "labour market tight", "labor market tight", "wage pressures",
    "financial conditions tightened",
    # forward guidance restrictif
    "further increases", "additional tightening", "policy needs to be more restrictive",
    "rates need to rise", "rates may need to rise",
    "monetary policy will need to tighten", "interest rates need to rise",
    "need to rise further", "additional rate increases",
    "more restrictive", "further tightening", "policy needs to be restrictive",
}

DOVISH_EN = {
    # actions d'assouplissement
    "cut rates", "cut the rate", "lower rates", "lower the rate",
    "lowered the target", "reduced target", "reduce target",
    "reduce the target", "decided to reduce", "decided to lower",
    "reduce rates", "lower interest rates", "ease", "easing",
    "accommodative", "stimulative", "supportive policy",
    "effective lower bound", "lower bound",
    # vocabulaire de croissance faible
    "weak growth", "subdued growth", "slowing economy", "economic slack",
    "excess supply", "excess capacity",
    "downside risks", "downside risk", "risks to the downside",
    "elevated uncertainty", "heightened uncertainty",
    "uncertainty has increased", "more-than-usual uncertainty",
    "weakness", "weakening", "weakened", "softening", "softened",
    "soft demand", "soft growth", "weaker growth",
    "deteriorating", "deteriorated", "contracting", "contraction", "recession",
    "weighs on", "weigh on", "weighing on", "weighed on",
    "slow the pace", "slowing pace", "slowed in recent months",
    # tensions commerciales (BdC contemporain)
    "trade tensions", "trade conflict", "trade war", "tariff", "tariffs",
    # désinflation
    "below target", "subdued inflation", "weak price pressures",
    "easing inflation", "disinflation", "inflation moderating",
    "inflation expected to ease", "inflation has slowed",
    "inflation close to target", "inflation back to target",
    "inflation easing", "easing of inflation", "moderating inflation",
    # forward guidance accommodant
    "further cuts", "further reduction", "further easing", "additional easing",
    "additional cuts", "more easing may be required",
    "policy needs to remain accommodative", "support the economy",
    "support to the economy", "more support",
}

# ---------- FRANÇAIS ----------

HAWKISH_FR = {
    "relever le taux", "hausse de taux", "resserrement", "resserrer",
    "retirer la détente", "réduire la détente",
    "pressions inflationnistes", "pression inflationniste",
    "supérieure à la cible", "au-dessus de la cible",
    "inflation élevée", "inflation persistante",
    "surchauffe", "demande excédentaire", "tensions sur les capacités",
    "croissance robuste", "marché du travail tendu",
    "pressions salariales",
    "nouvelles hausses", "resserrement supplémentaire",
}

DOVISH_FR = {
    "baisser le taux", "baisse de taux", "réduire le taux",
    "détente", "accommodante", "soutien à l'économie",
    "ralentissement", "faiblesse", "marges de capacité",
    "risques à la baisse", "incertitude élevée",
    "récession", "contraction",
    "inférieure à la cible", "sous la cible",
    "inflation modérée", "inflation s'atténue", "désinflation",
    "détente supplémentaire", "nouvelles baisses",
}


def get_lexicons():
    """Retourne (hawkish_terms, dovish_terms) en union EN+FR, en minuscules."""
    hawkish = {t.lower() for t in HAWKISH_EN | HAWKISH_FR}
    dovish = {t.lower() for t in DOVISH_EN | DOVISH_FR}
    return hawkish, dovish


if __name__ == "__main__":
    h, d = get_lexicons()
    print(f"Hawkish terms : {len(h)}")
    print(f"Dovish terms : {len(d)}")
    print("\nExemples hawkish :")
    for t in sorted(h)[:8]:
        print(f"  {t}")
    print("\nExemples dovish :")
    for t in sorted(d)[:8]:
        print(f"  {t}")
