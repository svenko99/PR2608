"""Domača stran."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from utils.data_loader import format_slovenian_date, load_changes, load_data

data = load_data()
changes = load_changes()

st.title("Analiza ponudbe študentskega dela v Sloveniji")
st.markdown(
    "Interaktivni pregled lastne podatkovne zbirke z e-Študentskega servisa."
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Oglasov", f"{len(data):,}".replace(",", "."))
c2.metric("Različnih podjetij", f"{data['company'].nunique():,}".replace(",", "."))
c3.metric(
    "Obdobje zbiranja",
    f"{format_slovenian_date(data['first_seen'].min())} – {format_slovenian_date(data['last_seen'].max())}",
)
c4.metric("Sprememb na oglasih", f"{len(changes):,}".replace(",", "."))

st.divider()

st.markdown("## Glavne ugotovitve")

st.markdown(
    """
### 1. Vsebina dela poganja plačo, lokacija skoraj nič
Razpon median po regijah znaša le 0,40 €/h, po kategorijah dela pa 4 €/h – desetkrat več.

### 2. Plače gredo skoraj samo navzgor
Od 274 sprememb urne postavke je bilo 99,6 % dvigov in eno samo znižanje. Mediana dviga znaša
0,68 €/h, mediana časa do dviga pa 25 dni od objave.

### 3. Besedilo oglasa napove plačo bolje kot strukturirani atributi
Logistična regresija na celotnem besedilu doseže 50,2 % točnost (3 razredi), strukturirani
atributi 44,9 %. Trivialni baseline doseže 37,6 %.

### 4. Trg je izrazito fragmentiran
66 % podjetij ima v zbirki le en oglas. Največji delodajalec zaseda 3,7 % trga, top 10 skupaj
le 11 %. Pareto pravilo 80/20 tu odpove.

### 5. Vrh novih objav v začetku tedna
Ponedeljek (142) in torek (114) prinašata največ novih oglasov, ob vikendih in praznikih portal
praktično ne objavlja.
"""
)
