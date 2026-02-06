import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# List of Excel files
files = [
    "/Users/kavin/Downloads/ERC20-stablecoins/price_data/usdc_price_data.csv",
    "/Users/kavin/Downloads/ERC20-stablecoins/price_data/usdt_price_data.csv",
    "/Users/kavin/Downloads/ERC20-stablecoins/price_data/ustc_price_data.csv",
    "/Users/kavin/Downloads/ERC20-stablecoins/price_data/dai_price_data.csv",
    "/Users/kavin/Downloads/ERC20-stablecoins/price_data/pax_price_data.csv"
]

fig, axes = plt.subplots(len(files), 1, figsize=(12, 3*len(files)), sharex=True)

if len(files) == 1:
    axes = [axes]

titles = [
    "USDC",
    "USDT",
    "USTC",
    "DAI",
    "PAX"
]

for ax, file, title in zip(axes, files, titles):
    df = pd.read_csv(file)

    df["datetime"] = pd.to_datetime(df["timestamp"], unit="s", utc=True)

    ax.plot(df["datetime"], df["close"], label="Close")
    ax.axhline(1, color="red", label="$1 Peg")
    ax.set_ylabel("Closing Price (USD)")
    ax.set_title(title)
    ax.grid(True)
    ax.legend()

axes[-1].set_xlabel("Date (UTC)")

plt.tight_layout()
plt.show()
