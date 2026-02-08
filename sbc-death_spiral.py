import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import zipfile

# ---- Load data ----
ZIP_PATH = "ERC20-stablecoins.zip"
INNER_PRICE_ZIP = "price_data.zip"

def load_price_csv(token_name):
    """
    Load <token>_price_data.csv from the nested price_data.zip
    regardless of folder structure.
    """
    target = f"{token_name.lower()}_price_data.csv"

    with zipfile.ZipFile(ZIP_PATH) as z:
        with z.open(INNER_PRICE_ZIP) as inner_zip:
            with zipfile.ZipFile(io.BytesIO(inner_zip.read())) as pz:
                for name in pz.namelist():
                    if name.lower().endswith(target):
                        with pz.open(name) as f:
                            return pd.read_csv(f)

    raise FileNotFoundError(f"{target} not found inside {INNER_PRICE_ZIP}")

ustc = load_price_csv("ustc")
wluna = load_price_csv("wluna")

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

# ============================================================
# EXTRA ANALYSIS + NEW VISUALS (drop-in replacement)
# ============================================================

# --- 0) Regularize timeline to avoid gaps/jumps in plots ---
# (Your inner-merge + missing timestamps can create discontinuities.)
merged = merged.sort_values("dt").drop_duplicates("dt").set_index("dt")

dt_seconds = merged.index.to_series().diff().dropna().dt.total_seconds()
median_step = float(dt_seconds.median()) if not dt_seconds.empty else 86400.0

# Heuristic: hourly-ish if median step <= 3 hours, else daily-ish
freq = "H" if median_step <= 3 * 3600 else "D"

# Resample to a regular grid, then fill small gaps by time interpolation
merged = merged.resample(freq).last()

merged[["ustc_close", "wluna_close"]] = (
    merged[["ustc_close", "wluna_close"]]
    .interpolate(method="time", limit=24)  # only fill up to 24 periods
    .ffill()
    .bfill()
)

merged = merged.reset_index()
print(f"[Info] Regularized grid to freq='{freq}' (median step ~ {median_step/3600:.2f} hours).")

# --- Helper: shade phases (label only on bottom subplot; no obstruction) ---
def add_phase_shading(ax, phases, alpha=0.08, label_phases=False):
    """
    Shade phase windows. If label_phases=True, label as P1/P2/... ABOVE axis using
    axes coordinates (won't collide with the plotted data).
    """
    for i, (name, start, end) in enumerate(phases, start=1):
        s = pd.Timestamp(start, tz="UTC")
        e = pd.Timestamp(end, tz="UTC")

        ax.axvspan(s, e, alpha=alpha)
        ax.axvline(s, linestyle=":", alpha=0.25)
        ax.axvline(e, linestyle=":", alpha=0.25)

        if label_phases:
            mid = s + (e - s) / 2
            ax.text(
                mid, 1.02, f"P{i}",
                transform=ax.get_xaxis_transform(),  # x=data, y=axes
                ha="center", va="bottom",
                fontsize=10, alpha=0.75,
                clip_on=False
            )

# --- 1) Returns (log returns with epsilon to avoid log(0)) ---
EPS = 1e-12
merged = merged.sort_values("dt").reset_index(drop=True)

merged["ustc_logret"]  = np.log(np.clip(merged["ustc_close"],  EPS, None)).diff()
merged["wluna_logret"] = np.log(np.clip(merged["wluna_close"], EPS, None)).diff()

# --- 2) Peg deviation metrics ---
merged["peg_deviation"] = merged["ustc_close"] - 1.0
merged["abs_peg_deviation"] = merged["peg_deviation"].abs()

# --- 3) Formal peg-break timestamps ---
PEG_THRESHOLD = 0.98
N_CONSEC = 12  # if DAILY data, use 2–3; if HOURLY data, 12+ is fine

below = (merged["ustc_close"] < PEG_THRESHOLD).astype(int)
streak = below.groupby((below != below.shift()).cumsum()).cumcount() + 1
merged["below_streak"] = np.where(below == 1, streak, 0)

peg_break_first = merged.loc[merged["ustc_close"] < PEG_THRESHOLD, "dt"]
peg_break_first_ts = peg_break_first.iloc[0] if len(peg_break_first) else pd.NaT

peg_break_sustained = merged.loc[merged["below_streak"] >= N_CONSEC, "dt"]
peg_break_sustained_ts = peg_break_sustained.iloc[0] if len(peg_break_sustained) else pd.NaT

print("\n=== Peg break timestamps (from your data) ===")
print(f"First dip below {PEG_THRESHOLD:.2f}: {peg_break_first_ts}")
print(f"First sustained dip below {PEG_THRESHOLD:.2f} for {N_CONSEC} consecutive obs: {peg_break_sustained_ts}")

# --- 4) Rolling volatility + rolling correlation ---
WINDOW = 48  # hourly: 48 ~ 2 days; daily: use 7 or 14

merged["ustc_vol"] = merged["ustc_logret"].rolling(WINDOW).std()
merged["wluna_vol"] = merged["wluna_logret"].rolling(WINDOW).std()

merged["rolling_corr"] = (
    merged["ustc_logret"]
    .rolling(WINDOW)
    .corr(merged["wluna_logret"])
)

# --- 5) Lead–lag correlation (who leads who?) ---
L = 10
lags = range(-L, L + 1)
lag_corrs = []
for lag in lags:
    lag_corrs.append(merged["ustc_logret"].corr(merged["wluna_logret"].shift(lag)))
lag_corrs = pd.DataFrame({"lag": list(lags), "corr": lag_corrs})

best_idx = lag_corrs["corr"].abs().idxmax()
best_lag = int(lag_corrs.loc[best_idx, "lag"])
best_corr = float(lag_corrs.loc[best_idx, "corr"])

print("\n=== Lead–lag correlation (log returns) ===")
print(lag_corrs)
print(f"\nMax |corr| at lag={best_lag}, corr={best_corr:.4f}")
print("Interpretation: if best_lag > 0, wLUNA tends to move first; if best_lag < 0, USTC tends to move first.")

lag_corrs.to_csv("death_spiral_lead_lag_corrs.csv", index=False)

# --- 6) NEW VISUAL: Peg deviation + rolling vol + rolling corr ---
fig2, axes = plt.subplots(3, 1, figsize=(14, 9), sharex=True)

# (A) Peg deviation
axA = axes[0]
axA.plot(merged["dt"], merged["peg_deviation"])
axA.axhline(0.0, linestyle="--")
axA.axhline(-0.02, linestyle="--", alpha=0.6)
axA.set_ylabel("USTC deviation from $1")
axA.set_title("USTC Peg Stress + Market Panic Diagnostics", pad=12)

# Peg-break event lines + legend (no text collisions)
event_handles = []
event_labels = []

if pd.notna(peg_break_first_ts):
    h1 = axA.axvline(peg_break_first_ts, linestyle="--", alpha=0.8)
    event_handles.append(h1)
    event_labels.append(f"First < {PEG_THRESHOLD:.2f}")

if pd.notna(peg_break_sustained_ts):
    h2 = axA.axvline(peg_break_sustained_ts, linestyle="--", alpha=0.8)
    event_handles.append(h2)
    event_labels.append(f"Sustained < {PEG_THRESHOLD:.2f} for {N_CONSEC} obs")

if event_handles:
    axA.legend(
        event_handles, event_labels,
        loc="upper right",
        frameon=True,
        fontsize=9,
        title="Peg-break events",
        title_fontsize=9
    )

add_phase_shading(axA, PHASES, label_phases=False)

# (B) Rolling vol
axB = axes[1]
axB.plot(merged["dt"], merged["ustc_vol"], label=f"USTC rolling vol (win={WINDOW})")
axB.plot(merged["dt"], merged["wluna_vol"], label=f"wLUNA rolling vol (win={WINDOW})")
axB.set_ylabel("Rolling vol (std log returns)")
axB.legend(loc="upper right")
add_phase_shading(axB, PHASES, label_phases=False)

# (C) Rolling correlation
axC = axes[2]
axC.plot(merged["dt"], merged["rolling_corr"], label=f"Rolling corr (win={WINDOW})")
axC.axhline(0.0, linestyle="--")
axC.set_ylabel("Rolling correlation")
axC.set_xlabel("Date (UTC)")
axC.legend(loc="upper right")
add_phase_shading(axC, PHASES, label_phases=True)  # phase labels only here

fig2.tight_layout(rect=[0, 0, 1, 0.98])
fig2.subplots_adjust(hspace=0.15)
plt.show()

# --- 7) Lead–lag correlation plot ---
fig3, ax = plt.subplots(figsize=(10, 4))
ax.plot(lag_corrs["lag"], lag_corrs["corr"], marker="o")
ax.axhline(0.0, linestyle="--")
ax.axvline(best_lag, linestyle="--")
ax.set_xlabel("Lag (positive = wLUNA leads USTC)")
ax.set_ylabel("Correlation of log returns")
ax.set_title("Lead–Lag Correlation: Who Moves First?")
fig3.tight_layout()
plt.show()

# --- 8) Phase diagnostics table ---
phase_diag_rows = []
for phase_name, start, end in PHASES:
    start_ts = pd.Timestamp(start, tz="UTC")
    end_ts   = pd.Timestamp(end, tz="UTC")
    sub = merged[(merged["dt"] >= start_ts) & (merged["dt"] <= end_ts)].copy()

    ust_vol_mean = float(sub["ustc_vol"].mean()) if sub["ustc_vol"].notna().any() else np.nan
    lun_vol_mean = float(sub["wluna_vol"].mean()) if sub["wluna_vol"].notna().any() else np.nan
    corr_mean    = float(sub["rolling_corr"].mean()) if sub["rolling_corr"].notna().any() else np.nan

    peg_abs_mean = float(sub["abs_peg_deviation"].mean()) if sub["abs_peg_deviation"].notna().any() else np.nan
    peg_abs_max  = float(sub["abs_peg_deviation"].max()) if sub["abs_peg_deviation"].notna().any() else np.nan

    phase_diag_rows.append({
        "Phase": phase_name,
        "Dates (UTC)": f"{start} to {end}",
        "Mean |peg deviation|": peg_abs_mean,
        "Max |peg deviation|": peg_abs_max,
        f"Mean USTC rolling vol (win={WINDOW})": ust_vol_mean,
        f"Mean wLUNA rolling vol (win={WINDOW})": lun_vol_mean,
        f"Mean rolling corr (win={WINDOW})": corr_mean,
        "Observations": len(sub),
    })

phase_diagnostics = pd.DataFrame(phase_diag_rows)
print("\n=== Phase Diagnostics (peg stress + volatility + correlation) ===")
print(phase_diagnostics)

phase_diagnostics.to_csv("death_spiral_phase_diagnostics.csv", index=False)
