import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ---- Load data ----

ustc = pd.read_csv("/Users/gabrielchia/Desktop/Databusters/ERC20-stablecoins/price_data/ustc_price_data.csv")
wluna = pd.read_csv("/Users/gabrielchia/Desktop/Databusters/ERC20-stablecoins/price_data/wluna_price_data.csv")

# Convert Unix timestamps (seconds) -> datetime (UTC)
ustc["dt"] = pd.to_datetime(ustc["timestamp"], unit="s", utc=True)
wluna["dt"] = pd.to_datetime(wluna["timestamp"], unit="s", utc=True)

# Keep only what we need, drop bad rows, sort
ustc = ustc[["dt", "close"]].dropna().sort_values("dt")
wluna = wluna[["dt", "close"]].dropna().sort_values("dt")

# Rename close columns so merge is clear
ustc = ustc.rename(columns={"close": "ustc_close"})
wluna = wluna.rename(columns={"close": "wluna_close"})

# Merge on date/time
merged = pd.merge(ustc, wluna, on="dt", how="inner")


# 2) PLOT DATA (DUAL AXIS)


fig, ax1 = plt.subplots(figsize=(10, 5))

# USTC (blue)
l1, = ax1.plot(
    merged["dt"],
    merged["ustc_close"],
    label="USTC",
    color="tab:blue"
)
ax1.axhline(1.0, linestyle="--", color="gray")
ax1.set_xlabel("Date (UTC)")
ax1.set_ylabel("USTC close price (USD)", color="tab:blue")
ax1.tick_params(axis="y", labelcolor="tab:blue")

# wLUNA (orange)
ax2 = ax1.twinx()
l2, = ax2.plot(
    merged["dt"],
    merged["wluna_close"],
    label="wLUNA",
    color="tab:orange"
)
ax2.set_ylabel("wLUNA close price (USD)", color="tab:orange")
ax2.tick_params(axis="y", labelcolor="tab:orange")

# Combined legend
lines = [l1, l2]
labels = [line.get_label() for line in lines]
ax1.legend(lines, labels, loc="best")

plt.title("USTC–wLUNA Death Spiral (Price Co-movement)")
fig.tight_layout()
plt.show()

#PHASE DEFINITIONS

PHASES = [
    ("Phase 1: Apparent Stability / Hidden Fragility", "2022-04-02", "2022-05-07"),
    ("Phase 2: Peg Break / Onset of Panic",            "2022-05-07", "2022-05-09"),
    ("Phase 3: Death Spiral / System Collapse",        "2022-05-10", "2022-05-15"),
    ("Phase 4: Post-Collapse Low-Confidence Equilibrium","2022-06-01","2022-11-30"),
]

def phase_stats(df: pd.DataFrame, col: str, start: str, end: str) -> dict:
    """Compute start/end/min/max and % change for one series in a date window."""
    start_ts = pd.Timestamp(start, tz="UTC")
    end_ts   = pd.Timestamp(end, tz="UTC")

    sub = df[(df["dt"] >= start_ts) & (df["dt"] <= end_ts)][["dt", col]].dropna().sort_values("dt")

    if sub.empty:
        return {
            "start": np.nan, "end": np.nan, "min": np.nan, "max": np.nan,
            "pct_change": np.nan, "n_obs": 0
        }

    start_val = float(sub.iloc[0][col])
    end_val   = float(sub.iloc[-1][col])
    min_val   = float(sub[col].min())
    max_val   = float(sub[col].max())

    pct_change = np.nan
    if start_val != 0:
        pct_change = (end_val / start_val - 1.0) * 100.0

    return {
        "start": start_val,
        "end": end_val,
        "min": min_val,
        "max": max_val,
        "pct_change": pct_change,
        "n_obs": len(sub)
    }


# Phase Summary Table

rows = []
for phase_name, start, end in PHASES:
    ust = phase_stats(merged, "ustc_close", start, end)
    lun = phase_stats(merged, "wluna_close", start, end)

    rows.append({
        "Phase": phase_name,
        "Dates (UTC)": f"{start} to {end}",
        "USTC start": ust["start"],
        "USTC end": ust["end"],
        "USTC min": ust["min"],
        "USTC max": ust["max"],
        "USTC % change": ust["pct_change"],
        "wLUNA start": lun["start"],
        "wLUNA end": lun["end"],
        "wLUNA min": lun["min"],
        "wLUNA max": lun["max"],
        "wLUNA % change": lun["pct_change"],
        "Observations": min(ust["n_obs"], lun["n_obs"]),
    })

phase_summary = pd.DataFrame(rows)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

print("\n=== Phase Summary (computed from your data) ===")
print(phase_summary)

phase_summary.to_csv("death_spiral_phase_numbers.csv", index=False)
