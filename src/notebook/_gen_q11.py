"""Regenerate reports/img/q11_znacke.png in the ORIGINAL clean style with current data:
title 'napovedujejo...', x-label with overall median, green/gray/red bars + value labels."""
import os
os.environ["MPLBACKEND"] = "Agg"
import pandas as pd
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "reports", "img", "q11_znacke.png")

# Matplotlib stil (same rcParams as notebook cell 1)
plt.rcParams.update({
    "figure.dpi": 150, "font.family": "sans-serif", "font.size": 10,
    "axes.titlesize": 13, "axes.titleweight": "bold", "axes.labelsize": 11,
    "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--", "grid.color": "#E0E0E0",
})

data = pd.read_csv(os.path.join(DATA, "data.csv"))

# --- replicate notebook cell 96 (Q11 step 1) ---
hourly = data[(data["normalized_payment_type"] == "HOURLY")
              & data["hourly_rate_neto"].notna()].copy()
hourly = hourly.drop_duplicates(subset="description").reset_index(drop=True)
text_field = (hourly["title"].fillna("") + " " + hourly["description"].fillna("")).str.lower()
overall_median = hourly["hourly_rate_neto"].median()

KEYWORD_PATTERNS = {
    "inštrukcije, poučevanje": r"\b(?:in[šs]trukcij|tutor|pou[čc]evan|pomo[čc]\s+pri\s+u[čc]enj)",
    "fitnes, šport, vodenje vadb": r"\b(?:fitnes|aerobik|vaditelj|trener|pilates|joga|plesn\s+u[čc]itel)",
    "promocije, anketiranje": r"\b(?:promocij|pospe[šs]evan|degustacij|anketiran)",
    "delo z otroki, animacije": r"\b(?:otro[čc]|otrok|vars?tv|animator)",
    "modelska dela, fotografiranje": r"\b(?:model\s|modeli\s+|fotografiran|snemanj|statisti)",
    "računalniške veščine, oblikovanje": r"\b(?:excel|word|programir|python|sql|figma|java|photoshop|adobe|oblikov\w*|video|grafi[čc])",
    "zdravstvo, nega, fizioter., kozmet.": r"\b(?:zdravstven|medicin|nega|fizioter|kineziolog|farmac|psiholog|psihoterap|maser|masa[žz]|kozmet)",
    "klicni center, telefon. prodaja": r"\b(?:klicni\s+cent|kontaktni\s+cent|call\s+center|telefonist|telefonsk[aei]\s+(?:prodaj|anketiranj|stik|kontakt|komunikac))",
    "prevoz, dostava": r"\b(?:prevoz|dostav|razvoz|kurir|[šs]ofer)",
    "gradbeništvo": r"\b(?:gradben|monter|monta[žz]|elektrikar|vodoinstal)",
    "marketing": r"\b(?:marketing|tr[žz]enj|copywrit)",
    "vozniški izpit / lasten avto": r"\b(?:vozni[šs]ki|izpit\s+b|lasten\s+avto)",
    "strežba, gostinstvo": r"\b(?:stre[žz]b|natakar|kuhinj)",
    "trgovina, blagajna": r"\b(?:trgovin|polnjenje\s+polic|blagajn)",
    "fizično delo, skladišče": r"\b(?:fizi[čc]n|dvigovan|skladi[šs][čc])",
}

rows = []
for label, pattern in KEYWORD_PATTERNS.items():
    mask = text_field.str.contains(pattern, regex=True, na=False)
    median_z = hourly.loc[mask, "hourly_rate_neto"].median()
    median_brez = hourly.loc[~mask, "hourly_rate_neto"].median()
    rows.append({"značka": label, "razlika €/h": round(median_z - median_brez, 2)})
kw_table = pd.DataFrame(rows).sort_values("razlika €/h", ascending=False).reset_index(drop=True)

# --- clean chart (original q11_znacke.png style) ---
order = kw_table.sort_values("razlika €/h")  # ascending -> largest at top
colors = ["#C44E52" if d < 0 else ("#7FB069" if d > 0.3 else "#BFBFBF")
          for d in order["razlika €/h"]]

fig, ax = plt.subplots(figsize=(9.6, 5.2))
bars = ax.barh(order["značka"], order["razlika €/h"], color=colors)
ax.axvline(0, color="black", linewidth=0.9)
ax.set_xlabel(f"Razlika v mediani plačila (€/h)   |   Splošna mediana = {overall_median:.2f} €/h")
ax.set_title("Katere besede v opisu napovedujejo višje/nižje plačilo")
for b, v in zip(bars, order["razlika €/h"]):
    ax.text(v + (0.06 if v >= 0 else -0.06), b.get_y() + b.get_height() / 2,
            f"{v:+.2f}", va="center", ha="left" if v >= 0 else "right", fontsize=9)
ax.margins(x=0.10)
plt.tight_layout()
fig.savefig(OUT, dpi=150, facecolor="white")
print("saved", OUT)
from PIL import Image
print("size", Image.open(OUT).size)
print("overall median (Splošna mediana):", round(overall_median, 2))
print(kw_table.to_string())
