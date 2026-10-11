"""
Unit tests for serialized machine learning models and evaluation metrics
"""

import os
import joblib
import pytest
import pandas as pd
import numpy as np

BEST_MODEL_PATH = os.path.join("models", "best_model.pkl")
RC_MODEL_PATH = os.path.join("models", "root_cause_classifier.joblib")
TEST_DATA_PATH = os.path.join("data", "processed", "test.parquet")

def test_models_exist():
    assert os.path.exists(BEST_MODEL_PATH), "best_model.pkl does not exist"
    assert os.path.exists(RC_MODEL_PATH), "root_cause_classifier.joblib does not exist"

def test_best_model_inference():
    model = joblib.load(BEST_MODEL_PATH)
    df_test = pd.read_parquet(TEST_DATA_PATH)
    
    feature_cols = [
        'entity', 'account_cat', 'source_system', 'is_manual_entry',
        'mapping_version_age_days', 'posting_lag_days', 'days_to_period_end',
        'prior_breaks_30d', 'vendor_dup_flag', 'amount_gl', 'log_amount_gl',
        'is_close_window', 'close_manual_interaction', 'mapping_stale_flag',
        'mapping_very_stale_flag', 'posting_lag_ratio', 'high_prior_breaks_flag'
    ]
    
    probs = model.predict_proba(df_test[feature_cols].head(100))[:, 1]
    assert len(probs) == 100
    assert (probs >= 0.0).all() and (probs <= 1.0).all(), "Predicted probabilities must be within [0.0, 1.0]"

def test_root_cause_classifier_predictions():
    rc_model = joblib.load(RC_MODEL_PATH)
    df_test = pd.read_parquet(TEST_DATA_PATH)
    breaks = df_test[df_test['is_break'] == 1].copy()
    
    breaks['log10_abs_diff'] = np.log10(np.maximum(breaks['abs_diff'], 0.01))
    breaks['is_sub_dollar'] = (breaks['abs_diff'] < 1.0).astype(int)
    breaks['is_full_amount'] = (np.abs(breaks['abs_diff'] - breaks['amount_gl']) < 1.0).astype(int)
    breaks['pct_diff_capped'] = np.clip(breaks['pct_diff'], 0.0, 2.0)
    
    feature_cols = [
        'mapping_version_age_days', 'posting_lag_days', 'days_to_period_end',
        'prior_breaks_30d', 'amount_gl', 'log_amount_gl', 'posting_lag_ratio',
        'log10_abs_diff', 'pct_diff_capped', 'is_manual_entry', 'vendor_dup_flag',
        'is_close_window', 'close_manual_interaction', 'mapping_stale_flag',
        'is_sub_dollar', 'is_full_amount', 'entity', 'account_cat', 'source_system'
    ]
    
    preds = rc_model.predict(breaks[feature_cols].head(50))
    valid_classes = {'rounding_fx', 'mapping_error', 'timing', 'missing_feed', 'duplicate'}
    for p in preds:
        assert p in valid_classes, f"Unexpected root-cause class prediction: {p}"
