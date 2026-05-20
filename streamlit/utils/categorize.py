CATEGORIES = [
    "POUČEVANJE / INŠTRUKCIJE",
    "PROMOCIJE",
    "ČIŠČENJE",
    "RECEPCIJA / TURIZEM",
    "ZDRAVSTVO / NEGA",
    "DELO Z OTROKI",
    "DOSTAVA / PREVOZ",
    "KLICNI CENTER",
    "TEHNIČNO / MONTAŽA",
    "MARKETING",
    "IT / RAČUNALNIŠTVO",
    "GOSTINSTVO",
    "TRGOVINA / PRODAJA",
    "ADMINISTRACIJA",
    "PROIZVODNJA / SKLADIŠČE",
    "FIZIČNO DELO",
    "OSTALO",
]


def categorize(title: str) -> str:
    # Kategorija oglasa iz velikih črk naslova (+ subtitle).
    if not isinstance(title, str):
        return "OSTALO"
    t = title.upper()
    if "POUČEVAN" in t or "INŠTRUKCIJ" in t or "TUTOR" in t:
        return "POUČEVANJE / INŠTRUKCIJE"
    if "PROMOCIJ" in t or "POSPEŠEVAN" in t or "ANKETIRAN" in t:
        return "PROMOCIJE"
    if "ČIŠČENJ" in t:
        return "ČIŠČENJE"
    if "RECEPCIJ" in t or "TURIZ" in t:
        return "RECEPCIJA / TURIZEM"
    if "ZDRAVSTV" in t or " NEGA" in t or "FIZIOTER" in t or "MEDICIN" in t or "KINEZIOLOG" in t:
        return "ZDRAVSTVO / NEGA"
    if "OTROK" in t or "OTROČ" in t or "VARSTV" in t or "ANIMATOR" in t:
        return "DELO Z OTROKI"
    if "DOSTAV" in t or "RAZVOZ" in t or "KURIR" in t or "ŠOFER" in t:
        return "DOSTAVA / PREVOZ"
    if "KLICNI" in t or "TELEFONIST" in t:
        return "KLICNI CENTER"
    if "MONTAŽ" in t or "GRADBEN" in t or "ELEKTROTEHN" in t or "MONTER" in t:
        return "TEHNIČNO / MONTAŽA"
    if "MARKETING" in t or "TRŽENJ" in t:
        return "MARKETING"
    if (
        "PROGRAMIR" in t
        or " IT " in t
        or t.startswith("IT ")
        or t.endswith(" IT")
        or "SPLETN" in t
        or "RAČUNALNIŠ" in t
    ):
        return "IT / RAČUNALNIŠTVO"
    if "STREŽB" in t or "KUHINJ" in t or "NATAKAR" in t or "POMIVANJ" in t:
        return "GOSTINSTVO"
    if (
        "TRGOVIN" in t
        or "PRODAJ" in t
        or "BLAGAJN" in t
        or "BENCINSK" in t
        or "POLNJENJ POLIC" in t
    ):
        return "TRGOVINA / PRODAJA"
    if "ADMINISTR" in t or "TAJNIK" in t:
        return "ADMINISTRACIJA"
    if "PROIZVODNJ" in t or "PAKIRAN" in t or "SKLADIŠČ" in t:
        return "PROIZVODNJA / SKLADIŠČE"
    if "FIZIČN" in t or "DVIGOVAN" in t or "NAKLAD" in t:
        return "FIZIČNO DELO"
    return "OSTALO"


def map_duration(d: str) -> str:
    if not isinstance(d, str):
        return "OSTALO"
    d = d.upper()
    if "DLJE ČASA" in d:
        return "DLJE ČASA"
    if "PO DOGOVORU" in d:
        return "PO DOGOVORU"
    return "OSTALO"
