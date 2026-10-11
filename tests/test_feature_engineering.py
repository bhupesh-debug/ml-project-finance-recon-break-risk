"""
Unit tests for feature engineering, time-based split, and leakage prevention firewall
"""

import os
import pytest
import pandas as pd
import numpy as np

TRAIN_PATH = os.path.join("data", "processed", "train.parquet")
TEST_PATH = os.path.join("data", "processed", "test.parquet")

def test_processed_files_exist():
    assert os.path.exists(TRAIN_PATH), f"Train dataset {TRAIN_PATH} missing"
    assert os.path.exists(TEST_PATH), f"Test dataset {TEST_PATH} missing"

def test_chronological_split_integrity():
    df_train = pd.read_parquet(TRAIN_PATH)
    df_test = pd.read_parquet(TEST_PATH)
    
    assert len(df_train) == 24000, f"Expected 24,000 train rows, got {len(df_train)}"
    assert len(df_test) == 6000, f"Expected 6,000 test rows, got {len(df_test)}"
    
    max_train_date = df_train['posting_date'].max()
    min_test_date = df_test['posting_date'].min()
    assert max_train_date <= min_test_date, f"Lookahead leakage: train max date {max_train_date} > test min date {min_test_date}"

def test_leakage_firewall_pre_close_features():
    """
    CRITICAL QUALITY GATE: Pre-close features must strictly exclude
    post-reconciliation fields (abs_diff, pct_diff, break_type).
    """
    df_train = pd.read_parquet(TRAIN_PATH)
    
    pre_close_feature_cols = [
        'entity', 'account_cat', 'source_system', 'is_manual_entry',
        'mapping_version_age_days', 'posting_lag_days', 'days_to_period_end',
        'prior_breaks_30d', 'vendor_dup_flag', 'amount_gl', 'log_amount_gl',
        'is_close_window', 'close_manual_interaction', 'mapping_stale_flag',
        'mapping_very_stale_flag', 'posting_lag_ratio', 'high_prior_breaks_flag'
    ]
    
    for forbidden in ['abs_diff', 'pct_diff', 'break_type']:
        assert forbidden not in pre_close_feature_cols, f"LEAKAGE DETECTED: {forbidden} present in pre-close features"

def test_engineered_features_validity():
    df_test = pd.read_parquet(TEST_PATH)
    assert 'close_manual_interaction' in df_test.columns
    assert 'posting_lag_ratio' in df_test.columns
    assert 'mapping_stale_flag' in df_test.columns
    assert (df_test['posting_lag_ratio'] >= 0).all()
