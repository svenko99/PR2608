import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import plotly.graph_objects as go
import streamlit as st

from utils.categorize import CATEGORIES
from utils.data_loader import load_data
from utils.model import (
    category_from_text,
    find_similar,
    predict_structured,
    predict_text,
    train_models,
)

st.title("Napovedovalec razreda plače")
st.caption(
    "Model napove razred neto urne postavke (nizka / srednja / visoka)."
)

data = load_data()
models = train_models()

st.markdown(
    f"""
**Meje razredov** (33. in 66. percentil oglasov z znano postavko):

- **nizka** - < {models.q33:.2f} €/h
- **srednja** - {models.q33:.2f} - {models.q66:.2f} €/h
- **visoka** - > {models.q66:.2f} €/h
"""
)

CLASS_COLORS = {"nizka": "#F39C12", "srednja": "#F1C40F", "visoka": "#27AE60"}


def render_prediction(pred: str, probs: dict[str, float]) -> None:
    st.markdown(f"### Napovedan razred: **{pred.upper()}**")

    classes = ["nizka", "srednja", "visoka"]
    values = [probs.get(c, 0) for c in classes]
    fig = go.Figure(
        go.Bar(
            x=classes,
            y=values,
            marker_color=[CLASS_COLORS[c] for c in classes],
            text=[f"{v:.1%}" for v in values],
            textposition="outside",
        )
    )
    fig.update_layout(
        height=280,
        yaxis_tickformat=".0%",
        yaxis_range=[0, max(values) * 1.2 if max(values) > 0 else 1],
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Razred plače",
        yaxis_title="Verjetnost",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_similar(vec, top_k: int = 5) -> None:
    similar = find_similar(models, vec, top_k=top_k)
    st.subheader(f"Top {top_k} podobnih oglasov iz zbirke")
    for _, row in similar.iterrows():
        with st.container(border=True):
            cols = st.columns([3, 1, 1, 1])
            cols[0].markdown(
                f"**{row['title']}**  \n_{row['company']}_"
            )
            cols[1].metric("€/h neto", f"{row['hourly_rate_neto']:.2f}")
            cols[2].metric("razred", row["razred"])
            cols[3].metric("podobnost", f"{row['similarity']:.2f}")
            with st.expander("Pokaži opis"):
                st.write(
                    f"**Lokacija:** {row['normalized_city'] or '-'}, "
                    f"{row['normalized_region'] or '-'} • "
                    f"**Kategorija:** {row['category']}"
                )
                st.write(row["description"] or "*(brez opisa)*")


tab_struct, tab_text = st.tabs(
    ["Strukturirani vnos", "Prosti opis dela"]
)

with tab_struct:
    st.markdown(
        "Model: **logistična regresija na strukturiranih atributih** (vrsta dela, regija, urnik, "
        "trajanje). Točnost na testnem setu v notebooku: 44,9 %."
    )

    regions = sorted(data["normalized_region"].dropna().unique().tolist()) + ["NEZNANO"]
    schedules = ["PO DOGOVORU", "DOPOLDAN", "POPOLDAN", "IZMENSKO", "MED VIKENDI"]
    durations = ["DLJE ČASA", "PO DOGOVORU", "OSTALO"]

    c1, c2 = st.columns(2)
    with c1:
        vrsta = st.selectbox("Vrsta dela", CATEGORIES, index=CATEGORIES.index("GOSTINSTVO"))
        regija = st.selectbox(
            "Regija",
            regions,
            index=regions.index("OSREDNJESLOVENSKA") if "OSREDNJESLOVENSKA" in regions else 0,
        )
    with c2:
        urnik = st.selectbox("Urnik", schedules, index=0)
        trajanje = st.selectbox("Trajanje", durations, index=0)

    # Privzeta dolžina opisa = mediana dolžin opisov v zbirki (400 znakov)
    DEFAULT_DESC_LEN = 400

    if st.button("Napovej razred plače", type="primary", key="struct"):
        pred, probs = predict_structured(models, vrsta, regija, urnik, trajanje, DEFAULT_DESC_LEN)
        render_prediction(pred, probs)

with tab_text:
    st.markdown(
        "Model: **TF-IDF (besedni + znakovni n-grami) + logistična regresija** na celotnem "
        "besedilu (naslov + opis). Točnost na testnem setu v notebooku: 50,2 % - najboljši model."
    )

    title = st.text_input(
        "Naslov oglasa",
        value="POMOČ V TRGOVINI - POLNJENJE POLIC",
    )
    description = st.text_area(
        "Opis dela",
        value=(
            "Iščemo zanesljivega študenta za delo v naši trgovini. "
            "Naloge: polnjenje polic, urejanje skladišča, pomoč na blagajni. "
            "Plačilo po dogovoru, fleksibilni delovni čas."
        ),
        height=180,
    )

    if st.button("Napovej razred plače", type="primary", key="text"):
        if not (title.strip() or description.strip()):
            st.warning("Vnesi vsaj naslov ali opis.")
        else:
            pred, probs, vec = predict_text(models, title, description)
            render_prediction(pred, probs)

            inferred_cat = category_from_text(title, description)
            st.caption(f"Avtomatsko prepoznana kategorija iz naslova: **{inferred_cat}**")

            st.divider()
            render_similar(vec, top_k=5)
