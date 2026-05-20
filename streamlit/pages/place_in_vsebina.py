"""Plače po atributih + analiza ključnih besed v opisih."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_data

st.title("Plače in vsebina")
st.caption(
    "Primerjava plač po atributih (regija, kategorija, urnik …) in analiza ključnih besed."
)

data = load_data()
hourly = data[
    (data["normalized_payment_type"] == "HOURLY") & data["hourly_rate_neto"].notna()
].copy()
overall_median = hourly["hourly_rate_neto"].median()
overall_mean = hourly["hourly_rate_neto"].mean()

tab1, tab2 = st.tabs(["Plače po atributih", "Ključne besede"])

with tab1:
    st.subheader("Plače po izbranem atributu")

    ATTR_LABELS = {
        "normalized_region": "Regija",
        "category": "Kategorija dela",
        "work_schedule": "Delovni urnik",
        "trajanje": "Trajanje dela",
        "normalized_city": "Mesto",
        "company": "Delodajalec",
    }

    c_atr, c_min = st.columns([2, 1])
    with c_atr:
        attr = st.selectbox(
            "Skupina po atributu",
            options=list(ATTR_LABELS.keys()),
            format_func=lambda x: ATTR_LABELS[x],
            index=1,
        )
    with c_min:
        default_min = 50 if attr in {"normalized_city", "company"} else 5
        min_count = st.number_input(
            "Najmanj oglasov v skupini",
            min_value=1,
            max_value=2000,
            value=default_min,
            step=10,
            help="Skupine z manj oglasi so izpuščene, da odstranimo šum.",
        )

    df_attr = hourly.dropna(subset=[attr]).copy()
    stats = (
        df_attr.groupby(attr)["hourly_rate_neto"]
        .agg(["median", "mean", "count"])
        .rename(columns={"median": "Mediana", "mean": "Povprečje", "count": "Št. oglasov"})
    )
    stats = stats[stats["Št. oglasov"] >= min_count]
    stats = stats.sort_values("Mediana", ascending=True)

    if len(stats) == 0:
        st.warning("Pri tem pragu ni nobene skupine. Zmanjšaj minimum.")
    else:
        st.markdown(
            f"**Skupna mediana**: {overall_median:.2f} €/h • **povprečje**: {overall_mean:.2f} €/h • "
            f"**vključenih skupin**: {len(stats)}"
        )

        fig = go.Figure()
        colors = ["#B0D4FF" if v < overall_median else "#007AFF" for v in stats["Mediana"]]
        fig.add_trace(
            go.Bar(
                y=stats.index.astype(str),
                x=stats["Mediana"],
                orientation="h",
                marker_color=colors,
                name="Mediana",
                text=[f"{v:.2f} €" for v in stats["Mediana"]],
                textposition="outside",
                customdata=stats[["Povprečje", "Št. oglasov"]].values,
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Mediana: %{x:.2f} €/h<br>"
                    "Povprečje: %{customdata[0]:.2f} €/h<br>"
                    "Št. oglasov: %{customdata[1]:.0f}"
                    "<extra></extra>"
                ),
            )
        )
        fig.add_trace(
            go.Scatter(
                y=stats.index.astype(str),
                x=stats["Povprečje"],
                mode="markers",
                marker=dict(color="black", symbol="diamond", size=9),
                name="Povprečje",
                hovertemplate="Povprečje: %{x:.2f} €/h<extra></extra>",
            )
        )
        fig.add_vline(
            x=overall_median,
            line_dash="dash",
            line_color="#E03030",
            annotation_text=f"Skupna mediana {overall_median:.2f} €",
            annotation_position="top",
        )
        fig.update_layout(
            height=max(350, 30 * len(stats) + 100),
            xaxis_title="Neto urna postavka (€/h)",
            yaxis_title=ATTR_LABELS[attr],
            margin=dict(l=10, r=10, t=30, b=10),
            legend=dict(orientation="h", y=-0.15),
        )
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Numerična tabela"):
            display = stats.copy()
            display.index.name = ATTR_LABELS[attr]
            st.dataframe(
                display.style.format(
                    {"Mediana": "{:.2f} €", "Povprečje": "{:.2f} €", "Št. oglasov": "{:.0f}"}
                ).background_gradient(subset=["Mediana"], cmap="RdYlGn"),
                use_container_width=True,
            )

    st.divider()

    st.subheader("Porazdelitev plač znotraj posameznih skupin")
    n_top = st.slider(
        "Število najpogostejših skupin za prikaz",
        min_value=3,
        max_value=20,
        value=10,
    )
    top_groups = df_attr[attr].value_counts().head(n_top).index.tolist()
    box_df = df_attr[df_attr[attr].isin(top_groups)]
    fig_box = px.box(
        box_df,
        x=attr,
        y="hourly_rate_neto",
        category_orders={attr: top_groups},
        labels={"hourly_rate_neto": "Neto urna postavka (€/h)", attr: ATTR_LABELS[attr]},
        color_discrete_sequence=["#007AFF"],
    )
    fig_box.update_layout(
        height=450,
        margin=dict(l=10, r=10, t=30, b=80),
        xaxis_tickangle=-30,
    )
    st.plotly_chart(fig_box, use_container_width=True)


# ===================== TAB 2: KLJUČNE BESEDE =====================
with tab2:
    st.subheader("Ključne besede v opisu in plačilo")
    st.markdown(
        "Za vsako 'značko' primerjamo mediano plače pri oglasih, kjer se vzorec pojavi, in "
        "tistih, kjer se ne."
    )

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

    hourly_unique = hourly.drop_duplicates(subset="description").reset_index(drop=True)
    text_field = (
        hourly_unique["title"].fillna("") + " " + hourly_unique["description"].fillna("")
    ).str.lower()

    rows = []
    for label, pattern in KEYWORD_PATTERNS.items():
        mask = text_field.str.contains(pattern, regex=True, na=False)
        n = int(mask.sum())
        if n == 0:
            continue
        med_z = hourly_unique.loc[mask, "hourly_rate_neto"].median()
        med_brez = hourly_unique.loc[~mask, "hourly_rate_neto"].median()
        rows.append(
            {
                "značka": label,
                "št. oglasov": n,
                "mediana € z značko": round(med_z, 2),
                "mediana € brez": round(med_brez, 2),
                "razlika €/h": round(med_z - med_brez, 2),
            }
        )
    kw_table = pd.DataFrame(rows).sort_values("razlika €/h", ascending=True)

    fig_kw = go.Figure()
    colors = [
        "#B0D4FF" if d < 0 else ("#007AFF" if d > 0.3 else "#5AA9F2")
        for d in kw_table["razlika €/h"]
    ]
    fig_kw.add_trace(
        go.Bar(
            y=kw_table["značka"],
            x=kw_table["razlika €/h"],
            orientation="h",
            marker_color=colors,
            text=[f"{v:+.2f} €" for v in kw_table["razlika €/h"]],
            textposition="outside",
            customdata=kw_table[["mediana € z značko", "mediana € brez", "št. oglasov"]].values,
            hovertemplate=(
                "<b>%{y}</b><br>"
                "z značko: %{customdata[0]:.2f} €/h<br>"
                "brez: %{customdata[1]:.2f} €/h<br>"
                "razlika: %{x:+.2f} €/h<br>"
                "št. oglasov: %{customdata[2]:.0f}<extra></extra>"
            ),
        )
    )
    fig_kw.add_vline(x=0, line_color="black", line_width=1)
    fig_kw.update_layout(
        height=520,
        xaxis_title="Razlika v mediani plačila (€/h) – značka prisotna − odsotna",
        margin=dict(l=10, r=10, t=30, b=30),
    )
    st.plotly_chart(fig_kw, use_container_width=True)

    with st.expander("Numerična tabela vseh značk"):
        st.dataframe(
            kw_table.sort_values("razlika €/h", ascending=False).reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )

    st.divider()
    st.subheader("Preizkusi svoj regex vzorec")
    st.caption(
        "Vnesi regex (case-insensitive), aplikacija primerja mediano plače pri oglasih, kjer se "
        "vzorec pojavi v naslovu ali opisu, s tistimi, kjer se ne."
    )

    col_a, col_b = st.columns([3, 1])
    with col_a:
        user_pattern = st.text_input(
            "Regex vzorec",
            value=r"\b(?:in[šs]trukcij|tutor|pou[čc]evan)",
            help="Primer: \\bpython\\b ali \\bvozni[šs]ki",
        )
    with col_b:
        st.markdown("&nbsp;", unsafe_allow_html=True)
        st.button("Analiziraj", use_container_width=True)

    if user_pattern:
        try:
            mask = text_field.str.contains(user_pattern, regex=True, na=False, case=False)
            n = int(mask.sum())
        except re.error as e:
            st.error(f"Napaka v regex izrazu: {e}")
            n = 0
            mask = None

        if mask is not None:
            if n == 0:
                st.info("Vzorec se ne pojavi v nobenem oglasu.")
            else:
                med_z = hourly_unique.loc[mask, "hourly_rate_neto"].median()
                med_brez = hourly_unique.loc[~mask, "hourly_rate_neto"].median()
                diff = med_z - med_brez

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Št. oglasov z vzorcem", f"{n:,}".replace(",", "."))
                m2.metric("Mediana z vzorcem", f"{med_z:.2f} €/h")
                m3.metric("Mediana brez", f"{med_brez:.2f} €/h")
                m4.metric(
                    "Razlika",
                    f"{diff:+.2f} €/h",
                )

                st.markdown("**Najdražji primeri z vzorcem:**")
                examples = hourly_unique.loc[mask].nlargest(5, "hourly_rate_neto")[
                    ["title", "company", "hourly_rate_neto", "normalized_city"]
                ].rename(
                    columns={
                        "title": "Naslov",
                        "company": "Delodajalec",
                        "hourly_rate_neto": "€/h",
                        "normalized_city": "Mesto",
                    }
                )
                st.dataframe(
                    examples,
                    use_container_width=True,
                    hide_index=True,
                    column_config={"€/h": st.column_config.NumberColumn(format="%.2f €")},
                )
