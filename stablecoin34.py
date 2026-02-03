from stablecoin_validation import df_tokentrans
import pandas as pd
import matplotlib.pyplot as plt

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

# flight to safety
flow_by_token = (
    df
    .groupby(["hour", "token"], as_index=False)["value"]
    .sum()
    .rename(columns={"value": "volume"})
)
flow_by_token["total_volume"] = (
    flow_by_token
    .groupby("hour")["volume"]
    .transform("sum")
)

flow_by_token["share"] = (
    flow_by_token["volume"] / flow_by_token["total_volume"]
)

ZERO = "0x0000000000000000000000000000000000000000"

df["is_mint"] = df["from_address"] == ZERO
df["is_burn"] = df["to_address"] == ZERO

#“We clean the transfer data by standardizing timestamps, restricting attention to major stablecoins, and aggregating flows at the hourly level. We do not remove repeated or routed transactions, as these reflect genuine trading activity during periods of stress.”
# in the cleaned dataset:
# each row -> capital movement
# time = consistent
# tokens = comparable
# aggregation = economically meaningful


# making plots
# Make sure hour is sorted
ustc_run_volume = ustc_run_volume.sort_values("hour")

fig, ax1 = plt.subplots(figsize=(12, 5))

# Left axis: transfer volume
ax1.plot(ustc_run_volume["hour"], ustc_run_volume["transfer_volume"])
ax1.set_xlabel("Time (hourly, UTC)")
ax1.set_ylabel("USTC transfer volume")
ax1.tick_params(axis="x", rotation=45)

# Right axis: transaction count
ax2 = ax1.twinx()
ax2.plot(ustc_run_volume["hour"], ustc_run_volume["tx_count"])
ax2.set_ylabel("USTC transaction count")

plt.title("Run intensity: USTC transfer volume and transaction count over time")
plt.tight_layout()
plt.show()

# interpretation:
# spikes in tx count = "panic churn"
# spikes in volume = "large exits/ reallocations"

# Pivot to wide format: rows=hour, columns=token, values=volume
vol_wide = (
    flow_by_token
    .pivot(index="hour", columns="token", values="volume")
    .fillna(0)
    .sort_index()
)

fig, ax = plt.subplots(figsize=(12, 5))

ax.stackplot(
    vol_wide.index,
    [vol_wide[c] for c in vol_wide.columns],
    labels=vol_wide.columns
)

ax.set_title("Flight to safety: transfer volume by token over time")
ax.set_xlabel("Time (hourly, UTC)")
ax.set_ylabel("Transfer volume")
ax.tick_params(axis="x", rotation=45)
ax.legend(loc="upper left", ncol=3)

plt.tight_layout()
plt.show()




