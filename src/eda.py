"""
Exploratory Data Analysis (EDA) Module
Generates all visual insights and empirical financial statistics matching PDF Pages 6-7.
Produces publication-quality charts saved to figures/.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

FIGURES_DIR = "figures"
TRAIN_PATH = os.path.join("data", "processed", "train.parquet")
ALL_DATA_PATH = os.path.join("data", "synthetic", "reconciliation_items.parquet")

def set_style():
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    plt.rcParams.update({
        'font.sans-serif': 'DejaVu Sans',
        'font.family': 'sans-serif',
        'figure.titlesize': 14,
        'axes.titlesize': 12,
        'axes.labelsize': 10,
        'xtick.labelsize': 9,
        'ytick.labelsize': 9,
        'figure.dpi': 300
    })

def plot_class_balance_and_differences(df: pd.DataFrame):
    """
    Recreates PDF Page 7 top charts:
    1. Class balance (items, log scale)
    2. log10(abs difference $) by break type box plot
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # 1. Class balance
    counts = df['break_type'].value_counts()
    order = ['none', 'mapping_error', 'timing', 'rounding_fx', 'missing_feed', 'duplicate']
    counts = counts.reindex([c for c in order if c in counts.index])
    
    colors = ['#4A7C59', '#3D5A80', '#508991', '#98C1D9', '#EE6C4D', '#293241']
    bars = ax1.bar(counts.index, counts.values, color=colors[:len(counts)], edgecolor='black', alpha=0.85)
    ax1.set_yscale('log')
    ax1.set_ylabel('Number of Items (log scale)', fontweight='bold')
    ax1.set_title('Class Balance: Reconciliation Outcomes (N=30,000)', fontweight='bold', pad=12)
    ax1.set_xticklabels(counts.index, rotation=30, ha='right')
    
    # Add count labels on top
    for bar in bars:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval * 1.15, f"{int(yval):,}", ha='center', va='bottom', fontsize=8)
    
    # 2. log10(abs difference $) by type
    df_diff = df.copy()
    # Floor difference at $0.01 for log transformation of rounding
    df_diff['log10_abs_diff'] = np.log10(np.maximum(df_diff['abs_diff'], 0.01))
    
    sns.boxplot(
        data=df_diff,
        x='break_type',
        y='log10_abs_diff',
        order=order,
        palette='Blues_d',
        ax=ax2,
        boxprops=dict(alpha=0.85),
        showfliers=False
    )
    ax2.set_ylabel('log10(Absolute Difference $)', fontweight='bold')
    ax2.set_xlabel('Reconciliation Outcome', fontweight='bold')
    ax2.set_title('Discrepancy Magnitude by Root Cause ($ USD)', fontweight='bold', pad=12)
    ax2.set_xticklabels(order, rotation=30, ha='right')
    
    # Add dollar guidance lines
    ax2.axhline(0, color='gray', linestyle='--', linewidth=0.8, alpha=0.7) # $1
    ax2.text(5.2, 0.1, '$1 threshold', color='gray', fontsize=8)
    ax2.axhline(2, color='orange', linestyle='--', linewidth=0.8, alpha=0.7) # $100
    ax2.text(5.2, 2.1, '$100 threshold', color='orange', fontsize=8)
    
    plt.tight_layout()
    out_file = os.path.join(FIGURES_DIR, "class_balance_and_differences.png")
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_file}")

def plot_break_rates_by_drivers(df: pd.DataFrame):
    """
    Plots break rate across core operational drivers:
    - Manual vs Automated
    - Mapping Staleness Bins
    - Entity and Account Category
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. Manual vs Automated
    man_df = df.groupby('is_manual_entry')['is_break'].agg(['mean', 'count']).reset_index()
    man_df['label'] = man_df['is_manual_entry'].map({0: 'Automated Feed\n(Straight-Through)', 1: 'Manual Journal\nEntry'})
    axes[0, 0].bar(man_df['label'], man_df['mean'] * 100, color=['#2b5c8f', '#d95f02'], edgecolor='black', alpha=0.85, width=0.5)
    axes[0, 0].set_ylabel('Break Rate (%)', fontweight='bold')
    axes[0, 0].set_title('Break Risk: Manual vs. Automated Booking', fontweight='bold')
    for idx, row in man_df.iterrows():
        axes[0, 0].text(idx, row['mean']*100 + 0.3, f"{row['mean']*100:.2f}%\n(N={row['count']:,})", ha='center', fontsize=9)
    axes[0, 0].set_ylim(0, max(man_df['mean']*100)*1.3)
    
    # 2. Mapping Staleness Bins
    bins = [0, 30, 60, 90, 180, 500]
    labels = ['<30d (Fresh)', '30-60d', '60-90d', '90-180d (Stale)', '>180d (Very Stale)']
    df['map_bin'] = pd.cut(df['mapping_version_age_days'], bins=bins, labels=labels)
    map_df = df.groupby('map_bin', observed=False)['is_break'].agg(['mean', 'count']).reset_index()
    
    axes[0, 1].plot(map_df['map_bin'], map_df['mean'] * 100, marker='o', linewidth=2.5, color='#c93b27')
    axes[0, 1].fill_between(range(len(map_df)), map_df['mean'] * 100, color='#c93b27', alpha=0.15)
    axes[0, 1].set_ylabel('Break Rate (%)', fontweight='bold')
    axes[0, 1].set_title('Mapping Staleness vs. Break Incidence', fontweight='bold')
    axes[0, 1].set_xticklabels(labels, rotation=25, ha='right')
    for idx, row in map_df.iterrows():
        axes[0, 1].text(idx, row['mean']*100 + 0.4, f"{row['mean']*100:.2f}%", ha='center', fontsize=8, fontweight='bold')
    axes[0, 1].set_ylim(0, max(map_df['mean']*100)*1.3)
    
    # 3. Entity Breakdown
    ent_df = df.groupby('entity')['is_break'].agg(['mean', 'count']).sort_values('mean', ascending=False).reset_index()
    axes[1, 0].barh(ent_df['entity'], ent_df['mean'] * 100, color='#3182bd', edgecolor='black', alpha=0.85)
    axes[1, 0].set_xlabel('Break Rate (%)', fontweight='bold')
    axes[1, 0].set_title('Break Rate Across Legal Entities', fontweight='bold')
    for idx, row in ent_df.iterrows():
        axes[1, 0].text(row['mean']*100 + 0.2, idx, f"{row['mean']*100:.2f}%", va='center', fontsize=9)
    axes[1, 0].set_xlim(0, max(ent_df['mean']*100)*1.25)
    
    # 4. Account Category Breakdown
    acc_df = df.groupby('account_cat')['is_break'].agg(['mean', 'count']).sort_values('mean', ascending=False).reset_index()
    axes[1, 1].barh(acc_df['account_cat'], acc_df['mean'] * 100, color='#756bb1', edgecolor='black', alpha=0.85)
    axes[1, 1].set_xlabel('Break Rate (%)', fontweight='bold')
    axes[1, 1].set_title('Break Rate Across Account Categories', fontweight='bold')
    for idx, row in acc_df.iterrows():
        axes[1, 1].text(row['mean']*100 + 0.2, idx, f"{row['mean']*100:.2f}%", va='center', fontsize=9)
    axes[1, 1].set_xlim(0, max(acc_df['mean']*100)*1.25)
    
    plt.tight_layout()
    out_file = os.path.join(FIGURES_DIR, "break_rates_by_operational_drivers.png")
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_file}")

def plot_time_series_break_rate(df: pd.DataFrame):
    """
    Plots daily and rolling 7-day break rate across the chronologically ordered dataset.
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['posting_date']).dt.date
    daily = df.groupby('date')['is_break'].agg(['mean', 'count']).reset_index()
    daily['rolling_7d'] = daily['mean'].rolling(7, min_periods=1).mean()
    
    plt.figure(figsize=(12, 4.5))
    plt.plot(daily['date'], daily['mean'] * 100, color='#9ecae1', alpha=0.5, label='Daily Raw Break Rate')
    plt.plot(daily['date'], daily['rolling_7d'] * 100, color='#08519c', linewidth=2.2, label='7-Day Trailing Trend')
    
    # Train/Test boundary
    split_date = df.iloc[int(len(df)*0.8)]['posting_date'].date()
    plt.axvline(split_date, color='red', linestyle='--', linewidth=1.5, label=f'Train/Test Holdout Split ({split_date})')
    
    plt.title('Chronological Break Rate Trend (Simulated 30,000 Transactions)', fontweight='bold')
    plt.ylabel('Break Rate (%)', fontweight='bold')
    plt.xlabel('Posting Date', fontweight='bold')
    plt.legend(loc='upper right')
    plt.ylim(0, max(daily['rolling_7d']*100)*1.4)
    plt.tight_layout()
    
    out_file = os.path.join(FIGURES_DIR, "chronological_break_rate_trend.png")
    plt.savefig(out_file, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out_file}")

def run_eda():
    set_style()
    os.makedirs(FIGURES_DIR, exist_ok=True)
    print("Running comprehensive EDA and generating visual figures...")
    
    df = pd.read_parquet(ALL_DATA_PATH)
    plot_class_balance_and_differences(df)
    plot_break_rates_by_drivers(df)
    plot_time_series_break_rate(df)
    
    print("EDA Visuals successfully generated.")

if __name__ == "__main__":
    run_eda()
