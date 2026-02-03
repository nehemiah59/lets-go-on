from stablecoin_validation.py import df_tokentrans
import pandas as pd

df = df_tokentrans[
    ["datetime", "token", "value", "from_address", "to_address"]
].copy()

# enforce numeric value
df["value"] = pd.to_numeric(df["value"], errors="coerce")

# drop rows missing essentials
df = df.dropna(subset=["datetime", "token", "value"])

# for visual 3:
TOKENS_OF_INTEREST = ["USTC", "USDC", "USDT", "DAI", "PAX"]
df = df[df["token"].isin(TOKENS_OF_INTEREST)]

#time aggregation
df["hour"] = df["datetime"].dt.floor("H")  # choose hourly as it captures panic dynamics, smoothes noise, aligns well with price


#volume based intensity
ustc = df[df["token"] == "USTC"]

ustc_run_volume = (
    ustc
    .groupby("hour", as_index=False)
    .agg(
        transfer_volume=("value", "sum"),
        tx_count=("value", "count")
    )
)



