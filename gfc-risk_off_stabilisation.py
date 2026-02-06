import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 10

# ============================================================================
# Data Loading
# ============================================================================

gspc = pd.read_csv('^GSPC.csv')
gspc.columns = gspc.iloc[0]
gspc = gspc.drop([0, 1]).reset_index(drop=True)
gspc.columns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']

dji = pd.read_csv('^DJI.csv')
dji.columns = dji.iloc[0]
dji = dji.drop([0, 1]).reset_index(drop=True)
dji.columns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']

vix = pd.read_csv('^VIX.csv')
vix.columns = vix.iloc[0]
vix = vix.drop([0, 1]).reset_index(drop=True)
vix.columns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']

# Financial sector stocks
aig = pd.read_csv('AIG.csv')
aig.columns = aig.iloc[0]
aig = aig.drop([0, 1]).reset_index(drop=True)
aig.columns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']

citi = pd.read_csv('C.csv')
citi.columns = citi.iloc[0]
citi = citi.drop([0, 1]).reset_index(drop=True)
citi.columns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']

jpm = pd.read_csv('JPM.csv')
jpm.columns = jpm.iloc[0]
jpm = jpm.drop([0, 1]).reset_index(drop=True)
jpm.columns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']

treasury = pd.read_csv('WGS3MO.csv')
ted_spread = pd.read_csv('TEDRATE.csv')

# ============================================================================
# Data cleaning and preprocessing
# ============================================================================

for df in [gspc, dji, vix, aig, citi, jpm]:
    df['Date'] = pd.to_datetime(df['Date'])
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    df['Volume'] = pd.to_numeric(df['Volume'], errors='coerce')
    df.sort_values('Date', inplace=True)
    df.set_index('Date', inplace=True)

treasury['observation_date'] = pd.to_datetime(treasury['observation_date'])
treasury['WGS3MO'] = pd.to_numeric(treasury['WGS3MO'], errors='coerce')
treasury.set_index('observation_date', inplace=True)

ted_spread['observation_date'] = pd.to_datetime(ted_spread['observation_date'])
ted_spread['TEDRATE'] = pd.to_numeric(ted_spread['TEDRATE'], errors='coerce')
ted_spread.set_index('observation_date', inplace=True)

start_date = '2007-01-01'
end_date = '2009-12-31'

# ============================================================================
# Visualization 1: Flight to Safety
# ============================================================================

fig, axes = plt.subplots(3, 1, figsize=(16, 12), sharex=True)
fig.suptitle('Flight to Safety During 2008 Financial Crisis:\nDecline in Risk Assets vs. Rise in Safe-Haven Indicators', 
             fontsize=16, fontweight='bold', y=0.995)

# Subplot 1
ax1 = axes[0]
ax1.plot(aig.loc[start_date:end_date].index, aig.loc[start_date:end_date]['Close'], 
         label='AIG', linewidth=2, color='#d62728')
ax1.plot(citi.loc[start_date:end_date].index, citi.loc[start_date:end_date]['Close'], 
         label='Citigroup', linewidth=2, color='#ff7f0e')
ax1.plot(jpm.loc[start_date:end_date].index, jpm.loc[start_date:end_date]['Close'], 
         label='JPMorgan Chase', linewidth=2, color='#2ca02c')

crisis_events = [
    ('2008-03-16', 'Bear Stearns\nCollapse', 0.95),
    ('2008-09-15', 'Lehman Brothers\nBankruptcy', 0.85),
    ('2008-09-16', 'AIG Bailout', 0.65),
    ('2008-10-03', 'TARP Enacted', 0.55)
]

for date_str, label, height_ratio in crisis_events:
    date = pd.to_datetime(date_str)
    ax1.axvline(x=date, color='red', linestyle='--', alpha=0.5, linewidth=1.5, ymin=0, ymax=1)
    ax1.text(date, ax1.get_ylim()[1] * height_ratio, label, 
             rotation=0, fontsize=8, ha='left', va='top',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3))

ax1.set_ylabel('Stock Price ($)', fontweight='bold')
ax1.set_title('Panel A: Financial Sector Stock Prices (Declining Risk Assets)', 
              fontsize=12, fontweight='bold', loc='left')
ax1.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
ax1.grid(True, alpha=0.3)

#Subplot 2
ax2 = axes[1]
ax2.fill_between(vix.loc[start_date:end_date].index, 
                  vix.loc[start_date:end_date]['Close'], 
                  alpha=0.4, color='#d62728', label='VIX Level')
ax2.plot(vix.loc[start_date:end_date].index, vix.loc[start_date:end_date]['Close'], 
         linewidth=2, color='#8b0000', label='VIX (Fear Index)')
ax2.axhspan(15, 25, alpha=0.2, color='green', label='Normal VIX Range (15-25)', zorder=0)
ax2.axhline(y=15, color='green', linestyle='--', linewidth=1, alpha=0.5)
ax2.axhline(y=25, color='green', linestyle='--', linewidth=1, alpha=0.5)

ax2.text(vix.loc[start_date:end_date].index[50], 20, 'Normal Range', 
         fontsize=9, ha='left', va='center', color='darkgreen', fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.5))

for date_str, label, height_ratio in crisis_events:
    date = pd.to_datetime(date_str)
    ax2.axvline(x=date, color='red', linestyle='--', alpha=0.5, linewidth=1.5, ymin=0, ymax=1)

ax2.set_ylabel('VIX Index', fontweight='bold')
ax2.set_title('Panel B: Market Volatility Index (Rising Fear)', 
              fontsize=12, fontweight='bold', loc='left')
ax2.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
ax2.grid(True, alpha=0.3)

# Subplot 3
ax3 = axes[2]

treasury_daily = treasury.loc[start_date:end_date].resample('D').interpolate()

ax3.plot(treasury_daily.index, treasury_daily['WGS3MO'], 
         linewidth=2.5, color='#1f77b4', label='3-Month Treasury Rate')
ax3.fill_between(treasury_daily.index, treasury_daily['WGS3MO'], 
                  alpha=0.3, color='#1f77b4')

for date_str, label, height_ratio in crisis_events:
    date = pd.to_datetime(date_str)
    ax3.axvline(x=date, color='red', linestyle='--', alpha=0.5, linewidth=1.5, ymin=0, ymax=1)

ax3.set_ylabel('Yield (%)', fontweight='bold')
ax3.set_xlabel('Date', fontweight='bold', fontsize=12)
ax3.set_title('Panel C: 3-Month Treasury Bill Rates (Falling - Flight to Safety)', 
              fontsize=12, fontweight='bold', loc='left')
ax3.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
ax3.grid(True, alpha=0.3)

for ax in axes:
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.show()

# ============================================================================
# Visualization 2: Policy Backstop and Stabilization
# ============================================================================

fig, axes = plt.subplots(2, 1, figsize=(16, 10), sharex=True)
fig.suptitle('Policy Interventions and Market Stabilization During 2008 Financial Crisis', 
             fontsize=16, fontweight='bold', y=0.995)

# Subplot 1
ax1 = axes[0]
ax1.plot(gspc.loc[start_date:end_date].index, gspc.loc[start_date:end_date]['Close'], 
         linewidth=2.5, color='#1f77b4', label='S&P 500 Index')
ax1.fill_between(gspc.loc[start_date:end_date].index, 
                  gspc.loc[start_date:end_date]['Close'], 
                  alpha=0.2, color='#1f77b4')

policy_interventions = [
    ('2008-03-16', 'Bear Stearns\nBailout', '#2ca02c', 0.85, 5),      
    ('2008-09-07', 'Fannie/Freddie\nConservatorship', '#2ca02c', 0.95, -5),
    ('2008-09-16', 'AIG Bailout\n$85B', '#2ca02c', 0.70, 5),         
    ('2008-10-03', 'TARP\n$700B', '#2ca02c', 0.85, -5),              
    ('2008-11-25', 'TALF\nAnnounced', '#2ca02c', 0.75, 5),          
    ('2008-12-16', 'Fed Cuts Rate\nto 0-0.25%', '#2ca02c', 0.88, -5)
]

for date_str, label, color, height_ratio, x_offset_days in policy_interventions:
    date = pd.to_datetime(date_str)
    ax1.axvline(x=date, color=color, linestyle='--', alpha=0.6, linewidth=2.5)
    label_date = date + pd.Timedelta(days=x_offset_days)
    y_pos = ax1.get_ylim()[1] * height_ratio
    h_align = 'left' if x_offset_days > 0 else 'right'
    
    ax1.text(label_date, y_pos, label, 
             rotation=0, fontsize=8, ha=h_align, va='top',
             bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgreen', alpha=0.7, edgecolor='darkgreen'))

ax1.set_ylabel('S&P 500 Index Level', fontweight='bold', fontsize=11)
ax1.set_title('Panel A: S&P 500 Performance with Major Policy Interventions', 
              fontsize=12, fontweight='bold', loc='left')
ax1.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
ax1.grid(True, alpha=0.3)

# Subplot 2
ax2 = axes[1]

volume_rolling = gspc.loc[start_date:end_date]['Volume'].rolling(window=20).mean()

ax2.bar(gspc.loc[start_date:end_date].index, 
        gspc.loc[start_date:end_date]['Volume'] / 1e9, 
        alpha=0.5, color='#ff7f0e', label='Daily Trading Volume')
ax2.plot(gspc.loc[start_date:end_date].index, 
         volume_rolling / 1e9, 
         linewidth=2.5, color='#d62728', label='20-Day Rolling Average')

for date_str, label, color, height_ratio, h_align in policy_interventions:
    date = pd.to_datetime(date_str)
    ax2.axvline(x=date, color=color, linestyle='--', alpha=0.6, linewidth=2.5)

ax2.set_ylabel('Volume (Billions of Shares)', fontweight='bold', fontsize=11)
ax2.set_xlabel('Date', fontweight='bold', fontsize=12)
ax2.set_title('Panel B: S&P 500 Trading Volume (Panic Spikes → Gradual Stabilization)', 
              fontsize=12, fontweight='bold', loc='left')
ax2.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
ax2.grid(True, alpha=0.3)

for ax in axes:
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()
plt.show()

# ============================================================================
# Correlation Heatmap of Various Banks and Safe Haven Indicators
# ============================================================================

crisis_start = '2008-01-01'
crisis_end = '2008-12-31'

treasury_daily_crisis = treasury.loc[crisis_start:crisis_end].resample('D').interpolate()
ted_daily_crisis = ted_spread.loc[crisis_start:crisis_end].resample('D').interpolate()

combined_data = pd.DataFrame({
    'S&P 500': gspc.loc[crisis_start:crisis_end]['Close'],
    'AIG': aig.loc[crisis_start:crisis_end]['Close'],
    'Citigroup': citi.loc[crisis_start:crisis_end]['Close'],
    'JPMorgan': jpm.loc[crisis_start:crisis_end]['Close'],
    'VIX': vix.loc[crisis_start:crisis_end]['Close'],
    '3M Treasury': treasury_daily_crisis['WGS3MO'],
    'TED Spread': ted_daily_crisis['TEDRATE']
})

correlation_matrix = combined_data.corr()

fig, ax = plt.subplots(figsize=(10, 8))
im = ax.imshow(correlation_matrix, cmap='RdYlGn', aspect='auto', vmin=-1, vmax=1)

ax.set_xticks(np.arange(len(correlation_matrix.columns)))
ax.set_yticks(np.arange(len(correlation_matrix.columns)))
ax.set_xticklabels(correlation_matrix.columns, rotation=45, ha='right')
ax.set_yticklabels(correlation_matrix.columns)

cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Correlation Coefficient', rotation=270, labelpad=20, fontweight='bold')

for i in range(len(correlation_matrix.columns)):
    for j in range(len(correlation_matrix.columns)):
        text = ax.text(j, i, f'{correlation_matrix.iloc[i, j]:.2f}',
                      ha="center", va="center", color="black", fontsize=9, fontweight='bold')

ax.set_title('Correlation Matrix: 2008 Crisis Year\n(Risk Assets vs. Safe Haven Indicators)', 
             fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.show()

