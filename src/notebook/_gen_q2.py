"""Refresh reports/img/q2_dvigi.png with current data. Replicates notebook cells 33 + 35
(figure only), same style."""
import os
os.environ["MPLBACKEND"] = "Agg"
import pandas as pd
import matplotlib.pyplot as plt

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "reports", "img", "q2_dvigi.png")

plt.rcParams.update({
    "figure.dpi": 150, "font.family": "sans-serif", "font.size": 10,
    "axes.titlesize": 13, "axes.titleweight": "bold", "axes.labelsize": 11,
    "axes.grid": True, "grid.alpha": 0.3, "grid.linestyle": "--", "grid.color": "#E0E0E0",
})
COLORS = plt.cm.tab10.colors

data = pd.read_csv(os.path.join(DATA, "data.csv"), parse_dates=["first_seen", "last_seen"])
changes = pd.read_csv(os.path.join(DATA, "changes.csv"), parse_dates=["changed_at"])

# --- cell 33 ---
rate_changes = changes[changes["field"] == "hourly_rate_neto"].copy()
rate_changes["old_value"] = pd.to_numeric(rate_changes["old_value"], errors="coerce")
rate_changes["new_value"] = pd.to_numeric(rate_changes["new_value"], errors="coerce")
rate_changes = rate_changes.dropna(subset=["old_value", "new_value"])
rate_changes["diff"] = rate_changes["new_value"] - rate_changes["old_value"]
rate_changes = rate_changes.merge(data[["id", "first_seen"]], left_on="listing_id", right_on="id", how="left")
rate_changes["days_after_post"] = (rate_changes["changed_at"] - rate_changes["first_seen"]).dt.days
raises = rate_changes[rate_changes["diff"] > 0]

# --- cell 35 figure ---
bins_size = [0, 0.25, 0.50, 1.00, 2.00, float("inf")]
labels_size = ["0 – 0,25 €", "0,25 – 0,50 €", "0,50 – 1,00 €", "1,00 – 2,00 €", "2,00 € +"]
bins_days = [-1, 1, 3, 7, 14, 21, 28, float("inf")]
labels_days = ["0 – 1 dan", "2 – 3 dni", "4 – 7 dni", "8 – 14 dni", "15 – 21 dni", "22 – 28 dni", "29+ dni"]

rate_changes["abs_diff"] = rate_changes["diff"].abs()
rate_changes["interval_size"] = pd.cut(rate_changes["abs_diff"], bins=bins_size, labels=labels_size, right=True)
rate_changes["interval_days"] = pd.cut(rate_changes["days_after_post"], bins=bins_days, labels=labels_days, right=True)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 3.5), layout="constrained")

raises_binned = rate_changes[rate_changes["diff"] > 0].groupby("interval_size", observed=False).size()
cuts_binned = rate_changes[rate_changes["diff"] < 0].groupby("interval_size", observed=False).size()

bars_r = ax1.barh(labels_size, raises_binned.values, color="#4CAF50", edgecolor="white", label="Dvig ↑")
ax1.bar_label(bars_r, label_type="center", color="white", fontweight="bold", fontsize=10)
if cuts_binned.sum() > 0:
    bars_c = ax1.barh(labels_size, cuts_binned.values, left=raises_binned.values,
                      color="#E53935", edgecolor="white", label="Znižanje ↓")
    ax1.bar_label(bars_c, padding=3, fontsize=10)
    ax1.legend(loc="lower right")
ax1.set_xlabel("Število sprememb")
ax1.set_title("Velikost sprememb urne postavke")
ax1.set_xlim(right=max(raises_binned.max(), 1) * 1.3)
ax1.invert_yaxis()

days_binned = rate_changes.groupby("interval_days", observed=False).size()
bars_d = ax2.barh(labels_days, days_binned.values, color=COLORS[0], edgecolor="white")
ax2.bar_label(bars_d, padding=3, fontsize=10)
ax2.set_xlabel("Število sprememb")
ax2.set_title("Po koliko dneh pride do spremembe plače?")
ax2.set_xlim(right=max(days_binned.max(), 1) * 1.3)
ax2.invert_yaxis()

fig.savefig(OUT, dpi=100, bbox_inches="tight", facecolor="white")
print("saved", OUT)
from PIL import Image
print("size", Image.open(OUT).size)
print("raises total:", int(raises_binned.sum()), "| cuts:", int(cuts_binned.sum()),
      "| changes:", len(rate_changes))
print("size bins:", raises_binned.to_dict())
print("days bins:", days_binned.to_dict())
