import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import streamlit as st

st.set_page_config(
    page_title="Študentsko delo v Sloveniji",
    layout="wide",
)

st.markdown(
    """
    <style>
    button.st-bq { color: #007AFF !important; }

    a, a:hover, a:visited { color: #007AFF !important; }

    span[data-baseweb="tag"] {
        background-color: #007AFF !important;
        color: white !important;
    }
    span[data-baseweb="tag"] svg { fill: white !important; }

    [data-baseweb="slider"] [role="slider"],
    [data-testid="stSlider"] [role="slider"] {
        background-color: #007AFF !important;
        border-color: #007AFF !important;
    }
    [data-baseweb="slider"] div[style*="background"][style*="rgb"],
    [data-testid="stSlider"] div[style*="background"][style*="rgb"] {
        background: #007AFF !important;
    }
    [data-testid="stSliderTickBarMin"],
    [data-testid="stSliderTickBarMax"],
    [data-testid="stSliderThumbValue"] {
        color: #007AFF !important;
    }

    [data-baseweb="checkbox"] div[role="checkbox"][aria-checked="true"],
    [data-baseweb="radio"] div[role="radio"][aria-checked="true"] {
        background-color: #007AFF !important;
        border-color: #007AFF !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

domov = st.Page("pages/domov.py", title="Domov", url_path="domov", default=True)
pregled = st.Page("pages/pregled.py", title="Pregled", url_path="pregled")
place_in_vsebina = st.Page(
    "pages/place_in_vsebina.py",
    title="Plače in vsebina",
    url_path="place-in-vsebina",
)
dinamika_trga = st.Page(
    "pages/dinamika_trga.py", title="Dinamika trga", url_path="dinamika-trga"
)
napovedovalec = st.Page(
    "pages/napovedovalec.py", title="Napovedovalec plače", url_path="napovedovalec"
)

nav = st.navigation(
    [domov, pregled, place_in_vsebina, dinamika_trga, napovedovalec],
    position="top",
)
nav.run()
