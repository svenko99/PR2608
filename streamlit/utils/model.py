"""Trening + napoved + iskanje podobnih oglasov (Q11 Korak 2 iz notebooka)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import streamlit as st
from scipy.sparse import csr_matrix, hstack
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from utils.categorize import categorize, map_duration
from utils.data_loader import load_data, load_stopwords

CAT_COLS = ["vrsta_dela", "regija", "urnik", "trajanje"]
NUM_COLS = ["desc_len_log"]


@dataclass
class TrainedModels:
    q33: float
    q66: float
    classes: list[str]
    struct_model: Pipeline
    text_model: LogisticRegression
    word_vec: TfidfVectorizer
    char_vec: TfidfVectorizer
    text_matrix: csr_matrix  # za cosine similarity z oglasi iz zbirke
    hourly_df: pd.DataFrame  # podmnožica oglasov, na kateri je model treniran (HOURLY + znana plača)
    struct_train_examples: pd.DataFrame  # za izpis možnosti v UI selectboxih


def _to_class(x: float, q33: float, q66: float) -> str:
    if x < q33:
        return "nizka"
    if x <= q66:
        return "srednja"
    return "visoka"


def _prep_structured(df: pd.DataFrame) -> pd.DataFrame:
    vrsta = df["category"].fillna("OSTALO") if "category" in df.columns else pd.Series(
        "OSTALO", index=df.index
    )
    desc_len_log = np.log1p(df["description"].fillna("").str.len())
    return pd.DataFrame(
        {
            "vrsta_dela": vrsta,
            "regija": df["normalized_region"].fillna("NEZNANO"),
            "urnik": df["work_schedule"].fillna("PO DOGOVORU"),
            "trajanje": df["duration"].fillna("").str.upper().apply(
                lambda d: "DLJE ČASA"
                if "DLJE ČASA" in d
                else ("PO DOGOVORU" if "PO DOGOVORU" in d else "OSTALO")
            ),
            "desc_len_log": desc_len_log,
        },
        index=df.index,
    )


@st.cache_resource(show_spinner="Treniranje modela...")
def train_models() -> TrainedModels:
    df = load_data()
    hourly = df[
        (df["normalized_payment_type"] == "HOURLY") & df["hourly_rate_neto"].notna()
    ].copy()
    # Odstranimo podvojene opise (kot v notebooku) – preprečimo, da en pogost oglas prevladuje
    hourly = hourly.drop_duplicates(subset="description").reset_index(drop=True)

    q33 = float(hourly["hourly_rate_neto"].quantile(0.33))
    q66 = float(hourly["hourly_rate_neto"].quantile(0.66))
    hourly["razred"] = hourly["hourly_rate_neto"].apply(lambda x: _to_class(x, q33, q66))
    hourly["text"] = (
        hourly["title"].fillna("") + " " + hourly["description"].fillna("")
    ).str.lower()
    hourly["desc_len_log"] = np.log1p(hourly["description"].fillna("").str.len())

    # === Strukturirani model ===
    X_struct = _prep_structured(hourly)
    y = hourly["razred"]

    ct = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), CAT_COLS),
            ("num", StandardScaler(), NUM_COLS),
        ]
    )
    struct_model = Pipeline(
        [
            ("prep", ct),
            (
                "clf",
                LogisticRegression(
                    max_iter=2000, class_weight="balanced", random_state=42
                ),
            ),
        ]
    )
    struct_model.fit(X_struct, y)

    # === Tekstovni model (TF-IDF: besedni + znakovni) ===
    stop = load_stopwords()
    word_vec = TfidfVectorizer(
        stop_words=stop,
        ngram_range=(1, 2),
        min_df=20,
        sublinear_tf=True,
        max_features=8000,
    )
    char_vec = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
        min_df=20,
        sublinear_tf=True,
        max_features=8000,
    )
    X_word = word_vec.fit_transform(hourly["text"])
    X_char = char_vec.fit_transform(hourly["text"])
    X_text = hstack([X_word, X_char]).tocsr()

    text_model = LogisticRegression(
        max_iter=2000, C=1.0, class_weight="balanced", random_state=42
    )
    text_model.fit(X_text, y)

    return TrainedModels(
        q33=q33,
        q66=q66,
        classes=list(text_model.classes_),
        struct_model=struct_model,
        text_model=text_model,
        word_vec=word_vec,
        char_vec=char_vec,
        text_matrix=X_text,
        hourly_df=hourly[
            [
                "id",
                "title",
                "company",
                "normalized_city",
                "normalized_region",
                "category",
                "hourly_rate_neto",
                "description",
                "razred",
                "work_schedule",
                "duration",
            ]
        ].reset_index(drop=True),
        struct_train_examples=X_struct,
    )


def predict_structured(
    models: TrainedModels,
    vrsta_dela: str,
    regija: str,
    urnik: str,
    trajanje: str,
    desc_len: int,
) -> tuple[str, dict[str, float]]:
    """Vrne (napovedan_razred, {razred: verjetnost})."""
    X = pd.DataFrame(
        [
            {
                "vrsta_dela": vrsta_dela,
                "regija": regija,
                "urnik": urnik,
                "trajanje": trajanje,
                "desc_len_log": np.log1p(max(desc_len, 0)),
            }
        ]
    )
    proba = models.struct_model.predict_proba(X)[0]
    pred = models.struct_model.classes_[int(np.argmax(proba))]
    probs = dict(zip(models.struct_model.classes_, proba.tolist()))
    return str(pred), probs


def predict_text(
    models: TrainedModels, title: str, description: str
) -> tuple[str, dict[str, float], csr_matrix]:
    """Vrne (napovedan_razred, verjetnosti, TF-IDF vektor) za prosti opis."""
    text = ((title or "") + " " + (description or "")).lower()
    vec = hstack([models.word_vec.transform([text]), models.char_vec.transform([text])]).tocsr()
    proba = models.text_model.predict_proba(vec)[0]
    pred = models.text_model.classes_[int(np.argmax(proba))]
    probs = dict(zip(models.text_model.classes_, proba.tolist()))
    return str(pred), probs, vec


def find_similar(models: TrainedModels, vec: csr_matrix, top_k: int = 5) -> pd.DataFrame:
    """Vrne top_k najbolj podobnih oglasov (cosine similarity)."""
    sims = cosine_similarity(vec, models.text_matrix).ravel()
    top_idx = np.argsort(sims)[::-1][:top_k]
    result = models.hourly_df.iloc[top_idx].copy()
    result.insert(0, "similarity", sims[top_idx])
    return result.reset_index(drop=True)


def category_from_text(title: str, description: str = "") -> str:
    """Hitra kategorizacija prostega opisa (za UI prikaz)."""
    full = ((title or "") + " " + (description or ""))
    return categorize(full)
