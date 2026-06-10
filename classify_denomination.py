"""
classify_denomination.py — infer denomination from church NAMES where the
OpenStreetMap `denomination` tag is missing.

About 46% of churches have no OSM denomination tag (denom_class = "Unspecified").
Many of their names nonetheless signal a denomination ("... Catholic Church",
"Pentecostal", "SDA", "PCEA", etc.). This script keyword-matches names (in
several languages) and adds two columns to data/osm_churches_near_tsip.csv:

  denom_guess        specific denomination inferred from the name (untagged rows only)
  denom_class_final  best class: OSM-tag class where known, else name-inferred
                     class, else "Unspecified"

The original tag-based `denom_class` is kept unchanged for transparency. Name
inference is a heuristic: only ~15% of untagged churches have a name with a
clear denominational signal; the rest stay Unspecified. Ambiguous names
(e.g. "St Mary's Church") are deliberately NOT assigned.

Run:  python classify_denomination.py
"""
import re
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
CSV = ROOT / "data" / "osm_churches_near_tsip.csv"

# (specific denomination, broad class, regex) — checked in order, first match wins
RULES = [
    ("Catholic",            "Catholic",        r"\bcatholic|cath[oó]lic|kath?olik|katolik|\br\.?c\.?\b|gereja katolik|roman catholic"),
    ("Anglican/Episcopal",  "Anglican",        r"anglican|anglicana|episcopal|church of england|\ba\.?c\.?k\.?\b|church of the province"),
    ("Orthodox",            "Other Christian", r"orthodox|ortodox|ortodoxa|coptic|tewahedo|jacobite|syriac"),
    ("Methodist",           "Other Christian", r"methodist|metodist|metodista"),
    ("Presbyterian",        "Other Christian", r"presbyterian|presbiterian|presbiteriana|\bpcea\b|reform"),
    ("Baptist",             "Other Christian", r"baptist|bautista|batista|\bbaptis\b"),
    ("Lutheran",            "Other Christian", r"luther|luteran|luterana|luth[ée]rien|\bhkbp\b"),
    ("Adventist",           "Other Christian", r"adventist|adventista|seventh[- ]day|\bsda\b"),
    ("Church of God",       "Other Christian", r"church of god|\bcogic\b"),
    ("Assemblies of God",   "Other Christian", r"assemblies of god|assembly of god|asambleas de dios|assembleia de deus|\baog\b"),
    ("Pentecostal",         "Other Christian", r"pentecost|pentekosta|pentecost[eé]s|pantekosta|\bgbi\b|foursquare|cuadrangular"),
    ("Salvation Army",      "Other Christian", r"salvation army|ej[eé]rcito de salvaci[oó]n"),
    ("Jehovah's Witnesses", "Other Christian", r"jehovah|kingdom hall|testigos de jehov|saksi.?yehuwa"),
    ("Latter-day Saints",   "Other Christian", r"latter[- ]day|of latter|\blds\b|mormon"),
    ("Iglesia ni Cristo",   "Other Christian", r"iglesia ni (cristo|kristo)"),
    ("Apostolic",           "Other Christian", r"apostolic|apost[oó]lica|apostolik"),
    ("Evangelical",         "Other Christian", r"evangelic|evang[eé]lic|evangelis|\binjili\b"),
]
RULES = [(lab, cls, re.compile(rx, re.I)) for lab, cls, rx in RULES]

# Second pass: names with no explicit denomination word but an unambiguous
# Catholic marker — Marian/devotional titles, Catholic religious orders and
# missions, and strongly Catholic-associated saints. Applied only if no rule
# above matched, so e.g. "ACK St Teresa" stays Anglican.
CATHOLIC_MARKERS = re.compile(
    r"our lady|nuestra se|nossa senhora|notre[- ]dame|madonna|"
    r"immacul|inmaculada|imaculada|sacred heart|sagrado cora|"
    r"rosary|rosari|ros[áa]rio|mount carmel|\bcarmel|perpetual help|perpetuo socorro|"
    r"fatima|f[áa]tima|lourdes|guadalupe|assumption|asunci[óo]n|assun[cç][ãa]o|"
    r"annunciation|corpus christi|blessed sacrament|divine mercy|cristo rey|precious blood|"
    r"comboni|consolata|salesian|don bosco|marist|oblate|franciscan|dominican|"
    r"jesuit|loyola|ignatius|xavier|de la salle|spiritan|mill hill|redemptorist|"
    r"vincent de paul|padre pio|\bteresa|th[ée]r[èe]se|"
    r"bakhita|kizito|lwanga|aquinas|goretti|"
    r"parroquia|paroquia|paroisse|parroquial", re.I)


def guess(name):
    if not isinstance(name, str):
        return (None, None)
    s = " " + name.lower() + " "
    for lab, cls, rx in RULES:
        if rx.search(s):
            return (lab, cls)
    if CATHOLIC_MARKERS.search(s):
        return ("Catholic", "Catholic")
    return (None, None)


def main():
    df = pd.read_csv(CSV, low_memory=False)
    mask = df["denom_class"] == "Unspecified"
    g = df.loc[mask, "name"].apply(guess)
    df["denom_guess"] = pd.NA
    df.loc[mask, "denom_guess"] = g.apply(lambda x: x[0])
    name_cls = g.apply(lambda x: x[1])

    df["denom_class_final"] = df["denom_class"]
    sel = mask & name_cls.notna()
    df.loc[sel, "denom_class_final"] = name_cls[name_cls.notna()]

    df.to_csv(CSV, index=False)
    guessed = int(df["denom_guess"].notna().sum())
    print(f"Untagged churches: {int(mask.sum()):,} | name-inferred: {guessed:,} "
          f"({100*guessed/int(mask.sum()):.0f}%)")
    print("Wrote", CSV.relative_to(ROOT))


if __name__ == "__main__":
    main()
