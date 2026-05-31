"""Regenerate reports/img/q3_regije_map.png — clean choropleth of median net hourly
rate per Slovenian statistical region, current data. Matplotlib-only (no geopandas)."""
import os, json
os.environ["MPLBACKEND"] = "Agg"
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection
import matplotlib.cm as cm
from matplotlib.colors import Normalize

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "reports", "img", "q3_regije_map.png")

# --- current data: median net hourly rate per region (same filter as notebook cell 39) ---
data = pd.read_csv(os.path.join(DATA, "data.csv"))
hr = data[(data["normalized_payment_type"] == "HOURLY")
          & (data["normalized_region"].notna())
          & (data["hourly_rate_neto"].notna())]
med = hr.groupby("normalized_region")["hourly_rate_neto"].median()
# index is upper-case region names; map to GeoJSON SR_UIME (title case, hyphen lower)
import re
def to_geo(name):
    t = name.title()
    return re.sub(r"-([A-ZŠŽČ])", lambda m: "-" + m.group(1).lower(), t)
med_geo = {to_geo(k): v for k, v in med.items()}

with open(os.path.join(DATA, "slovenia_regions.geojson"), encoding="utf-8") as f:
    geo = json.load(f)

def centroid(ring):
    """Area-weighted centroid (shoelace) of a polygon outer ring (lon,lat)."""
    a = np.array(ring)
    x, y = a[:, 0], a[:, 1]
    x1, y1 = np.roll(x, -1), np.roll(y, -1)
    cross = x * y1 - x1 * y
    A = cross.sum() / 2.0
    if abs(A) < 1e-12:
        return x.mean(), y.mean()
    cx = ((x + x1) * cross).sum() / (6 * A)
    cy = ((y + y1) * cross).sum() / (6 * A)
    return cx, cy

# --- color scale (RdYlGn), same family/look as original ---
# vmin below the data floor (8.00) so the floor maps to neutral yellow (not orange),
# keeping the muted look of the original; vmax covers the top region (Gorenjska 8.50).
VMIN, VMAX = 7.5, 8.5
norm = Normalize(vmin=VMIN, vmax=VMAX)
cmap = plt.get_cmap("RdYlGn")

mean_lat = 46.15
aspect = 1.0 / np.cos(np.radians(mean_lat))

fig, ax = plt.subplots(figsize=(9.0, 5.0))

# manual label nudges (lon,lat offset) where centroid is awkward
NUDGE = {
    "Obalno-kraška": (0.02, -0.04),
    "Osrednjeslovenska": (0.0, -0.05),
    "Goriška": (-0.03, 0.05),
    "Jugovzhodna Slovenija": (0.10, -0.06),
    "Primorsko-notranjska": (-0.05, -0.02),
}

patches, colors = [], []
for feat in geo["features"]:
    name = feat["properties"]["SR_UIME"]
    ring = feat["geometry"]["coordinates"][0]
    val = med_geo.get(name, np.nan)
    poly = MplPolygon(np.array(ring), closed=True)
    patches.append(poly)
    colors.append(cmap(norm(val)) if not np.isnan(val) else (0.9, 0.9, 0.9, 1))

pc = PatchCollection(patches, facecolors=colors, edgecolor="white", linewidths=1.1, zorder=1)
ax.add_collection(pc)

# region labels: name + value
for feat in geo["features"]:
    name = feat["properties"]["SR_UIME"]
    ring = feat["geometry"]["coordinates"][0]
    cx, cy = centroid(ring)
    dx, dy = NUDGE.get(name, (0, 0))
    cx += dx; cy += dy
    val = med_geo.get(name, np.nan)
    label = f"{name}\n{val:.2f} €" if not np.isnan(val) else name
    ax.text(cx, cy, label, ha="center", va="center", fontsize=8.0,
            fontweight="bold", color="#1a1a1a", zorder=3,
            linespacing=1.25)

# fit bounds
all_xy = np.vstack([np.array(f["geometry"]["coordinates"][0]) for f in geo["features"]])
ax.set_xlim(all_xy[:, 0].min() - 0.05, all_xy[:, 0].max() + 0.05)
ax.set_ylim(all_xy[:, 1].min() - 0.05, all_xy[:, 1].max() + 0.05)
ax.set_aspect(aspect)
ax.axis("off")
ax.set_title("Mediana neto urne postavke po statističnih regijah Slovenije",
             fontsize=13, fontweight="bold", pad=12)

# colorbar
sm = cm.ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, fraction=0.035, pad=0.01,
                    ticks=np.round(np.arange(VMIN, VMAX + 0.001, 0.1), 1))
cbar.set_label("€/h", rotation=0, labelpad=10, va="center")
cbar.ax.tick_params(labelsize=8)

fig.savefig(OUT, dpi=150, bbox_inches="tight", facecolor="white")
print("saved", OUT)
from PIL import Image
print("size", Image.open(OUT).size)
print("region medians:")
for n in ["Gorenjska","Goriška","Osrednjeslovenska","Obalno-kraška","Koroška","Zasavska"]:
    print(" ", n, med_geo.get(n))
