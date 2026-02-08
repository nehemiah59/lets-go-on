import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

ZIP_PATH = "ERC20-stablecoins.zip"
INNER_PRICE_ZIP = "price_data.zip"   # name of the nested zip inside the main zip

TOKENS = ["USDC", "USDT", "USTC", "DAI", "PAX"]
price_dfs = {}

# --- Load from nested zip ---
with zipfile.ZipFile(ZIP_PATH) as z:
    # Read the nested zip as bytes
    with z.open(INNER_PRICE_ZIP) as inner_zip_file:
        inner_bytes = inner_zip_file.read()

    # Open nested zip from bytes (in-memory)
    with zipfile.ZipFile(io.BytesIO(inner_bytes)) as pz:
        # Find relevant price CSVs inside nested zip (be flexible about folder names)
        for name in pz.namelist():
            if name.lower().endswith("_price_data.csv"):
                token = name.split("/")[-1].replace("_price_data.csv", "").upper()

                if token in TOKENS:
                    with pz.open(name) as f:
                        df = pd.read_csv(f)

                    # Convert timestamp (support both)
                    if "timestamp" in df.columns:
                        df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
                        df["datetime"] = pd.to_datetime(df["timestamp"], unit="s", utc=True, errors="coerce")
                    elif "time_stamp" in df.columns:
                        df["time_stamp"] = pd.to_numeric(df["time_stamp"], errors="coerce")
                        df["datetime"] = pd.to_datetime(df["time_stamp"], unit="s", utc=True, errors="coerce")
                    else:
                        raise ValueError(f"No timestamp column in {name}. Columns: {df.columns.tolist()}")

                    df = df.dropna(subset=["datetime"])
                    price_dfs[token] = df

print("Loaded price tokens:", sorted(price_dfs.keys()))

# --- Plotting ---
fig, axes = plt.subplots(len(TOKENS), 1, figsize=(12, 3 * len(TOKENS)), sharex=True)
if len(TOKENS) == 1:
    axes = [axes]

for ax, token in zip(axes, TOKENS):
    if token not in price_dfs:
        ax.set_title(f"{token} (data not found)")
        ax.grid(True)
        continue

    df = price_dfs[token].sort_values("datetime")

    # Handle possible price column names
    price_col = next((c for c in ["close", "Close", "price", "Price"] if c in df.columns), None)
    if price_col is None:
        raise ValueError(f"No price column found for {token}. Columns: {df.columns.tolist()}")

    ax.plot(df["datetime"], df[price_col], label="Price")
    ax.axhline(1, color="red", linestyle="--", label="$1 Peg")
    ax.set_ylabel("Price (USD)")
    ax.set_title(token)
    ax.grid(True)
    ax.legend()

axes[-1].set_xlabel("Date (UTC)")
plt.tight_layout()
plt.show()
