"""
analyse.py — reproduce every figure in the briefing from the bundled dataset.

Reads data/osm_churches_near_tsip.csv (one row per church, with the
precomputed nearest-site distance) and prints the summary tables, then writes
the top-10 country chart to figures/churches_by_country_top10.png.

Run:  python analyse.py
"""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
df = pd.read_csv(ROOT / "data" / "osm_churches_near_tsip.csv", low_memory=False)

n  = len(df)
n1 = int(df["within_1km"].sum())
n5 = int(df["within_5km"].sum())

print("=" * 60)
print("CHURCHES NEAR DOCUMENTED CONTAMINATED SITES")
print("=" * 60)
print(f"Total OSM Christian churches : {n:,}")
print(f"Countries                    : {df['country'].nunique()}")
print(f"Within 5 km of a site        : {n5:,} ({100*n5/n:.1f}%)")
print(f"Within 1 km of a site        : {n1:,} ({100*n1/n:.1f}%)")

w5 = df[df.within_5km == 1]
print("\nBy denomination (within 5 km) — OSM tag only:")
print(w5["denom_class"].value_counts().to_string())
if "denom_class_final" in df.columns:
    print("\nBy denomination (within 5 km) — tag + name-inferred:")
    print(w5["denom_class_final"].value_counts().to_string())
    print("\nSpecific denominations inferred from names (within 5 km):")
    print(w5.loc[w5.denom_class == "Unspecified", "denom_guess"].dropna().value_counts().to_string())

print("\nMost common nearby pollutant (within 5 km):")
print(df.loc[df.within_5km == 1, "pollutant"].value_counts().head(6).to_string())

top5 = df.loc[df.within_5km == 1, "country"].value_counts()
top1 = df.loc[df.within_1km == 1, "country"].value_counts()
print("\nTop countries within 5 km:")
print(top5.head(12).to_string())

# --- write per-country summary table ---
summary = pd.DataFrame({"within_5km": top5, "within_1km": top1}).fillna(0).astype(int)
summary = summary.sort_values("within_5km", ascending=False)
(ROOT / "outputs").mkdir(exist_ok=True)
summary.to_csv(ROOT / "outputs" / "churches_by_country.csv")
print(f"\nWrote outputs/churches_by_country.csv ({len(summary)} countries)")

# --- chart: top 10 countries within 5 km ---
top = top5.head(10).sort_values()
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.barh(top.index, top.values, color="#C0392B")
ax.set_xlabel("Churches within 5 km of a documented contaminated site")
ax.set_title("Churches near toxic sites, top 10 countries",
             loc="left", fontsize=12, weight="bold")
for i, (c, v) in enumerate(top.items()):
    ax.text(v + 30, i, f"{v:,}", va="center", fontsize=9)
ax.spines[["top", "right"]].set_visible(False)
ax.margins(x=0.12)
plt.tight_layout()
fig_path = ROOT / "figures" / "churches_by_country_top10.png"
plt.savefig(fig_path, dpi=150)
print(f"Wrote {fig_path.relative_to(ROOT)}")
