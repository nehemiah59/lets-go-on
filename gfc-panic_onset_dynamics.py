"""
2008 gfc
Panic onset (zoom-in on AIG/Citigroup around September 2008)
Run intensity proxy (trading volume spikes during stress)
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
import zipfile
import io

plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (10, 6) # (14, 8)
plt.rcParams['font.size'] = 8 # 10

# extract zip (from the starter code given)
with zipfile.ZipFile("gfc.zip") as z:
    with z.open("gfc data/AIG.csv") as f:
        aig = pd.read_csv(f, skiprows=[1, 2])
    with z.open("gfc data/C.csv") as f:
        citigroup = pd.read_csv(f, skiprows=[1, 2])
    with z.open("gfc data/JPM.csv") as f:
        jpm = pd.read_csv(f, skiprows=[1, 2])
    with z.open("gfc data/^GSPC.csv") as f:
        sp500 = pd.read_csv(f, skiprows=[1, 2])
    with z.open("gfc data/^VIX.csv") as f:
        vix = pd.read_csv(f, skiprows=[1, 2])

def prepare_data(df):
    df.rename(columns={'Price': 'Date'}, inplace=True)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    for col in ['Close', 'Open', 'High', 'Low', 'Volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

aig = prepare_data(aig)
citigroup = prepare_data(citigroup)
jpm = prepare_data(jpm)
sp500 = prepare_data(sp500)
vix = prepare_data(vix)

print(f"Data loaded: {len(aig)} rows for AIG")
print(f"Date range: {aig['Date'].min()} to {aig['Date'].max()}")

###
# Panic onset (zoom-in on AIG/Citigroup around September 2008)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12,8)) # (2,1, (14,10))

# July 2008 - December 2008
crisis_start = datetime(2008, 7, 1)
crisis_end = datetime(2008, 12, 31)

# Filter data
aig_crisis = aig[(aig['Date'] >= crisis_start) & (aig['Date'] <= crisis_end)]
citi_crisis = citigroup[(citigroup['Date'] >= crisis_start) & (citigroup['Date'] <= crisis_end)]

# Plot 1: AIG Close Price
ax1.plot(aig_crisis['Date'], aig_crisis['Close'], linewidth=2, color='#d62728', label='AIG')
ax1.set_title('Panic Onset: AIG Stock Price Collapse (July-December 2008)', 
              fontsize=14, fontweight='bold', pad=20)
ax1.set_ylabel('Close Price ($)', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)

# Mark key events
lehman_date = datetime(2008, 9, 15)  # Lehman Brothers bankruptcy
aig_bailout = datetime(2008, 9, 16)  # AIG government bailout

# Add vertical lines for key events
ax1.axvline(lehman_date, color='black', linestyle='--', linewidth=1.5, alpha=0.7, label='Lehman Bankruptcy (Sep 15)')
ax1.axvline(aig_bailout, color='purple', linestyle='--', linewidth=1.5, alpha=0.7, label='AIG Bailout (Sep 16)')

# Add annotations
peak_price = aig_crisis.loc[aig_crisis['Close'].idxmax()]
trough_price = aig_crisis.loc[aig_crisis['Close'].idxmin()]

ax1.annotate(f'Peak: ${peak_price["Close"]:.2f}',
            xy=(peak_price['Date'], peak_price['Close']),
            xytext=(10, 20), textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='black'))

ax1.annotate(f'Trough: ${trough_price["Close"]:.2f}',
            xy=(trough_price['Date'], trough_price['Close']),
            xytext=(10, -30), textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='orange', alpha=0.7),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='black'))

ax1.legend(loc='upper right', framealpha=0.9)
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax1.xaxis.set_major_locator(mdates.MonthLocator())
plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

# Plot 2: Citigroup Close Price
ax2.plot(citi_crisis['Date'], citi_crisis['Close'], linewidth=2, color='#1f77b4', label='Citigroup')
ax2.set_title('Panic Onset: Citigroup Stock Price Collapse (July-December 2008)', 
              fontsize=14, fontweight='bold', pad=20)
ax2.set_xlabel('Date', fontsize=12, fontweight='bold')
ax2.set_ylabel('Close Price ($)', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)

# Mark same key events
ax2.axvline(lehman_date, color='black', linestyle='--', linewidth=1.5, alpha=0.7, label='Lehman Bankruptcy (Sep 15)')
ax2.axvline(aig_bailout, color='purple', linestyle='--', linewidth=1.5, alpha=0.7, label='AIG Bailout (Sep 16)')

# Add annotations for Citigroup
peak_price_c = citi_crisis.loc[citi_crisis['Close'].idxmax()]
trough_price_c = citi_crisis.loc[citi_crisis['Close'].idxmin()]

ax2.annotate(f'Peak: ${peak_price_c["Close"]:.2f}',
            xy=(peak_price_c['Date'], peak_price_c['Close']),
            xytext=(10, 20), textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='black'))

ax2.annotate(f'Trough: ${trough_price_c["Close"]:.2f}',
            xy=(trough_price_c['Date'], trough_price_c['Close']),
            xytext=(10, -30), textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='orange', alpha=0.7),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='black'))

ax2.legend(loc='upper right', framealpha=0.9)
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax2.xaxis.set_major_locator(mdates.MonthLocator())
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.show()


###
# Run intensity proxy (trading volume spikes during stress)
fig, axes = plt.subplots(3, 1, figsize=(10, 8)) # (3, 1, (14,12))

# Filter for 2007-2009 period to show before, during, and after crisis
volume_start = datetime(2007, 1, 1)
volume_end = datetime(2009, 12, 31)

aig_vol = aig[(aig['Date'] >= volume_start) & (aig['Date'] <= volume_end)]
sp500_vol = sp500[(sp500['Date'] >= volume_start) & (sp500['Date'] <= volume_end)]
citi_vol = citigroup[(citigroup['Date'] >= volume_start) & (citigroup['Date'] <= volume_end)]

# Plot 1: AIG Trading Volume
ax = axes[0]
ax.bar(aig_vol['Date'], aig_vol['Volume']/1e6, width=1, color='#d62728', alpha=0.7, label='AIG Daily Volume')
ax.set_title('Run Intensity: AIG Trading Volume Spikes During 2008 Crisis', 
             fontsize=14, fontweight='bold', pad=20)
ax.set_ylabel('Volume (Millions)', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

# Mark crisis period
crisis_period_start = datetime(2008, 9, 1)
crisis_period_end = datetime(2008, 10, 31)
ax.axvspan(crisis_period_start, crisis_period_end, alpha=0.2, color='red', label='Peak Crisis Period')

# Mark key events
ax.axvline(lehman_date, color='black', linestyle='--', linewidth=2, alpha=0.8, label='Lehman Bankruptcy')

# Calculate and show mean volume
mean_vol = aig_vol['Volume'].mean()
ax.axhline(mean_vol/1e6, color='green', linestyle='-', linewidth=2, alpha=0.6, label=f'Mean Volume: {mean_vol/1e6:.1f}M')

ax.legend(loc='upper left', framealpha=0.9)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

# Plot 2: S&P 500 Trading Volume
ax = axes[1]
ax.bar(sp500_vol['Date'], sp500_vol['Volume']/1e9, width=1, color='#ff7f0e', alpha=0.7, label='S&P 500 Daily Volume')
ax.set_title('Run Intensity: S&P 500 Trading Volume Spikes During 2008 Crisis', 
             fontsize=14, fontweight='bold', pad=20)
ax.set_ylabel('Volume (Billions)', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

# Mark crisis period
ax.axvspan(crisis_period_start, crisis_period_end, alpha=0.2, color='red', label='Peak Crisis Period')
ax.axvline(lehman_date, color='black', linestyle='--', linewidth=2, alpha=0.8, label='Lehman Bankruptcy')

# Calculate and show mean volume
mean_vol_sp = sp500_vol['Volume'].mean()
ax.axhline(mean_vol_sp/1e9, color='green', linestyle='-', linewidth=2, alpha=0.6, label=f'Mean Volume: {mean_vol_sp/1e9:.2f}B')

ax.legend(loc='upper left', framealpha=0.9)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

# Plot 3: Citigroup Trading Volume
ax = axes[2]
ax.bar(citi_vol['Date'], citi_vol['Volume']/1e6, width=1, color='#1f77b4', alpha=0.7, label='Citigroup Daily Volume')
ax.set_title('Run Intensity: Citigroup Trading Volume Spikes During 2008 Crisis', 
             fontsize=14, fontweight='bold', pad=20)
ax.set_xlabel('Date', fontsize=12, fontweight='bold')
ax.set_ylabel('Volume (Millions)', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

# Mark crisis period
ax.axvspan(crisis_period_start, crisis_period_end, alpha=0.2, color='red', label='Peak Crisis Period')
ax.axvline(lehman_date, color='black', linestyle='--', linewidth=2, alpha=0.8, label='Lehman Bankruptcy')

# Calculate and show mean volume
mean_vol_c = citi_vol['Volume'].mean()
ax.axhline(mean_vol_c/1e6, color='green', linestyle='-', linewidth=2, alpha=0.6, label=f'Mean Volume: {mean_vol_c/1e6:.1f}M')

ax.legend(loc='upper left', framealpha=0.9)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.show()

###
# Combined Price Collapse (Supporting Analysis)
fig, ax = plt.subplots(figsize=(14, 8))

def normalize_price(df, start_date): # show % decline (as a scale)
    base_value = df[df['Date'] >= start_date]['Close'].iloc[0]
    df = df.copy()
    df['Normalized'] = (df['Close'] / base_value) * 100
    return df

crisis_full_start = datetime(2008, 1, 1)
crisis_full_end = datetime(2009, 6, 30)

aig_norm = normalize_price(aig[(aig['Date'] >= crisis_full_start) & (aig['Date'] <= crisis_full_end)], crisis_full_start)
citi_norm = normalize_price(citigroup[(citigroup['Date'] >= crisis_full_start) & (citigroup['Date'] <= crisis_full_end)], crisis_full_start)
jpm_norm = normalize_price(jpm[(jpm['Date'] >= crisis_full_start) & (jpm['Date'] <= crisis_full_end)], crisis_full_start)
sp500_norm = normalize_price(sp500[(sp500['Date'] >= crisis_full_start) & (sp500['Date'] <= crisis_full_end)], crisis_full_start)

ax.plot(aig_norm['Date'], aig_norm['Normalized'], linewidth=2.5, label='AIG', color='#d62728')
ax.plot(citi_norm['Date'], citi_norm['Normalized'], linewidth=2.5, label='Citigroup', color='#1f77b4')
ax.plot(jpm_norm['Date'], jpm_norm['Normalized'], linewidth=2.5, label='JPMorgan', color='#2ca02c')
ax.plot(sp500_norm['Date'], sp500_norm['Normalized'], linewidth=2.5, label='S&P 500', color='#ff7f0e', linestyle='--')

ax.axhline(100, color='black', linestyle='-', linewidth=1, alpha=0.5, label='Baseline (Jan 2008)')
ax.axvline(lehman_date, color='black', linestyle='--', linewidth=2, alpha=0.7, label='Lehman Bankruptcy')

ax.set_title('Financial Sector Collapse: Normalized Stock Prices (Jan 2008 = 100)', 
             fontsize=14, fontweight='bold', pad=20)
ax.set_xlabel('Date', fontsize=12, fontweight='bold')
ax.set_ylabel('Price Index (Jan 2008 = 100)', fontsize=12, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(loc='upper right', framealpha=0.9, fontsize=11)

ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.show()

