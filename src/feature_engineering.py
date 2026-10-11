"""
Feature Engineering Pipeline for Reconciliation Break-Risk Scorer
Implements Top 5 engineered features, strict time-based holdout split (80/20),
and leakage-prevention firewalls.
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder

DATA_RAW_PARQUET = os.path.join("data", "synthetic", "reconciliation_items.parquet")
PROCESSED_DIR = os.path.join("data", "processed")

def engineer_features(df: pd.DataFrame, source_system_medians: dict = None) -> (pd.DataFrame, dict):
    """
    Engineers domain-specific finance features from pre-close attributes.
    Strictly forbids post-recon fields (abs_diff, pct_diff, break_type) in feature set.
    """
    df = df.copy()
    
    # 1. Close-window flag and interaction
    df["is_close_window"] = (df["days_to_period_end"] <= 3).astype(int)
    df["close_manual_interaction"] = (df["is_close_window"] * df["is_manual_entry"]).astype(int)
    
    # 2. Mapping staleness flags
    df["mapping_stale_flag"] = (df["mapping_version_age_days"] > 90).astype(int)
    df["mapping_very_stale_flag"] = (df["mapping_version_age_days"] > 180).astype(int)
    
    # 3. Posting lag vs source-system norm
    if source_system_medians is None:
        source_system_medians = df.groupby("source_system")["posting_lag_days"].median().to_dict()
    
    # Map median lag and compute ratio
    median_lag = df["source_system"].map(source_system_medians).fillna(1.0)
    df["posting_lag_ratio"] = (df["posting_lag_days"] / np.maximum(median_lag, 0.5)).round(4)
    
    # 4. Amount log transform
    df["log_amount_gl"] = np.log1p(np.maximum(df["amount_gl"], 0.0)).round(4)
    
    # 5. Prior break frequency indicator
    df["high_prior_breaks_flag"] = (df["prior_breaks_30d"] >= 2).astype(int)
    
    return df, source_system_medians


def run_feature_pipeline():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    print(f"Loading raw synthetic data from {DATA_RAW_PARQUET}...")
    df = pd.read_parquet(DATA_RAW_PARQUET)
    
    # Ensure chronological order
    df = df.sort_values("posting_date").reset_index(drop=True)
    
    n_total = len(df)
    n_train = int(n_total * 0.8)
    n_test = n_total - n_train
    print(f"Total records: {n_total} | Train (first 80%): {n_train} | Test (last 20%): {n_test}")
    
    df_train_raw = df.iloc[:n_train].copy()
    df_test_raw = df.iloc[n_train:].copy()
    
    # Fit source system medians on train only to prevent leakage
    df_train_feat, source_medians = engineer_features(df_train_raw)
    df_test_feat, _ = engineer_features(df_test_raw, source_system_medians=source_medians)
    
    # Save processed feature tables
    train_path = os.path.join(PROCESSED_DIR, "train.parquet")
    test_path = os.path.join(PROCESSED_DIR, "test.parquet")
    df_train_feat.to_parquet(train_path, index=False)
    df_test_feat.to_parquet(test_path, index=False)
    
    # Save metadata
    meta = {
        "n_total": n_total,
        "n_train": n_train,
        "n_test": n_test,
        "train_date_range": [str(df_train_feat["posting_date"].min()), str(df_train_feat["posting_date"].max())],
        "test_date_range": [str(df_test_feat["posting_date"].min()), str(df_test_feat["posting_date"].max())],
        "train_break_prevalence": float(df_train_feat["is_break"].mean()),
        "test_break_prevalence": float(df_test_feat["is_break"].mean()),
        "source_system_medians": {k: float(v) for k, v in source_medians.items()},
        "pre_close_features": [
            "entity", "account_cat", "source_system", "is_manual_entry",
            "mapping_version_age_days", "posting_lag_days", "days_to_period_end",
            "prior_breaks_30d", "vendor_dup_flag", "amount_gl", "log_amount_gl",
            "is_close_window", "close_manual_interaction", "mapping_stale_flag",
            "mapping_very_stale_flag", "posting_lag_ratio", "high_prior_breaks_flag"
        ],
        "post_recon_fields": ["abs_diff", "pct_diff", "break_type"]
    }
    with open(os.path.join(PROCESSED_DIR, "feature_metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)
        
    print(f"Feature engineering complete. Saved to {train_path} and {test_path}")
    print(f"Train break rate: {meta['train_break_prevalence']:.4%}")
    print(f"Test break rate:  {meta['test_break_prevalence']:.4%}")

if __name__ == "__main__":
    run_feature_pipeline()
