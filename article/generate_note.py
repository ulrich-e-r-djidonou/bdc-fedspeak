"""
Génère la note descriptive : indice de ton BdC 2009-2026
Output : article/note_descriptive_ton_bdc.docx
"""
import csv
import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TONE_CSV = os.path.join(BASE, "data", "processed", "tone_index.csv")
FIG1 = os.path.join(BASE, "article", "figures", "tone_vs_rate.png")
FIG2 = os.path.join(BASE, "article", "figures", "tone_episodes_macklem.png")
OUT = os.path.join(BASE, "article", "note_descriptive_ton_bdc.docx")


def load_tone():
    with open(TONE_CSV, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)


def add_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return p


def add_para(doc, text, bold=False, italic=False, size=11, space_before=0, space_after=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    return p


def add_caption(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(10)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(text)
    run.italic = True
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)


def build_yearly_stats(rows):
    from collections import defaultdict
    by_year = defaultdict(list)
    for r in rows:
        y = r["date"][:4]
        by_year[y].append(float(r["tone_score_net"]))
    return {y: by_year[y] for y in sorted(by_year)}


def main():
    rows = load_tone()

    doc = Document()

    # --- marges ---
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(3.0)
        section.right_margin = Cm(3.0)

    # === TITRE ===
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_after = Pt(4)
    run = title.add_run(
        "Mesurer le ton des communications de la Banque du Canada :\n"
        "un indice hawkish/dovish sur la période 2009-2026"
    )
    run.bold = True
    run.font.size = Pt(14)

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub.paragraph_format.space_after = Pt(14)
    sub.add_run("Note descriptive — Projet bdc-fedspeak | Ulrich Djidonou | Mai 2026").font.size = Pt(10)

    # === RÉSUMÉ ===
    add_heading(doc, "Résumé", level=2)
    add_para(doc,
        "Cette note présente un indice de ton hawkish/dovish construit à partir des 127 communiqués "
        "de décision de taux de la Banque du Canada publiés entre janvier 2009 et avril 2026. "
        "L'indice est calculé par comptage de termes dans un lexique adapté de la littérature "
        "(Apel et Blix Grimaldi, 2014 ; Picault et Renault, 2017). Les résultats montrent que "
        "le ton des communiqués anticipe systématiquement les retournements de politique monétaire "
        "et que le cycle Macklem (2022-2026) constitue l'épisode le plus documenté en termes de "
        "signal hawkish avant les hausses de taux.",
        size=10)

    doc.add_paragraph()

    # === 1. CONTEXTE ET QUESTION ===
    add_heading(doc, "1. Contexte et question de recherche", level=1)
    add_para(doc,
        "Les décisions de politique monétaire de la Banque du Canada ne se limitent pas au "
        "changement du taux directeur. Le texte des communiqués officiels (Fixed Announcement "
        "Dates, FAD) contient une information prospective — la guidance — qui conditionne les "
        "anticipations des marchés financiers au-delà de la décision elle-même. Cette note "
        "s'inscrit dans la littérature sur le 'fedspeak' en posant la question suivante : "
        "le ton des communiqués de la BdC est-il mesurable, systématique, et lié aux décisions "
        "de taux qui suivent ?")

    # === 2. DONNÉES ET MÉTHODOLOGIE ===
    add_heading(doc, "2. Données et méthodologie", level=1)

    add_heading(doc, "2.1 Données", level=2)
    add_para(doc,
        "Les communiqués FAD sont collectés via le sitemap WordPress de bankofcanada.ca "
        "(pattern d'URL fad-press-release, disponible depuis janvier 2009). L'échantillon "
        "final comprend 127 annonces après nettoyage du boilerplate institutionnel. "
        "Le taux directeur cible est issu de l'API Valet de la BdC (série V39079).")

    add_heading(doc, "2.2 Construction de l'indice de ton", level=2)
    add_para(doc,
        "L'indice de ton est construit par comptage de termes dans un lexique bilingue "
        "(anglais/français) classifiant les expressions en deux catégories :")

    p = doc.add_paragraph(style="List Bullet")
    p.add_run("Hawkish (restrictif) : ").bold = True
    p.add_run(
        "termes signalant un resserrement monétaire, des pressions inflationnistes, "
        "ou une économie en surchauffe (ex. : 'tightening', 'inflation pressures', "
        "'further increases', 'excess demand')."
    )
    p.paragraph_format.space_after = Pt(2)

    p = doc.add_paragraph(style="List Bullet")
    p.add_run("Dovish (accommodant) : ").bold = True
    p.add_run(
        "termes signalant un assouplissement, des risques à la baisse, "
        "ou un soutien à la croissance (ex. : 'easing', 'downside risks', "
        "'accommodative', 'uncertainty', 'tariffs')."
    )
    p.paragraph_format.space_after = Pt(8)

    add_para(doc,
        "Le lexique est adapté de Apel et Blix Grimaldi (2014) et Picault et Renault (2017), "
        "avec des ajouts propres au vocabulaire de la BdC. Le score net est calculé comme suit :")

    formula = doc.add_paragraph()
    formula.alignment = WD_ALIGN_PARAGRAPH.CENTER
    formula.paragraph_format.space_after = Pt(8)
    run = formula.add_run("Indice de ton = (N_hawkish - N_dovish) / (N_hawkish + N_dovish)")
    run.font.size = Pt(11)
    run.bold = True

    add_para(doc,
        "L'indice prend des valeurs dans [-1, 1] : +1 indique un communiqué entièrement "
        "hawkish, -1 un communiqué entièrement dovish, 0 un ton neutre ou équilibré. "
        "Les communiqués sans aucun terme des deux catégories reçoivent un score nul "
        "et sont classés 'neutres' (3 observations sur 127).")

    # === 3. RÉSULTATS DESCRIPTIFS ===
    add_heading(doc, "3. Résultats descriptifs", level=1)

    add_heading(doc, "3.1 Évolution de l'indice sur l'ensemble de la période", level=2)
    add_para(doc,
        "La Figure 1 représente l'indice de ton de chaque annonce FAD entre 2009 et 2026, "
        "superposé à la trajectoire du taux directeur. Cinq grands épisodes ressortent :")

    episodes = [
        ("Crise financière (2009-2010)", "ton systématiquement dovish (moy. = -0,92 en 2009), "
         "avec des scores de -1,0 lors des premières baisses de taux d'urgence."),
        ("Reprise progressive (2011-2017)", "dominance dovish persistante malgré quelques "
         "signaux hawkish en 2011 et 2014, reflétant une croissance canadienne fragile et "
         "des chocs pétroliers (2015-2016)."),
        ("Resserrement pré-COVID (2017-2018)", "basculement hawkish net : score moyen de +0,47 "
         "en 2018, avec 3 annonces à +1,0 — le signal le plus restrictif de la décennie avant "
         "le cycle Macklem."),
        ("COVID (2020-2021)", "retour au score plancher : moy. = -0,95 en 2020, reflétant "
         "l'engagement d'un maintien des taux à la borne effective basse."),
        ("Cycle Macklem (2022-2026)", "épisode le plus documenté : 10 hausses consécutives "
         "accompagnées de scores hawkish élevés (moy. = +0,55 en 2022), suivies d'une "
         "détente progressive à partir de mi-2024 (moy. = -0,74 en 2025)."),
    ]
    for title_ep, desc in episodes:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(f"{title_ep} : ").bold = True
        p.add_run(desc)
        p.paragraph_format.space_after = Pt(3)

    doc.add_paragraph()

    # Figure 1
    if os.path.exists(FIG1):
        doc.add_picture(FIG1, width=Inches(6.0))
        last_para = doc.paragraphs[-1]
        last_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_caption(doc,
            "Figure 1. Indice de ton des communiqués FAD de la Banque du Canada (2009-2026) "
            "et taux directeur cible. Points rouges = ton hawkish, bleus = dovish, gris = neutre. "
            "Source : bankofcanada.ca, API Valet. Calculs de l'auteur.")

    # Tableau annuel
    add_heading(doc, "3.2 Statistiques annuelles", level=2)
    add_para(doc,
        "Le Tableau 1 résume les statistiques de l'indice par année. "
        "L'hétérogénéité interannuelle est marquée : l'écart entre 2022 (+0,55) "
        "et 2020 (-0,95) représente le basculement le plus rapide observé dans l'échantillon.")

    yearly = build_yearly_stats(rows)
    headers = ["Année", "N annonces", "Score moyen", "Min", "Max", "Orientation dominante"]
    table = doc.add_table(rows=1 + len(yearly), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        hdr[i].paragraphs[0].runs[0].bold = True
        hdr[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_bg(hdr[i], "2E4057")
        for run in hdr[i].paragraphs[0].runs:
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            run.font.size = Pt(9)

    for idx, (year, vals) in enumerate(yearly.items()):
        moy = sum(vals) / len(vals)
        orientation = "Hawkish" if moy > 0.1 else ("Dovish" if moy < -0.1 else "Neutre")
        bg = "FFE8E8" if orientation == "Hawkish" else ("E8F0FF" if orientation == "Dovish" else "F5F5F5")
        row_cells = table.rows[idx + 1].cells
        values = [year, str(len(vals)), f"{moy:+.3f}", f"{min(vals):.2f}", f"{max(vals):.2f}", orientation]
        for i, v in enumerate(values):
            row_cells[i].text = v
            row_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            row_cells[i].paragraphs[0].runs[0].font.size = Pt(9)
            set_cell_bg(row_cells[i], bg)

    add_caption(doc,
        "Tableau 1. Statistiques annuelles de l'indice de ton (2009-2026). "
        "Fond rouge = orientation hawkish dominante ; fond bleu = orientation dovish.")

    # Tableau Top hawkish / dovish
    add_heading(doc, "3.3 Communiqués aux tons extrêmes", level=2)
    add_para(doc,
        "Le Tableau 2 identifie les cinq annonces les plus hawkish et les cinq les plus dovish "
        "de l'échantillon. Les annonces les plus hawkish se concentrent sur deux épisodes : "
        "le resserrement de 2018 et le cycle d'urgence de 2022. Les annonces les plus dovish "
        "correspondent toutes à la gestion de la crise financière de 2009.")

    hawk_top = sorted(rows, key=lambda r: float(r["tone_score_net"]), reverse=True)[:5]
    dove_top = sorted(rows, key=lambda r: float(r["tone_score_net"]))[:5]

    t2_headers = ["Date", "Taux (%)", "Chgt (bp)", "Score", "Résumé de l'annonce"]
    t2 = doc.add_table(rows=1 + len(hawk_top) + 1 + len(dove_top), cols=len(t2_headers))
    t2.style = "Table Grid"
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER

    # header principal
    hdr2 = t2.rows[0].cells
    for i, h in enumerate(t2_headers):
        hdr2[i].text = h
        hdr2[i].paragraphs[0].runs[0].bold = True
        hdr2[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_bg(hdr2[i], "2E4057")
        for run in hdr2[i].paragraphs[0].runs:
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            run.font.size = Pt(9)

    # Hawkish
    for idx, r in enumerate(hawk_top):
        row_cells = t2.rows[1 + idx].cells
        chgt = r["rate_change_bp"]
        chgt_str = f"+{int(float(chgt))}" if chgt and float(chgt) > 0 else (str(int(float(chgt))) if chgt else "-")
        title_short = r["title"].replace("Bank of Canada ", "BdC ")[:65]
        values = [r["date"], r["rate_pct"], chgt_str, f"{float(r['tone_score_net']):+.2f}", title_short]
        for i, v in enumerate(values):
            row_cells[i].text = v
            row_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            row_cells[i].paragraphs[0].runs[0].font.size = Pt(9)
            set_cell_bg(row_cells[i], "FFE8E8")

    # séparateur
    sep_row = t2.rows[1 + len(hawk_top)].cells
    sep_row[0].merge(sep_row[-1])
    sep_row[0].text = "5 communiqués les plus dovish"
    sep_row[0].paragraphs[0].runs[0].bold = True
    sep_row[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_cell_bg(sep_row[0], "2E4057")
    sep_row[0].paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    sep_row[0].paragraphs[0].runs[0].font.size = Pt(9)

    # Dovish
    base = 1 + len(hawk_top) + 1
    for idx, r in enumerate(dove_top):
        row_cells = t2.rows[base + idx].cells
        chgt = r["rate_change_bp"]
        chgt_str = f"{int(float(chgt))}" if chgt and float(chgt) != 0 else ("0" if chgt else "-")
        title_short = r["title"].replace("Bank of Canada ", "BdC ")[:65]
        values = [r["date"], r["rate_pct"], chgt_str, f"{float(r['tone_score_net']):+.2f}", title_short]
        for i, v in enumerate(values):
            row_cells[i].text = v
            row_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            row_cells[i].paragraphs[0].runs[0].font.size = Pt(9)
            set_cell_bg(row_cells[i], "E8F0FF")

    # insert subheader hawkish avant le premier bloc
    sep_row_top = t2.rows[1].cells
    # Reconstruire avec sous-titre hawkish dans Row 1 n'est pas simple en python-docx sans XML brut
    # On laisse le tableau tel quel et on ajoute une note en caption
    add_caption(doc,
        "Tableau 2. Cinq communiqués aux tons les plus hawkish (fond rouge) et dovish (fond bleu). "
        "Chgt = variation du taux directeur en points de base à l'annonce. Source : calculs de l'auteur.")

    # === 4. ZOOM CYCLE MACKLEM ===
    add_heading(doc, "4. Le cycle Macklem (2022-2026) : un cas d'école", level=1)
    add_para(doc,
        "Le cycle de politique monétaire amorcé sous Tiff Macklem en 2022 constitue l'épisode "
        "le mieux documenté de l'échantillon, tant par l'ampleur des mouvements de taux (de "
        "0,25 % à 5,0 % en 18 mois) que par la cohérence du signal textuel. La Figure 2 "
        "illustre la correspondance entre l'indice de ton et la trajectoire du taux directeur "
        "sur cette période.")

    add_para(doc,
        "Trois sous-épisodes ressortent. D'abord, la phase de resserrement (mars 2022 - "
        "juillet 2023) : 10 hausses de taux, précédées ou accompagnées d'un ton hawkish "
        "soutenu (score moyen de +0,55 en 2022). Le communiqué de septembre 2022 (+100 bp, "
        "score = +1,0) représente le pic de restrictivité. Ensuite, le plateau (juillet "
        "2023 - juin 2024) : le ton se neutralise progressivement, signalant la fin du cycle "
        "de hausse avant que la première baisse ne soit annoncée. Enfin, la phase de détente "
        "(juin 2024 - avril 2026) : le ton bascule résolument dovish, avec des scores proches "
        "de -1,0 lors des baisses consécutives de fin 2025 (-25 bp chacune), puis se stabilise "
        "légèrement à -0,14 en mars 2026 lors du premier maintien à 2,25 %.")

    add_para(doc,
        "Fait notable : le communiqué de janvier 2022 affiche un score de -0,60 malgré une "
        "hausse de 25 bp imminente, ce qui suggère que la BdC a d'abord tempéré ses "
        "communications avant de basculer vers une rhétorique de combat contre l'inflation.")

    if os.path.exists(FIG2):
        doc.add_picture(FIG2, width=Inches(6.0))
        last_para = doc.paragraphs[-1]
        last_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_caption(doc,
            "Figure 2. Cycle Macklem : indice de ton (barres) et taux directeur (courbe noire), "
            "2022-2026. Les étiquettes indiquent les variations de taux en points de base. "
            "Source : bankofcanada.ca, API Valet. Calculs de l'auteur.")

    # === 5. LIMITES ET PROCHAINES ÉTAPES ===
    add_heading(doc, "5. Limites et prochaines étapes", level=1)
    add_para(doc,
        "Cette note a trois limites principales. Premièrement, l'indice repose sur un lexique "
        "dichotomique qui ne capture pas la nuance ni le contexte : un terme hawkish dans une "
        "phrase de négation (ex. : 'we do not expect further tightening') reçoit le même poids "
        "qu'un usage positif. Deuxièmement, la couverture commence en 2009 en raison des "
        "contraintes du scraping par sitemap ; les communiqués antérieurs à 2009 nécessitent "
        "une extraction manuelle. Troisièmement, les données de marché intraday ne sont pas "
        "disponibles dans ce projet, ce qui limite la précision de l'étude d'événement aux "
        "fenêtres journalières.")

    add_para(doc,
        "Les prochaines étapes prévues sont : (1) l'étude d'événement formelle mesurant la "
        "réaction des rendements GoC et du taux de change CAD/USD à l'indice de ton en "
        "fenêtre J-1/J+1 ; (2) la décomposition Jarociński et Karadi (2020) pour séparer "
        "le choc de politique monétaire pure du choc d'information de la banque centrale ; "
        "(3) l'extension du lexique par apprentissage automatique supervisé.")

    # === RÉFÉRENCES ===
    add_heading(doc, "Références", level=1)
    refs = [
        "Apel, M. et Blix Grimaldi, M. (2014). The Information Content of Central Bank Minutes. "
        "Review of Economics, 65(1), 53-76.",
        "Jarociński, M. et Karadi, P. (2020). Deconstructing Monetary Policy Surprises : "
        "The Role of Information Shocks. American Economic Journal: Macroeconomics, 12(2), 1-43.",
        "Picault, M. et Renault, T. (2017). Words are not all created equal: A new measure "
        "of ECB communication. Journal of International Money and Finance, 79, 136-156.",
        "Banque du Canada (2009-2026). Communiqués de décision de taux (FAD). "
        "Récupérés via bankofcanada.ca.",
        "Banque du Canada (2026). API Valet — Données économiques et financières. "
        "https://www.bankofcanada.ca/valet/",
    ]
    for ref in refs:
        p = doc.add_paragraph(style="List Bullet")
        p.add_run(ref).font.size = Pt(10)
        p.paragraph_format.space_after = Pt(4)

    doc.save(OUT)
    print(f"Note generee : {OUT}")


if __name__ == "__main__":
    main()
