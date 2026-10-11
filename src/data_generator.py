"""
Data Generator Module for Finance Reconciliation Break-Risk Scorer
Generates a seeded, reproducible synthetic dataset of 30,000 reconciliation items
reflecting realistic general-ledger-vs-source reconciliation dynamics at a financial institution.
"""

import os
import argparse
import numpy as np
import pandas as pd
import duckdb

def generate_reconciliation_data(n_samples: int = 30000, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic reconciliation transactions with realistic statistical properties,
    pre-close feature indicators, and post-reconciliation break labels.
    """
    np.random.seed(seed)
    
    # 1. Transaction Identifiers and Dates (12 months chronological)
    start_date = pd.Timestamp("2026-01-01")
    # Generate dates across 365 days
    day_offsets = np.sort(np.random.randint(0, 365, size=n_samples))
    posting_dates = [start_date + pd.Timedelta(days=int(d)) for d in day_offsets]
    
    transaction_ids = [f"TXN-{i+1:06d}" for i in range(n_samples)]
    
    # 2. Categorical Attributes
    entities = ["Corp", "Settlement", "Clearing", "Data Svcs", "Intl"]
    entity_probs = [0.25, 0.30, 0.20, 0.15, 0.10]
    entity = np.random.choice(entities, size=n_samples, p=entity_probs)
    
    account_cats = ["Fees", "Payroll", "Vendor", "Accruals", "FX Reval", "Intercompany"]
    account_probs = [0.22, 0.12, 0.28, 0.18, 0.08, 0.12]
    account_cat = np.random.choice(account_cats, size=n_samples, p=account_probs)
    
    source_systems = ["ERP", "Billing", "Payroll", "Treasury"]
    source_probs = [0.45, 0.25, 0.15, 0.15]
    source_system = np.random.choice(source_systems, size=n_samples, p=source_probs)
    
    # Align source system logically for Payroll / FX
    for i in range(n_samples):
        if account_cat[i] == "Payroll":
            source_system[i] = "Payroll"
        elif account_cat[i] == "FX Reval" and np.random.rand() < 0.70:
            source_system[i] = "Treasury"
        elif account_cat[i] == "Fees" and np.random.rand() < 0.60:
            source_system[i] = "Billing"
            
    # 3. Process Flags and Time Proximities
    # Manual entry: ~18% base, higher for Accruals and FX Reval
    manual_prob = np.where(
        np.isin(account_cat, ["Accruals", "FX Reval"]), 0.35,
        np.where(account_cat == "Intercompany", 0.22, 0.12)
    )
    is_manual_entry = (np.random.rand(n_samples) < manual_prob).astype(int)
    
    # Mapping version age in days: uniform between 1 and 180 days
    mapping_version_age_days = np.random.randint(1, 181, size=n_samples)
    
    # Days to period-end: calendar cycle (0 to 30 days)
    days_to_period_end = np.array([30 - (d.day % 30) for d in posting_dates])
    
    # Source system typical lag
    # Billing median ~3, ERP median ~1, Payroll median ~2, Treasury median ~2
    source_median_lags = {"ERP": 1.0, "Billing": 3.0, "Payroll": 2.0, "Treasury": 2.0}
    posting_lag_days = []
    for s in source_system:
        base = source_median_lags[s]
        # Lognormal distribution around base
        lag = int(np.clip(np.random.lognormal(mean=np.log(base + 0.1), sigma=0.65), 0, 30))
        posting_lag_days.append(lag)
    posting_lag_days = np.array(posting_lag_days)
    
    # Prior breaks in last 30 days on same entity/account (Poisson)
    prior_breaks_lambda = np.where(
        np.isin(account_cat, ["Intercompany", "FX Reval"]), 0.65, 0.25
    )
    prior_breaks_30d = np.random.poisson(lam=prior_breaks_lambda)
    
    # Vendor duplicate flag: ~3.2% incidence, primarily in Vendor category
    dup_prob = np.where(account_cat == "Vendor", 0.075, 0.010)
    vendor_dup_flag = (np.random.rand(n_samples) < dup_prob).astype(int)
    
    # GL Amount in USD: lognormal distribution ($50 to $500,000)
    # Higher for Intercompany and Clearing
    amount_mu = np.where(
        account_cat == "Intercompany", 10.5, # ~$36k
        np.where(entity == "Clearing", 9.8, 7.8) # ~$18k vs ~$2.4k
    )
    amount_gl = np.round(np.random.lognormal(mean=amount_mu, sigma=1.15), 2)
    amount_gl = np.clip(amount_gl, 25.0, 750000.0)
    
    # 4. Latent Break Risk Function (Ground Truth Logistic Process)
    # Target prevalence: ~7.3% (approx 2,190 breaks in 30,000 items, ~438 in 6,000 test holdout)
    base_intercept = -4.32
    
    # Stale mapping tables are the strongest predictor (PDF Page 6: ~3x the next driver)
    mapping_effect = np.where(mapping_version_age_days >= 90, 1.25, 0.0) + (mapping_version_age_days / 180.0) * 0.55
    
    # Vendor duplicate flag
    dup_effect = vendor_dup_flag * 1.45
    
    # Close-window flag (days_to_period_end <= 3) crossed with manual entry
    close_window = (days_to_period_end <= 3).astype(int)
    close_manual_interaction = (close_window * is_manual_entry) * 1.10
    
    # Excess posting lag vs source median
    lag_ratio = posting_lag_days / np.array([source_median_lags[s] for s in source_system])
    lag_effect = np.clip((lag_ratio - 1.0) * 0.40, 0.0, 1.60)
    
    # Prior breaks effect
    prior_break_effect = np.clip(prior_breaks_30d * 0.32, 0.0, 1.50)
    
    # Account category specific risks
    cat_effects = {
        "Intercompany": 0.35,
        "FX Reval": 0.55,
        "Accruals": 0.20,
        "Vendor": 0.15,
        "Fees": -0.10,
        "Payroll": -0.25
    }
    cat_effect = np.array([cat_effects[c] for c in account_cat])
    
    # Entity specific variance
    entity_effects = {"Settlement": 0.20, "Clearing": 0.15, "Corp": 0.0, "Data Svcs": -0.10, "Intl": 0.10}
    ent_effect = np.array([entity_effects[e] for e in entity])
    
    # Calculate log-odds and probabilities
    log_odds = (
        base_intercept +
        mapping_effect +
        dup_effect +
        close_manual_interaction +
        lag_effect +
        prior_break_effect +
        cat_effect +
        ent_effect
    )
    
    break_probabilities = 1.0 / (1.0 + np.exp(-log_odds))
    is_break = (np.random.rand(n_samples) < break_probabilities).astype(int)
    
    # 5. Post-Reconciliation Fields & Root-Cause Assignment
    # 5 classes: 'timing', 'mapping_error', 'duplicate', 'rounding_fx', 'missing_feed'
    break_type = []
    abs_diff = []
    pct_diff = []
    
    for i in range(n_samples):
        if is_break[i] == 0:
            break_type.append("none")
            abs_diff.append(0.0)
            pct_diff.append(0.0)
        else:
            # Assign root cause based on observable feature profile matching PDF distribution:
            # Mapping error (~40%), Timing (~32%), Rounding/FX (~14%), Missing feed (~9%), Duplicate (~5%)
            if vendor_dup_flag[i] == 1 and np.random.rand() < 0.85:
                rc = "duplicate"
                diff = float(amount_gl[i]) # duplicate has 100% full amount difference
                p_diff = 1.0
            elif account_cat[i] == "FX Reval" and np.random.rand() < 0.65:
                rc = "rounding_fx"
                diff = float(np.round(np.random.uniform(0.01, 1.75), 2)) # small dollar difference under $2
                p_diff = float(np.round(diff / amount_gl[i], 6))
            elif mapping_version_age_days[i] >= 90 and np.random.rand() < 0.70:
                rc = "mapping_error"
                # Mapping error typically large difference
                diff = float(np.round(np.clip(np.random.lognormal(mean=7.5, sigma=0.8), 25.0, amount_gl[i]), 2))
                p_diff = float(np.round(diff / amount_gl[i], 4))
            elif posting_lag_days[i] >= 4 and np.random.rand() < 0.75:
                rc = "timing"
                diff = float(np.round(np.clip(np.random.lognormal(mean=6.2, sigma=0.9), 10.0, amount_gl[i]), 2))
                p_diff = float(np.round(diff / amount_gl[i], 4))
            elif np.random.rand() < 0.35 and is_manual_entry[i] == 0:
                rc = "missing_feed"
                diff = float(amount_gl[i]) # missing feed has 100% diff
                p_diff = 1.0
            else:
                # Weighted random selection across remaining causes
                choices = ["timing", "mapping_error", "rounding_fx", "missing_feed"]
                p_choices = [0.40, 0.40, 0.12, 0.08]
                rc = np.random.choice(choices, p=p_choices)
                if rc == "rounding_fx":
                    diff = float(np.round(np.random.uniform(0.02, 1.50), 2))
                elif rc == "missing_feed":
                    diff = float(amount_gl[i])
                else:
                    diff = float(np.round(np.clip(np.random.lognormal(mean=6.5, sigma=1.0), 10.0, amount_gl[i]), 2))
                p_diff = float(np.round(diff / amount_gl[i], 4))
                
            break_type.append(rc)
            abs_diff.append(diff)
            pct_diff.append(p_diff)
            
    df = pd.DataFrame({
        "transaction_id": transaction_ids,
        "posting_date": posting_dates,
        "entity": entity,
        "account_cat": account_cat,
        "source_system": source_system,
        "is_manual_entry": is_manual_entry,
        "mapping_version_age_days": mapping_version_age_days,
        "posting_lag_days": posting_lag_days,
        "days_to_period_end": days_to_period_end,
        "prior_breaks_30d": prior_breaks_30d,
        "vendor_dup_flag": vendor_dup_flag,
        "amount_gl": amount_gl,
        "is_break": is_break,
        "break_type": break_type,
        "abs_diff": abs_diff,
        "pct_diff": pct_diff
    })
    
    return df

def save_data(df: pd.DataFrame, base_dir: str):
    """Save dataset to CSV, Parquet, and embedded DuckDB."""
    synthetic_dir = os.path.join(base_dir, "data", "synthetic")
    os.makedirs(synthetic_dir, exist_ok=True)
    
    csv_path = os.path.join(synthetic_dir, "reconciliation_items.csv")
    parquet_path = os.path.join(synthetic_dir, "reconciliation_items.parquet")
    duckdb_path = os.path.join(synthetic_dir, "reconciliation.duckdb")
    
    # Save CSV and Parquet
    df.to_csv(csv_path, index=False)
    df.to_parquet(parquet_path, index=False)
    print(f"Saved CSV to {csv_path}")
    print(f"Saved Parquet to {parquet_path}")
    
    # Save to DuckDB
    con = duckdb.connect(duckdb_path)
    con.execute("CREATE OR REPLACE TABLE reconciliation_items AS SELECT * FROM df")
    count = con.execute("SELECT COUNT(*) FROM reconciliation_items").fetchone()[0]
    break_count = con.execute("SELECT COUNT(*) FROM reconciliation_items WHERE is_break = 1").fetchone()[0]
    con.close()
    print(f"Saved to DuckDB: {duckdb_path} ({count} rows, {break_count} breaks, {break_count/count:.2%} break rate)")
    
    # Generate Schema Markdown
    schema_path = os.path.join(synthetic_dir, "schema.md")
    with open(schema_path, "w", encoding="utf-8") as f:
        f.write("# Synthetic Reconciliation Dataset Schema\n\n")
        f.write("| Column Name | Physical Type | Logical Type | Known at Posting? | Description |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        f.write("| `transaction_id` | VARCHAR | Identifier | Yes | Unique reconciliation transaction identifier |\n")
        f.write("| `posting_date` | TIMESTAMP | Date | Yes | Transaction posting timestamp (chronological) |\n")
        f.write("| `entity` | VARCHAR | Categorical | Yes | Legal entity or business line (Corp, Settlement, Clearing, Data Svcs, Intl) |\n")
        f.write("| `account_cat` | VARCHAR | Categorical | Yes | GL account category (Fees, Payroll, Vendor, Accruals, FX Reval, Intercompany) |\n")
        f.write("| `source_system` | VARCHAR | Categorical | Yes | Ingestion feed origin (ERP, Billing, Payroll, Treasury) |\n")
        f.write("| `is_manual_entry` | INTEGER | Binary (0/1) | Yes | Manual journal adjustment (1) vs. automated straight-through feed (0) |\n")
        f.write("| `mapping_version_age_days` | INTEGER | Numeric | Yes | Days elapsed since current chart-of-accounts mapping rule was refreshed |\n")
        f.write("| `posting_lag_days` | INTEGER | Numeric | Yes | Elapsed calendar days between economic transaction date and GL booking |\n")
        f.write("| `days_to_period_end` | INTEGER | Numeric | Yes | Calendar days remaining until month-end financial close |\n")
        f.write("| `prior_breaks_30d` | INTEGER | Numeric | Yes | Historical break count for same entity/account over trailing 30 days |\n")
        f.write("| `vendor_dup_flag` | INTEGER | Binary (0/1) | Yes | Algorithmic indicator of identical vendor & amount within trailing 7 days |\n")
        f.write("| `amount_gl` | DOUBLE | Numeric (USD) | Yes | General Ledger transaction monetary value in USD |\n")
        f.write("| `is_break` | INTEGER | Binary (0/1) | Target (P1) | Ground truth reconciliation break status (1 = break, 0 = matched) |\n")
        f.write("| `break_type` | VARCHAR | Categorical | Target (P2) | Root cause classification: none, timing, mapping_error, duplicate, rounding_fx, missing_feed |\n")
        f.write("| `abs_diff` | DOUBLE | Numeric (USD) | Post-recon Only | Absolute monetary discrepancy between GL and source record |\n")
        f.write("| `pct_diff` | DOUBLE | Numeric (Ratio) | Post-recon Only | Discrepancy expressed as a fraction of GL transaction amount |\n")
    print(f"Generated Schema documentation at {schema_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic reconciliation data.")
    parser.add_argument("--samples", type=int, default=30000, help="Number of records to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--dir", type=str, default=".", help="Base project directory")
    args = parser.parse_args()
    
    df = generate_reconciliation_data(n_samples=args.samples, seed=args.seed)
    save_data(df, args.dir)
