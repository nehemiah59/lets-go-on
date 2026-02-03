import io
import pandas as pd


# Mapping from contract address to token symbol
TOKEN_MAP = {
    "0x6b175474e89094c44da98b954eedeac495271d0f": "DAI",
    "0x8e870d67f660d95d5be530380d0ec0bd388289e1": "PAX",
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": "USDC",
    "0xdac17f958d2ee523a2206206994597c13d831ec7": "USDT",
    "0xa47c8bf37f92abed4a126bda807a7b7498661acd": "USTC",
    "0xd2877702675e6ceb975b4a1dff9fb7baf4c91ea9": "WLUNA"
}

# opening token_transfers.csv
with zipfile.ZipFile("ERC20-stablecoins.zip") as z:
    with z.open("token_transfers.csv") as f:
        df_tokentrans = pd.read_csv(f)


# Convert Unix timestamp to datetime (UTC)
df_tokentrans["datetime"] = pd.to_datetime(df_tokentrans["time_stamp"], unit="s", utc=True)

# Map contract addresses to token symbols
df_tokentrans["token"] = df_tokentrans["contract_address"].str.lower().map(TOKEN_MAP)

# import df_tokentrans for 


# OPENING PRICE_DATA FOLDER
price_dfs = {}

with zipfile.ZipFile("ERC20-stablecoins.zip") as z:
    for file_path in price_files:
        token = file_path.split("/")[-1].replace("_price_data.csv", "").upper()
        with z.open(file_path) as f:
            df = pd.read_csv(f)
            df["datetime"] = pd.to_datetime(df["time_stamp"], unit="s", utc=True)
            df["token"] = token
            price_dfs[token] = df

#price_dfs["USTC"]   # USTC price DataFrame
#price_dfs["USDC"]   # USDC price DataFrame
#price_dfs["USDT"]   # USDT price DataFrame
#price_dfs["DAI"]    # DAI price DataFrame
#price_dfs["PAX"]    # PAX price DataFrame
# convert timestamp if necessary for above dfs^
