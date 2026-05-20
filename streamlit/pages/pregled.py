"""Pregled: filtriraj oglase + zemljevid + tabela rezultatov."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.categorize import CATEGORIES
from utils.data_loader import (
    load_data,
    load_geojson,
    normalize_region_name,
)

st.title("Pregled oglasov")
st.caption(
    "Filtriraj zbirko po kategoriji in plači. Zemljevid kaže izbrano metriko po regijah."
)

data = load_data()
geojson = load_geojson()

metrics_placeholder = st.container()
st.divider()

st.subheader("Zemljevid Slovenije")

metric_choice = st.radio(
    "Prikaži po regijah:",
    options=["Število oglasov", "Mediana neto urne postavke (€/h)"],
    horizontal=True,
)

with st.container(border=True):
    st.subheader("Filtri")

    sel_categories = st.multiselect(
        "Kategorija dela",
        CATEGORIES,
        default=CATEGORIES
    )

    hourly_all = data.dropna(subset=["hourly_rate_neto"])["hourly_rate_neto"]
    min_rate, max_rate = float(hourly_all.min()), float(hourly_all.max())

    c1, _ = st.columns([1, 3])

    with c1:
        sel_rate = st.slider(
            "Razpon neto urne postavke (€/h)",
            min_value=min_rate,
            max_value=max_rate,
            value=(min_rate, max_rate),
            step=0.1,
        )

mask = (
        data["category"].isin(sel_categories)
        & data["hourly_rate_neto"].notna()
        & data["hourly_rate_neto"].between(sel_rate[0], sel_rate[1])
)
filtered = data[mask]

with metrics_placeholder:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Zadetkov", f"{len(filtered):,}".replace(",", "."))
    hourly_f = filtered.dropna(subset=["hourly_rate_neto"])
    if len(hourly_f) > 0:
        c2.metric("Mediana plače", f"{hourly_f['hourly_rate_neto'].median():.2f} €/h")
        c3.metric("Povprečje plače", f"{hourly_f['hourly_rate_neto'].mean():.2f} €/h")
    else:
        c2.metric("Mediana plače", "–")
        c3.metric("Povprečje plače", "–")
    c4.metric("Različnih podjetij", f"{filtered['company'].nunique():,}".replace(",", "."))

if len(filtered) == 0:
    st.warning("Trenutni filtri ne vrnejo nobenega oglasa.")
    st.stop()

if metric_choice == "Število oglasov":
    region_agg = (
        filtered.groupby("normalized_region").size().rename("Vrednost").reset_index()
    )
    color_scale = "Blues"
    fmt = ":,.0f"
    range_color = None
else:
    region_agg = (
        hourly_f.groupby("normalized_region")["hourly_rate_neto"]
        .median()
        .rename("Vrednost")
        .reset_index()
    )
    color_scale = "Blues"
    fmt = ":.2f"
    if len(region_agg) > 0:
        lo, hi = region_agg["Vrednost"].min(), region_agg["Vrednost"].max()
        range_color = (lo - 0.1, hi + 0.1)
    else:
        range_color = None

if len(region_agg) > 0:
    region_agg["region_geo"] = region_agg["normalized_region"].apply(normalize_region_name)
    fig = px.choropleth_map(
        region_agg,
        geojson=geojson,
        locations="region_geo",
        featureidkey="properties.SR_UIME",
        color="Vrednost",
        color_continuous_scale=color_scale,
        range_color=range_color,
        map_style="carto-positron",
        zoom=6.7,
        center={"lat": 46.15, "lon": 14.95},
        opacity=0.7,
        hover_name="normalized_region",
        hover_data={"Vrednost": fmt, "region_geo": False},
        labels={"Vrednost": metric_choice},
    )
    fig.update_layout(height=520, margin=dict(l=0, r=0, t=10, b=0))

    # Apple-like okvirček (zaobljen, mehka senca)
    st.markdown(
        """
        <style>
        div[data-testid="stPlotlyChart"] {
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.05);
            border: 1px solid rgba(0,0,0,0.08);
        }
        span[data-baseweb="tag"] {
            background-color: #e0e0e0 !important;
            color: #333333 !important;
        }
        span[data-baseweb="tag"] span {
            color: #333333 !important;
        }
        span[data-baseweb="tag"] svg {
            fill: #666666 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Za izbrane filtre ni dovolj podatkov za prikaz na zemljevidu.")

st.divider()

st.subheader("Tabela zadetkov")

show_cols = [
    "title",
    "company",
    "normalized_city",
    "normalized_region",
    "category",
    "hourly_rate_neto",
    "payment_label",
    "schedule_label",
    "open_positions",
    "first_seen",
    "last_seen",
]
display_df = filtered[show_cols].copy().rename(
    columns={
        "title": "Naslov",
        "company": "Delodajalec",
        "normalized_city": "Mesto",
        "normalized_region": "Regija",
        "category": "Kategorija",
        "hourly_rate_neto": "€/h neto",
        "payment_label": "Tip plačila",
        "schedule_label": "Urnik",
        "open_positions": "Prosta mesta",
        "first_seen": "Prvič viden",
        "last_seen": "Zadnjič viden",
    }
)
display_df = display_df.sort_values("Prvič viden", ascending=False)

st.dataframe(
    display_df,
    use_container_width=True,
    height=400,
    column_config={
        "€/h neto": st.column_config.NumberColumn(format="%.2f €"),
        "Prvič viden": st.column_config.DatetimeColumn(format="DD.MM.YYYY"),
        "Zadnjič viden": st.column_config.DatetimeColumn(format="DD.MM.YYYY"),
    },
    hide_index=True,
)

st.subheader("Podroben pogled na oglas")

search_q = st.text_input(
    "Poišči oglas",
    placeholder="Naslov, podjetje ali ID …",
)

if search_q:
    q = search_q.strip().lower()
    search_mask = (
            filtered["title"].str.lower().str.contains(q, na=False)
            | filtered["company"].str.lower().str.contains(q, na=False)
            | filtered["id"].astype(str).str.contains(q, na=False)
    )
    searchable = filtered[search_mask]
else:
    searchable = filtered

st.caption(
    f"Zadetkov: {len(searchable):,}".replace(",", ".")
    + ("" if not search_q else f" za »{search_q}«")
)

if len(searchable) == 0:
    st.info("Brez zadetkov. Sprosti iskanje ali popravi poizvedbo.")
else:
    MAX_SHOWN = 200
    truncated = searchable.head(MAX_SHOWN)
    options = [
        f"#{row['id']} – {row['title']} ({row['company']})"
        for _, row in truncated.iterrows()
    ]
    if len(searchable) > MAX_SHOWN:
        st.caption(f"Pokazanih je prvih {MAX_SHOWN}. Zoži iskanje za več relevantnih zadetkov.")

    sel = st.selectbox("Izberi oglas", options, index=0)
    sel_id = int(sel.split(" – ")[0].lstrip("#"))
    row = data[data["id"] == sel_id].iloc[0]
    with st.container(border=True):
        st.markdown(f"### {row['title']}")
        if pd.notna(row["subtitle"]) and row["subtitle"]:
            st.markdown(f"**{row['subtitle']}**")
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f"**Delodajalec**\n\n{row['company']}")
        m2.markdown(f"**Lokacija**\n\n{row['normalized_city'] or '–'}")
        rate_text = (
            f"{row['hourly_rate_neto']:.2f} €/h"
            if pd.notna(row["hourly_rate_neto"])
            else row["payment_label"] or "–"
        )
        m3.markdown(f"**Plačilo**\n\n{rate_text}")
        m4.markdown(f"**Urnik**\n\n{row['schedule_label'] or '–'}")
        st.markdown("---")
        st.markdown("**Opis dela:**")
        st.write(row["description"] or "*(brez opisa)*")
