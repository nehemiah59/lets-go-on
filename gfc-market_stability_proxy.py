
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1). LOAD + CLEAN 

import pandas as pd

def format_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, header=None)
    df = df.iloc[2:].reset_index(drop=True)
    df.columns = ["Date", "Close", "High", "Low", "Open", "Volume"]
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
    for col in ["Close", "High", "Low", "Open", "Volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    return df

aig = format_csv("/Users/gabrielchia/Desktop/Databusters/gfc data/AIG.csv")
c   = format_csv("/Users/gabrielchia/Desktop/Databusters/gfc data/C.csv")
jpm = format_csv("/Users/gabrielchia/Desktop/Databusters/gfc data/JPM.csv")
sp  = format_csv("/Users/gabrielchia/Desktop/Databusters/gfc data/^GSPC.csv")

# 2). crisis window zoom in

start = pd.Timestamp("2007-01-01")
end   = pd.Timestamp("2009-12-31")
aig = aig[(aig["Date"] >= start) & (aig["Date"] <= end)]
c   = c[(c["Date"]   >= start) & (c["Date"]   <= end)]
jpm = jpm[(jpm["Date"] >= start) & (jpm["Date"] <= end)]
sp  = sp[(sp["Date"]  >= start) & (sp["Date"]  <= end)]


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
def label_peak_trough(df, label, color):
    # Peak (pre-crisis)
    peak_idx = df["Close"].idxmax()
    peak_date = df.loc[peak_idx, "Date"]
    peak_price = df.loc[peak_idx, "Close"]

    # Trough (crisis low)
    trough_idx = df["Close"].idxmin()
    trough_date = df.loc[trough_idx, "Date"]
    trough_price = df.loc[trough_idx, "Close"]

    # Peak annotation
    plt.scatter(peak_date, peak_price, color=color, zorder=5)
    plt.annotate(
        f"{label} peak\n{peak_date.date()}\n{peak_price:.1f}",
        (peak_date, peak_price),
        textcoords="offset points",
        xytext=(5, 10),
        fontsize=9
    )

    # Trough annotation
    plt.scatter(trough_date, trough_price, color=color, zorder=5)
    plt.annotate(
        f"{label} trough\n{trough_date.date()}\n{trough_price:.1f}",
        (trough_date, trough_price),
        textcoords="offset points",
        xytext=(5, -15),
        fontsize=9
    )

# Label AIG and S&P 500 only
label_peak_trough(aig, "AIG", "tab:blue")
label_peak_trough(sp, "S&P 500", "tab:red")
plt.show()

#4). Phase analysis

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

