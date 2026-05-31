"""Regenerate reports/img/q9_kategorije.png in the ORIGINAL clean style (green horizontal
bars = median, red dots = mean, 'X.XX € (n=N)' labels, dashed overall-median line) with
current data and the CURRENT notebook categorization (cell 82), so it matches the report."""
import os
os.environ["MPLBACKEND"] = "Agg"
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "reports", "img", "q9_kategorije.png")

plt.rcParams.update({
    "figure.dpi": 110, "font.family": "sans-serif", "font.size": 11,
    "axes.titlesize": 15, "axes.titleweight": "bold", "axes.labelsize": 12,
    "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--", "grid.color": "#E0E0E0",
})

data = pd.read_csv(os.path.join(DATA, "data.csv"))


# --- notebook cell 82 categorize() (verbatim) ---
def categorize(title):
    if "POUČEVAN" in title or "INŠTRUKCIJ" in title or "TUTOR" in title:
        return "POUČEVANJE / INŠTRUKCIJE"
    if "PROMOCIJ" in title or "POSPEŠEVAN" in title or "ANKETIRAN" in title:
        return "PROMOCIJE"
    if "ČIŠČENJ" in title:
        return "ČIŠČENJE"
    if "RECEPCIJ" in title or "TURIZ" in title:
        return "RECEPCIJA / TURIZEM"
    if "ZDRAVSTV" in title or " NEGA" in title or "FIZIOTER" in title or "MEDICIN" in title or "KINEZIOLOG" in title:
        return "ZDRAVSTVO / NEGA"
    if "OTROK" in title or "OTROČ" in title or "VARSTV" in title or "ANIMATOR" in title:
        return "DELO Z OTROKI"
    if "DOSTAV" in title or "RAZVOZ" in title or "KURIR" in title or "ŠOFER" in title:
        return "DOSTAVA / PREVOZ"
    if "KLICNI" in title or "TELEFONIST" in title:
        return "KLICNI CENTER"
    if "MONTAŽ" in title or "GRADBEN" in title or "ELEKTROTEHN" in title or "MONTER" in title:
        return "TEHNIČNO / MONTAŽA"
    if "MARKETING" in title or "TRŽENJ" in title:
        return "MARKETING"
    if "PROGRAMIR" in title or " IT " in title or title.startswith("IT ") or title.endswith(
            " IT") or "SPLETN" in title or "RAČUNALNIŠ" in title:
        return "IT / RAČUNALNIŠTVO"
    if "STREŽB" in title or "KUHINJ" in title or "NATAKAR" in title or "POMIVANJ" in title:
        return "GOSTINSTVO"
    if "TRGOVIN" in title or "PRODAJ" in title or "BLAGAJN" in title or "BENCINSK" in title or "POLNJENJ POLIC" in title:
        return "TRGOVINA / PRODAJA"
    if "ADMINISTR" in title or "TAJNIK" in title:
        return "ADMINISTRACIJA"
    if "PROIZVODNJ" in title or "PAKIRAN" in title or "SKLADIŠČ" in title:
        return "PROIZVODNJA / SKLADIŠČE"
    if "FIZIČN" in title or "DVIGOVAN" in title or "NAKLAD" in title:
        return "FIZIČNO DELO"
    return "OSTALO"


titles = (data["title"].fillna("") + " " + data["subtitle"].fillna("")).str.upper()
data["category"] = titles.map(categorize)

# --- per-category stats (cell 82 avg_salary_by: rows with hourly_rate_neto) ---
d = data[data["hourly_rate_neto"].notna()]
stats = (d.groupby("category")["hourly_rate_neto"]
         .agg(median="median", mean="mean", count="count"))
stats = stats.sort_values(["median", "mean"], ascending=[True, True])  # barh -> largest on top
overall_median = d["hourly_rate_neto"].median()

# --- clean chart ---
fig, ax = plt.subplots(figsize=(11.8, 8.0))
GREEN = "#4CAF50"
y = range(len(stats))
bars = ax.barh(list(y), stats["median"].values, color=GREEN, edgecolor="white", height=0.72, zorder=2)
ax.set_yticks(list(y))
ax.set_yticklabels(stats.index)
# mean dots
ax.scatter(stats["mean"].values, list(y), color="#D62728", s=70, zorder=4)
# value + n labels
for yi, (med, n) in enumerate(zip(stats["median"].values, stats["count"].values)):
    ax.text(med + 0.08, yi, f"{med:.2f} € (n={int(n)})", va="center", ha="left", fontsize=10, zorder=5)
# overall median line
ax.axvline(overall_median, color="#9E9E9E", linestyle="--", linewidth=1.6, zorder=1)

ax.set_xlim(7.5, 14)
ax.set_xlabel("Neto urna postavka (€/h)")
ax.set_title("Mediana plače po kategorijah dela")
ax.tick_params(axis="y", length=0)

legend_elems = [
    Line2D([0], [0], marker="o", color="white", markerfacecolor="#D62728", markersize=10, label="Povprečje"),
    Line2D([0], [0], color="#9E9E9E", linestyle="--", linewidth=1.6,
           label=f"Skupna mediana ({overall_median:.2f} €/h)"),
]
ax.legend(handles=legend_elems, loc="lower right", framealpha=0.95)

plt.tight_layout()
fig.savefig(OUT, dpi=110, facecolor="white")
print("saved", OUT)
from PIL import Image
print("size", Image.open(OUT).size)
print("overall median:", round(overall_median, 3))
print(stats.sort_values("median", ascending=False).round(2).to_string())
