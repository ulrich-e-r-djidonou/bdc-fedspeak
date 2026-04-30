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
    "raise rates", "increase rates", "hike", "tighten", "tightening",
    "remove accommodation", "reduce stimulus", "withdraw stimulus",
    # vocabulaire d'inflation
    "inflation pressure", "inflation pressures", "inflationary pressure",
    "inflationary pressures", "above target", "elevated inflation",
    "persistent inflation", "broad-based price increases",
    "overheating", "excess demand", "capacity pressures",
    # croissance forte
    "strong growth", "robust growth", "solid expansion",
    "tight labour market", "tight labor market", "wage pressures",
    # forward guidance restrictif
    "further increases", "additional tightening", "policy needs to be more restrictive",
    "rates need to rise", "monetary policy will need to tighten",
}

DOVISH_EN = {
    # actions d'assouplissement
    "cut rates", "lower rates", "reduce rates", "ease", "easing",
    "accommodative", "stimulative", "supportive policy",
    # vocabulaire de croissance faible
    "weak growth", "subdued growth", "slowing economy", "economic slack",
    "downside risks", "elevated uncertainty", "weakness", "soft demand",
    "deteriorating", "contracting", "contraction", "recession",
    # désinflation
    "below target", "subdued inflation", "weak price pressures",
    "easing inflation", "disinflation", "inflation moderating",
    "inflation expected to ease", "inflation has slowed",
    # forward guidance accommodant
    "further cuts", "additional easing", "policy needs to remain accommodative",
    "support the economy", "more easing may be required",
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
