"""Dinamika trga: časovne vrste novih oglasov, dvigi plač, koncentracija podjetij."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import load_changes, load_data

st.title("Dinamika trga študentskega dela")
st.caption(
    "Časovne vrste novih oglasov, dvigi plač iz changes.csv in koncentracija delodajalcev."
)

data = load_data()
changes = load_changes()

tab1, tab2, tab3 = st.tabs(
    ["Časovna dinamika", "Dvigi plač", "Koncentracija podjetij"]
)

# ===================== TAB 1: ČASOVNA DINAMIKA =====================
with tab1:
    st.subheader("Število novih oglasov skozi čas")

    daily = data.groupby(data["first_seen"].dt.date).size()
    first_day = daily.index.min()
    daily = daily.drop(first_day)
    daily.index = pd.to_datetime(daily.index)

    fig_ts = go.Figure()
    fig_ts.add_trace(
        go.Bar(
            x=daily.index,
            y=daily.values,
            marker_color="#007AFF",
            hovertemplate="%{x|%d.%m.%Y}: %{y} novih oglasov<extra></extra>",
        )
    )
    fig_ts.update_layout(
        xaxis_title="Datum",
        yaxis_title="Število novih oglasov",
        height=380,
        margin=dict(l=10, r=10, t=30, b=10),
        title=f"Brez prvega zajema ({first_day.day}.{first_day.month}.{first_day.year})",
    )
    st.plotly_chart(fig_ts, use_container_width=True)

    st.divider()
    st.subheader("Povprečje po dnevu v tednu")

    daily_fixed = daily.copy()
    sat = pd.Timestamp(2026, 3, 14)
    fri = pd.Timestamp(2026, 3, 13)
    if sat in daily_fixed.index:
        daily_fixed[fri] = daily_fixed.get(fri, 0) + daily_fixed[sat]
        daily_fixed[sat] = 0

    full_range = pd.date_range(daily_fixed.index.min(), daily_fixed.index.max(), freq="D")
    daily_fixed = daily_fixed.reindex(full_range, fill_value=0)
    daily_fixed.index = pd.to_datetime(daily_fixed.index)

    weekday_avg = daily_fixed.groupby(daily_fixed.index.dayofweek).mean()
    day_names = ["Ponedeljek", "Torek", "Sreda", "Četrtek", "Petek", "Sobota", "Nedelja"]
    weekday_avg.index = [day_names[i] for i in weekday_avg.index]

    fig_w = go.Figure()
    fig_w.add_trace(
        go.Bar(
            x=weekday_avg.index,
            y=weekday_avg.values,
            marker_color="#007AFF",
            text=[f"{v:.1f}" for v in weekday_avg.values],
            textposition="outside",
        )
    )
    fig_w.update_layout(
        xaxis_title="Dan v tednu",
        yaxis_title="Povprečno število novih oglasov",
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_w, use_container_width=True)


# ===================== TAB 2: DVIGI PLAČ =====================
with tab2:
    st.subheader("Spremembe urne postavke")

    rate_changes = changes[changes["field"] == "hourly_rate_neto"].copy()
    rate_changes["old_value"] = pd.to_numeric(rate_changes["old_value"], errors="coerce")
    rate_changes["new_value"] = pd.to_numeric(rate_changes["new_value"], errors="coerce")
    rate_changes = rate_changes.dropna(subset=["old_value", "new_value"])
    rate_changes["diff"] = rate_changes["new_value"] - rate_changes["old_value"]
    rate_changes = rate_changes.merge(
        data[["id", "first_seen", "title", "company"]],
        left_on="listing_id",
        right_on="id",
        how="left",
    )
    rate_changes["days_after_post"] = (
        rate_changes["changed_at"] - rate_changes["first_seen"]
    ).dt.days

    raises = rate_changes[rate_changes["diff"] > 0]
    cuts = rate_changes[rate_changes["diff"] < 0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sprememb skupaj", f"{len(rate_changes)}")
    c2.metric(
        "Dvigov",
        f"{len(raises)} ({len(raises) / max(len(rate_changes), 1):.0%})",
    )
    c3.metric(
        "Znižanj",
        f"{len(cuts)} ({len(cuts) / max(len(rate_changes), 1):.0%})",
    )
    if len(raises) > 0:
        c4.metric("Mediana dviga", f"{raises['diff'].median():.2f} €/h")

    if len(rate_changes) > 0:
        col_a, col_b = st.columns(2)

        bins_size = [0, 0.25, 0.50, 1.00, 2.00, float("inf")]
        labels_size = [
            "0 – 0,25 €",
            "0,25 – 0,50 €",
            "0,50 – 1,00 €",
            "1,00 – 2,00 €",
            "2,00 € +",
        ]
        rate_changes["abs_diff"] = rate_changes["diff"].abs()
        rate_changes["interval_size"] = pd.cut(
            rate_changes["abs_diff"], bins=bins_size, labels=labels_size, right=True
        )
        raises_binned = (
            rate_changes[rate_changes["diff"] > 0]
            .groupby("interval_size", observed=False)
            .size()
        )
        cuts_binned = (
            rate_changes[rate_changes["diff"] < 0]
            .groupby("interval_size", observed=False)
            .size()
        )

        with col_a:
            fig_size = go.Figure()
            fig_size.add_trace(
                go.Bar(
                    y=labels_size,
                    x=raises_binned.values,
                    orientation="h",
                    name="Dvig",
                    marker_color="#007AFF",
                    text=raises_binned.values,
                    textposition="outside",
                )
            )
            if cuts_binned.sum() > 0:
                fig_size.add_trace(
                    go.Bar(
                        y=labels_size,
                        x=cuts_binned.values,
                        orientation="h",
                        name="Znižanje",
                        marker_color="#B0D4FF",
                        text=cuts_binned.values,
                        textposition="outside",
                    )
                )
            fig_size.update_layout(
                title="Velikost sprememb urne postavke",
                xaxis_title="Število sprememb",
                barmode="stack",
                height=380,
                margin=dict(l=10, r=10, t=40, b=10),
                yaxis=dict(autorange="reversed"),
            )
            st.plotly_chart(fig_size, use_container_width=True)

        bins_days = [-1, 1, 3, 7, 14, 21, 28, float("inf")]
        labels_days = [
            "0 – 1 dan",
            "2 – 3 dni",
            "4 – 7 dni",
            "8 – 14 dni",
            "15 – 21 dni",
            "22 – 28 dni",
            "29+ dni",
        ]
        rate_changes["interval_days"] = pd.cut(
            rate_changes["days_after_post"], bins=bins_days, labels=labels_days, right=True
        )
        days_binned = rate_changes.groupby("interval_days", observed=False).size()

        with col_b:
            fig_days = go.Figure()
            fig_days.add_trace(
                go.Bar(
                    y=labels_days,
                    x=days_binned.values,
                    orientation="h",
                    marker_color="#007AFF",
                    text=days_binned.values,
                    textposition="outside",
                )
            )
            fig_days.update_layout(
                title="Po koliko dneh pride do spremembe",
                xaxis_title="Število sprememb",
                height=380,
                margin=dict(l=10, r=10, t=40, b=10),
                yaxis=dict(autorange="reversed"),
            )
            st.plotly_chart(fig_days, use_container_width=True)

        st.divider()
        st.subheader("Top 10 največjih dvigov")
        top_raises = (
            raises.sort_values("diff", ascending=False)
            .head(10)[
                ["title", "company", "old_value", "new_value", "diff", "days_after_post"]
            ]
            .rename(
                columns={
                    "title": "Naslov",
                    "company": "Delodajalec",
                    "old_value": "Prej (€)",
                    "new_value": "Potem (€)",
                    "diff": "Dvig (€)",
                    "days_after_post": "Dni po objavi",
                }
            )
        )
        st.dataframe(
            top_raises,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Prej (€)": st.column_config.NumberColumn(format="%.2f €"),
                "Potem (€)": st.column_config.NumberColumn(format="%.2f €"),
                "Dvig (€)": st.column_config.NumberColumn(format="+%.2f €"),
                "Dni po objavi": st.column_config.NumberColumn(format="%.0f"),
            },
        )
    else:
        st.info("V podatkih ni sprememb urne postavke.")


# ===================== TAB 3: KONCENTRACIJA PODJETIJ =====================
with tab3:
    st.subheader("Pareto krivulja koncentracije")

    company_counts = data["company"].value_counts()
    sorted_counts = company_counts.sort_values(ascending=False)
    cum_share = sorted_counts.cumsum() / sorted_counts.sum() * 100

    total_companies = len(company_counts)
    total_ads = company_counts.sum()
    top_1_share = sorted_counts.iloc[0] / total_ads * 100
    top_10_share = sorted_counts.head(10).sum() / total_ads * 100
    one_ad = int((company_counts == 1).sum())
    one_ad_pct = one_ad / total_companies * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Različnih podjetij", f"{total_companies:,}".replace(",", "."))
    c2.metric("Največjega podjetja", f"{top_1_share:.1f} %")
    c3.metric("Top 10 podjetij", f"{top_10_share:.1f} %")
    c4.metric("Podjetja z 1 oglasom", f"{one_ad} ({one_ad_pct:.0f} %)")

    fig_pareto = go.Figure()
    fig_pareto.add_trace(
        go.Scatter(
            x=list(range(1, len(cum_share) + 1)),
            y=cum_share.values,
            mode="lines",
            line=dict(color="#007AFF", width=2),
            hovertemplate="Pri %{x} podjetjih je pokritih %{y:.1f} %% oglasov<extra></extra>",
        )
    )
    for level, color in [(50, "#E5F1FF"), (80, "#5AA9F2"), (90, "#007AFF")]:
        fig_pareto.add_hline(
            y=level, line_dash="dash", line_color=color, annotation_text=f"{level} %"
        )
    fig_pareto.update_layout(
        xaxis_title="Število podjetij (urejena po velikosti)",
        yaxis_title="Kumulativni delež oglasov (%)",
        height=440,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

    st.divider()
    st.subheader("Top 10 delodajalcev")
    top10 = company_counts.head(10).reset_index()
    top10.columns = ["Delodajalec", "Št. oglasov"]
    top10["Delež trga"] = top10["Št. oglasov"] / total_ads * 100

    fig_top = px.bar(
        top10.sort_values("Št. oglasov"),
        x="Št. oglasov",
        y="Delodajalec",
        orientation="h",
        text="Št. oglasov",
        color_discrete_sequence=["#007AFF"],
    )
    fig_top.update_traces(textposition="outside")
    fig_top.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    st.plotly_chart(fig_top, use_container_width=True)

    with st.expander("Tabela top 10"):
        st.dataframe(
            top10,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Delež trga": st.column_config.NumberColumn(format="%.2f %%"),
            },
        )
