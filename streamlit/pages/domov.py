import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from utils.data_loader import format_slovenian_date, load_changes, load_data

data = load_data()
changes = load_changes()


def fmt(value: float, decimals: int = 2) -> str:
    return f"{value:.{decimals}f}".replace(".", ",")


def fmt_int(value: int) -> str:
    return f"{value:,}".replace(",", ".")


hourly = data[
    (data["normalized_payment_type"] == "HOURLY") & data["hourly_rate_neto"].notna()
].copy()

region_medians = (
    hourly
    .dropna(subset=["normalized_region"])
    .groupby("normalized_region")["hourly_rate_neto"]
    .agg(["median", "count"])
)
region_medians = region_medians[region_medians["count"] >= 5]
region_spread = region_medians["median"].max() - region_medians["median"].min()

category_medians = (
    hourly
    .dropna(subset=["category"])
    .groupby("category")["hourly_rate_neto"]
    .agg(["median", "count"])
)
category_medians = category_medians[category_medians["count"] >= 5]
category_spread = category_medians["median"].max() - category_medians["median"].min()

rate_changes = changes[changes["field"] == "hourly_rate_neto"].copy()
rate_changes["old_value"] = pd.to_numeric(rate_changes["old_value"], errors="coerce")
rate_changes["new_value"] = pd.to_numeric(rate_changes["new_value"], errors="coerce")
rate_changes = rate_changes.dropna(subset=["old_value", "new_value"])
rate_changes["diff"] = rate_changes["new_value"] - rate_changes["old_value"]
raises = rate_changes[rate_changes["diff"] > 0]
n_changes = len(rate_changes)
n_raises = len(raises)
n_cuts = int((rate_changes["diff"] < 0).sum())
raise_share = n_raises / n_changes * 100 if n_changes > 0 else 0.0
median_raise = raises["diff"].median() if len(raises) > 0 else 0.0

rate_changes_merged = rate_changes.merge(
    data[["id", "first_seen"]], left_on="listing_id", right_on="id", how="left"
)
rate_changes_merged["days_after_post"] = (
    rate_changes_merged["changed_at"] - rate_changes_merged["first_seen"]
).dt.days
median_days = rate_changes_merged["days_after_post"].median()

company_counts = data["company"].value_counts()
total_companies = len(company_counts)
total_ads = int(company_counts.sum())
one_ad_pct = (company_counts == 1).sum() / total_companies * 100
top1_pct = company_counts.iloc[0] / total_ads * 100
top10_pct = company_counts.head(10).sum() / total_ads * 100

daily = data.groupby(data["first_seen"].dt.date).size()
first_day = daily.index.min()
daily = daily.drop(first_day)
daily.index = pd.to_datetime(daily.index)
sat = pd.Timestamp(2026, 3, 14)
fri = pd.Timestamp(2026, 3, 13)
if sat in daily.index:
    daily[fri] = daily.get(fri, 0) + daily[sat]
    daily[sat] = 0
full_range = pd.date_range(daily.index.min(), daily.index.max(), freq="D")
daily = daily.reindex(full_range, fill_value=0)
weekday_avg = daily.groupby(daily.index.dayofweek).mean()
mon_avg = weekday_avg.get(0, 0)
tue_avg = weekday_avg.get(1, 0)

st.title("Analiza ponudbe študentskega dela v Sloveniji")
st.markdown("Interaktivni pregled lastne podatkovne zbirke z e-Študentskega servisa.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Oglasov", fmt_int(len(data)))
c2.metric("Različnih podjetij", fmt_int(data["company"].nunique()))
c3.metric(
    "Obdobje zbiranja",
    f"{format_slovenian_date(data['first_seen'].min())} - {format_slovenian_date(data['last_seen'].max())}",
)
c4.metric("Sprememb na oglasih", fmt_int(len(changes)))

st.divider()

st.markdown("## Glavne ugotovitve")

cuts_text = (
    "eno samo znižanje"
    if n_cuts == 1
    else (f"{n_cuts} znižanj" if n_cuts != 0 else "nobenega znižanja")
)

st.markdown(
    f"""
### 1. Vsebina dela ima veliko večji vpliv na plačo kot lokacija dela
Razpon median po regijah znaša le {fmt(region_spread)} €/h, po kategorijah dela pa {fmt(category_spread, 1)} €/h - približno
{round(category_spread / region_spread) if region_spread > 0 else "—"}-krat več.

### 2. Plače gredo skoraj samo navzgor
Od {fmt_int(n_changes)} sprememb urne postavke je bilo {fmt(raise_share, 1)} % dvigov in {cuts_text}. Mediana dviga znaša
{fmt(median_raise)} €/h, mediana časa do dviga pa {int(round(median_days))} dni od objave.

### 3. Besedilo oglasa napove plačo bolje kot strukturirani atributi
Logistična regresija na celotnem besedilu doseže 50,2 % točnost (3 razredi), strukturirani
atributi 44,9 %. Trivialni baseline doseže 37,6 %.

### 4. Trg je izrazito fragmentiran
{fmt(one_ad_pct, 0)} % podjetij ima v zbirki le en oglas. Največji delodajalec zaseda {fmt(top1_pct, 1)} % trga, top 10 skupaj
{fmt(top10_pct, 0)} %.

### 5. Vrh novih objav v začetku tedna
Ponedeljek ({fmt(mon_avg, 0)}) in torek ({fmt(tue_avg, 0)}) prinašata največ novih oglasov, ob vikendih in praznikih portal
praktično ne objavlja.
"""
)
