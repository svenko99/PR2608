from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import streamlit as st
from utils.categorize import categorize, map_duration

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
STREAMLIT_DIR = Path(__file__).resolve().parent.parent

PAYMENT_LABELS = {
    "HOURLY": "Urna postavka",
    "NEGOTIABLE": "Po dogovoru",
    "PROJECT": "Projektno plačilo",
    "PER_EVENT": "Na dogodek",
    "PER_TRIP": "Na izlet",
    "OTHER": "Drugo",
}

SCHEDULE_LABELS = {
    "PO DOGOVORU": "Po dogovoru",
    "DOPOLDAN": "Dopoldan",
    "POPOLDAN": "Popoldan",
    "IZMENSKO": "Izmensko",
    "MED VIKENDI": "Med vikendi",
}

def format_slovenian_date(d) -> str:
    return f"{d.day}.{d.month}.{d.year}"


@st.cache_data(show_spinner="Nalagam oglase…")
def load_data() -> pd.DataFrame:
    df = pd.read_csv(
        DATA_DIR / "data.csv",
        parse_dates=["first_seen", "last_seen", "start_date"],
    )
    titles = (df["title"].fillna("") + " " + df["subtitle"].fillna("")).str.upper()
    df["category"] = titles.map(categorize)
    df["trajanje"] = df["duration"].fillna("").map(map_duration)
    df["payment_label"] = df["normalized_payment_type"].map(PAYMENT_LABELS)
    df["schedule_label"] = df["work_schedule"].map(SCHEDULE_LABELS)
    return df


@st.cache_data(show_spinner="Nalagam spremembe…")
def load_changes() -> pd.DataFrame:
    return pd.read_csv(
        DATA_DIR / "changes.csv",
        parse_dates=["changed_at"],
    )


@st.cache_data
def load_geojson() -> dict:
    with open(DATA_DIR / "slovenia_regions.geojson", "r") as f:
        return json.load(f)


@st.cache_data
def load_stopwords() -> list[str]:
    raw = json.loads((STREAMLIT_DIR / "stopwords-sl.json").read_text())
    return sorted({w.rstrip(".") for w in raw})


def normalize_region_name(region: str) -> str:
    if not isinstance(region, str):
        return region
    titled = region.title()
    import re

    return re.sub(r"-([A-ZŠŽČ])", lambda m: "-" + m.group(1).lower(), titled)
