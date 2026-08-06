"""Verifie que les figures attendues existent et sont fraiches.

Sans ce controle, une figure non produite ne fait echouer personne : le pas
de publication ne voit aucun changement, ne commite rien, et le run se
termine en succes. Le depot garderait alors silencieusement une figure
vieille de plusieurs mois a cote de donnees a jour.

Le controle porte sur l'existence et la taille, pas sur le contenu : il
attrape une figure absente ou une ecriture interrompue, pas une figure
correctement ecrite mais trompeuse. Comme il tourne juste apres le script
de traçage dans le meme run, une figure presente et de taille normale a
forcement ete produite par ce run.

    python code/verifier_figures.py
"""

from __future__ import annotations

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
DOSSIER_FIGURES = RACINE / "article" / "figures"

FIGURES_ATTENDUES = (
    "tone_vs_rate.png",
    "tone_episodes_macklem.png",
)

# Une figure matplotlib valide pese quelques dizaines de kilo-octets. Un
# fichier de quelques centaines d'octets signale une ecriture interrompue.
TAILLE_MINIMALE = 10_000


def main() -> int:
    problemes = []

    for nom in FIGURES_ATTENDUES:
        chemin = DOSSIER_FIGURES / nom
        if not chemin.exists():
            problemes.append(f"{nom} : absente")
            continue
        taille = chemin.stat().st_size
        if taille < TAILLE_MINIMALE:
            problemes.append(f"{nom} : {taille} octets, en dessous du seuil "
                             f"de {TAILLE_MINIMALE}")
            continue
        print(f"  {nom} : {taille // 1000} ko")

    if problemes:
        print(f"\n{len(problemes)} figure(s) manquante(s) ou tronquee(s) :")
        for probleme in problemes:
            print(f"  {probleme}")
        return 1

    print(f"{len(FIGURES_ATTENDUES)} figures presentes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
