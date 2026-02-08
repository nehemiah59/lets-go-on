import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import zipfile

# 1). LOAD + CLEAN 

def format_csv(file_obj) -> pd.DataFrame:
    df = pd.read_csv(file_obj, header=None)
    df = df.iloc[2:].reset_index(drop=True)
    df.columns = ["Date", "Close", "High", "Low", "Open", "Volume"]
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    for col in ["Close", "High", "Low", "Open", "Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    return df


GFC_ZIP = "gfc.zip"

with zipfile.ZipFile(GFC_ZIP) as z:
    with z.open("gfc data/AIG.csv") as f:
        aig = format_csv(f)

    with z.open("gfc data/C.csv") as f:
        c = format_csv(f)

    with z.open("gfc data/JPM.csv") as f:
        jpm = format_csv(f)

    with z.open("gfc data/^GSPC.csv") as f:
        sp = format_csv(f)

# 2). crisis window zoom in

start = pd.Timestamp("2007-01-01")
end   = pd.Timestamp("2009-12-31")


# 3). PLOT: Market Stability Proxy


plt.figure(figsize=(10, 5))
plt.plot(aig["Date"], aig["Close"], label="AIG")
plt.plot(c["Date"],   c["Close"],   label="Citigroup (C)")
plt.plot(jpm["Date"], jpm["Close"], label="JPMorgan (JPM)")
plt.plot(sp["Date"],  sp["Close"],  label="S&P 500 (^GSPC)", linestyle="--")
plt.title("Market Stability Proxy (2008): Close Prices")
plt.xlabel("Date")
plt.ylabel("Close Price (USD)")
plt.legend()
plt.tight_layout()
plt.show()


def label_peak_trough(ax, df, xcol, ycol, series_name, fmt="{:.4f}"):
    # Peak and trough over the current df window
    peak_idx = df[ycol].idxmax()
    trough_idx = df[ycol].idxmin()

    peak_date, peak_val = df.loc[peak_idx, xcol], df.loc[peak_idx, ycol]
    trough_date, trough_val = df.loc[trough_idx, xcol], df.loc[trough_idx, ycol]

    # Markers
    ax.scatter([peak_date], [peak_val], zorder=5)
    ax.scatter([trough_date], [trough_val], zorder=5)

    # Labels
    ax.annotate(
        f"{series_name} peak\n{peak_date.date()}\n{fmt.format(peak_val)}",
        (peak_date, peak_val),
        textcoords="offset points",
        xytext=(8, 8),
        fontsize=9
    )
    ax.annotate(
        f"{series_name} trough\n{trough_date.date()}\n{fmt.format(trough_val)}",
        (trough_date, trough_val),
        textcoords="offset points",
        xytext=(8, -28),
        fontsize=9
    )

#Phase analysis

PHASES_2008 = [
    ("Phase 1: Pre-crisis / Apparent Stability", "2007-01-01", "2007-12-31"),
    ("Phase 2: Early Stress (Bear Stearns period)", "2008-01-01", "2008-06-30"),
    ("Phase 3: Panic / Acute Crisis (Lehman period)", "2008-07-01", "2009-03-09"),
    ("Phase 4: Stabilization / Recovery", "2009-03-10", "2009-12-31"),
]

def phase_stats(df: pd.DataFrame, value_col: str, start: str, end: str) -> dict:
    start_ts = pd.Timestamp(start)
    end_ts   = pd.Timestamp(end)
    sub = df[(df["Date"] >= start_ts) & (df["Date"] <= end_ts)][["Date", value_col]].dropna().sort_values("Date")

    if sub.empty:
        return {"start": np.nan, "end": np.nan, "min": np.nan, "max": np.nan, "pct_change": np.nan, "n_obs": 0}

    start_val = float(sub.iloc[0][value_col])
    end_val   = float(sub.iloc[-1][value_col])
    min_val   = float(sub[value_col].min())
    max_val   = float(sub[value_col].max())

    pct_change = np.nan
    if start_val != 0:
        pct_change = (end_val / start_val - 1.0) * 100.0

    return {"start": start_val, "end": end_val, "min": min_val, "max": max_val, "pct_change": pct_change, "n_obs": len(sub)}

series = {
    "AIG": aig,
    "C": c,
    "JPM": jpm,
    "S&P500": sp,
}

rows = []
for phase_name, start, end in PHASES_2008:
    row = {"Phase": phase_name, "Dates": f"{start} to {end}"}
    for name, df in series.items():
        st = phase_stats(df, "Close", start, end)
        row[f"{name} start"] = st["start"]
        row[f"{name} end"] = st["end"]
        row[f"{name} min"] = st["min"]
        row[f"{name} max"] = st["max"]
        row[f"{name} % change"] = st["pct_change"]
    rows.append(row)

phase_summary_2008 = pd.DataFrame(rows)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 200)

print("\n=== 2008 Phase Summary (Close price stats) ===")
print(phase_summary_2008)

phase_summary_2008.to_csv("market_stability_phase_summary_2008.csv", index=False)

def worst_drawdown(df: pd.DataFrame, col: str = "Close") -> dict:
    s = df[["Date", col]].dropna().sort_values("Date").reset_index(drop=True)
    s["peak"] = s[col].cummax()
    s["drawdown"] = (s[col] / s["peak"]) - 1.0

    trough_idx = s["drawdown"].idxmin()
    trough_date = s.loc[trough_idx, "Date"]
    trough_price = float(s.loc[trough_idx, col])
    dd = float(s.loc[trough_idx, "drawdown"]) * 100.0

    # Find the peak date immediately before the trough
    peak_price = float(s.loc[:trough_idx, "peak"].max())
    peak_idx = s.loc[:trough_idx, "peak"].idxmax()
    peak_date = s.loc[peak_idx, "Date"]

    return {
        "peak_date": peak_date,
        "peak_price": peak_price,
        "trough_date": trough_date,
        "trough_price": trough_price,
        "max_drawdown_%": dd
    }

dd_rows = []
for name, df in series.items():
    d = worst_drawdown(df, "Close")
    d["Series"] = name
    dd_rows.append(d)

drawdowns = pd.DataFrame(dd_rows)[["Series","peak_date","peak_price","trough_date","trough_price","max_drawdown_%"]]
print("\n=== Worst Drawdown (peak → trough) ===")
print(drawdowns)

drawdowns.to_csv("market_stability_drawdowns_2008.csv", index=False)

# ============================================================
# EXTRA ANALYSIS (added at bottom; original visuals + CSVs above unchanged)
# ============================================================

# 5) RETURNS + ROLLING VOLATILITY (confidence instability proxy)
# Use percentage returns; 30-day rolling vol is a common choice for daily data.
for name, df in series.items():
    df["ret"] = df["Close"].pct_change()
    df["vol_30d"] = df["ret"].rolling(30).std()

# Plot rolling volatility (banks vs market)
plt.figure(figsize=(11, 5))
plt.plot(aig["Date"], aig["vol_30d"], label="AIG vol (30d)")
plt.plot(c["Date"],   c["vol_30d"],   label="C vol (30d)")
plt.plot(jpm["Date"], jpm["vol_30d"], label="JPM vol (30d)")
plt.plot(sp["Date"],  sp["vol_30d"],  label="S&P 500 vol (30d)", linestyle="--")
plt.title("Market Stress Proxy: Rolling Volatility of Returns (30-day)")
plt.xlabel("Date")
plt.ylabel("Rolling volatility (std of daily returns)")
plt.legend()
plt.tight_layout()
plt.show()

# Save volatility diagnostics
vol_table = pd.DataFrame({
    "Date": sp["Date"],
    "AIG_vol_30d": aig["vol_30d"].values if len(aig) == len(sp) else np.nan,
})
# Safer: export each series separately to avoid length mismatch
aig[["Date","ret","vol_30d"]].to_csv("aig_returns_vol_30d.csv", index=False)
c[["Date","ret","vol_30d"]].to_csv("c_returns_vol_30d.csv", index=False)
jpm[["Date","ret","vol_30d"]].to_csv("jpm_returns_vol_30d.csv", index=False)
sp[["Date","ret","vol_30d"]].to_csv("sp_returns_vol_30d.csv", index=False)

# 6) INDEXED PRICES (start = 100) for relative performance / flight-to-quality visual
for name, df in series.items():
    if len(df) > 0:
        df["indexed_100"] = (df["Close"] / df["Close"].iloc[0]) * 100.0
    else:
        df["indexed_100"] = np.nan

plt.figure(figsize=(10, 5))
plt.plot(aig["Date"], aig["indexed_100"], label="AIG (Indexed)")
plt.plot(c["Date"],   c["indexed_100"],   label="C (Indexed)")
plt.plot(jpm["Date"], jpm["indexed_100"], label="JPM (Indexed)")
plt.plot(sp["Date"],  sp["indexed_100"],  label="S&P 500 (Indexed)", linestyle="--")
plt.title("Relative Performance (Start=100): Banks vs S&P 500 (2007–2009)")
plt.xlabel("Date")
plt.ylabel("Indexed price (Start = 100)")
plt.legend()
plt.tight_layout()
plt.show()

# Export indexed prices for write-up use
aig[["Date","Close","indexed_100"]].to_csv("aig_indexed_prices.csv", index=False)
c[["Date","Close","indexed_100"]].to_csv("c_indexed_prices.csv", index=False)
jpm[["Date","Close","indexed_100"]].to_csv("jpm_indexed_prices.csv", index=False)
sp[["Date","Close","indexed_100"]].to_csv("sp_indexed_prices.csv", index=False)

# 7) ROLLING CORRELATION (panic synchronization / contagion proxy)
# Rolling correlation of bank returns with S&P returns
WINDOW_CORR = 30

def rolling_corr_with_sp(bank_df: pd.DataFrame, sp_df: pd.DataFrame, window: int = 30) -> pd.DataFrame:
    merged_rs = pd.merge(
        bank_df[["Date", "ret"]].dropna(),
        sp_df[["Date", "ret"]].dropna(),
        on="Date",
        how="inner",
        suffixes=("_bank", "_sp")
    ).sort_values("Date")

    merged_rs["roll_corr"] = merged_rs["ret_bank"].rolling(window).corr(merged_rs["ret_sp"])
    return merged_rs

rc_aig = rolling_corr_with_sp(aig, sp, WINDOW_CORR)
rc_c   = rolling_corr_with_sp(c, sp, WINDOW_CORR)
rc_jpm = rolling_corr_with_sp(jpm, sp, WINDOW_CORR)

plt.figure(figsize=(11, 5))
plt.plot(rc_aig["Date"], rc_aig["roll_corr"], label=f"AIG vs S&P (roll corr {WINDOW_CORR}d)")
plt.plot(rc_c["Date"],   rc_c["roll_corr"],   label=f"C vs S&P (roll corr {WINDOW_CORR}d)")
plt.plot(rc_jpm["Date"], rc_jpm["roll_corr"], label=f"JPM vs S&P (roll corr {WINDOW_CORR}d)")
plt.axhline(0.0, linestyle="--")
plt.title("Panic Synchronization: Rolling Correlation of Returns with S&P 500")
plt.xlabel("Date")
plt.ylabel("Rolling correlation")
plt.legend()
plt.tight_layout()
plt.show()

rc_aig.to_csv("aig_sp_rolling_corr.csv", index=False)
rc_c.to_csv("c_sp_rolling_corr.csv", index=False)
rc_jpm.to_csv("jpm_sp_rolling_corr.csv", index=False)

# 8) LEAD–LAG CORRELATION (who moves first? propagation direction)
def lead_lag_corr(x: pd.Series, y: pd.Series, max_lag: int = 20) -> pd.DataFrame:
    lags = range(-max_lag, max_lag + 1)
    corrs = []
    for lag in lags:
        corrs.append(x.corr(y.shift(lag)))
    return pd.DataFrame({"lag": list(lags), "corr": corrs})

# Align returns by date (inner join), then compute lead-lag vs S&P
def aligned_returns(bank_df: pd.DataFrame, sp_df: pd.DataFrame) -> pd.DataFrame:
    m = pd.merge(
        bank_df[["Date", "ret"]].dropna(),
        sp_df[["Date", "ret"]].dropna(),
        on="Date",
        how="inner",
        suffixes=("_bank", "_sp")
    ).sort_values("Date")
    return m

m_aig = aligned_returns(aig, sp)
m_c   = aligned_returns(c, sp)
m_jpm = aligned_returns(jpm, sp)

ll_aig = lead_lag_corr(m_aig["ret_bank"], m_aig["ret_sp"], max_lag=20)
ll_c   = lead_lag_corr(m_c["ret_bank"],   m_c["ret_sp"],   max_lag=20)
ll_jpm = lead_lag_corr(m_jpm["ret_bank"], m_jpm["ret_sp"], max_lag=20)

# Save lead-lag tables
ll_aig.to_csv("lead_lag_aig_vs_sp.csv", index=False)
ll_c.to_csv("lead_lag_c_vs_sp.csv", index=False)
ll_jpm.to_csv("lead_lag_jpm_vs_sp.csv", index=False)

# Plot lead-lag correlations
fig, axes = plt.subplots(3, 1, figsize=(10, 9), sharex=True)
axes[0].plot(ll_aig["lag"], ll_aig["corr"], marker="o")
axes[0].axhline(0.0, linestyle="--")
axes[0].set_title("Lead–Lag Correlation: AIG returns vs S&P returns")
axes[0].set_ylabel("Correlation")

axes[1].plot(ll_c["lag"], ll_c["corr"], marker="o")
axes[1].axhline(0.0, linestyle="--")
axes[1].set_title("Lead–Lag Correlation: C returns vs S&P returns")
axes[1].set_ylabel("Correlation")

axes[2].plot(ll_jpm["lag"], ll_jpm["corr"], marker="o")
axes[2].axhline(0.0, linestyle="--")
axes[2].set_title("Lead–Lag Correlation: JPM returns vs S&P returns")
axes[2].set_xlabel("Lag (positive = bank leads S&P)")
axes[2].set_ylabel("Correlation")

fig.tight_layout()
plt.show()

# 9) DRAW DOWN TIMING COMPARISON (order of troughs = propagation narrative)
drawdowns_sorted = drawdowns.sort_values("trough_date").reset_index(drop=True)
print("\n=== Drawdowns sorted by trough_date (who bottomed first?) ===")
print(drawdowns_sorted)
drawdowns_sorted.to_csv("market_stability_drawdowns_sorted_by_trough_date.csv", index=False)
