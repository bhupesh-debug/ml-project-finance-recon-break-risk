"""
Unit tests for data generator and schema integrity
"""

import os
import pytest
import pandas as pd
import numpy as np

DATA_PARQUET = os.path.join("data", "synthetic", "reconciliation_items.parquet")

def test_dataset_exists_and_shape():
    assert os.path.exists(DATA_PARQUET), f"Dataset {DATA_PARQUET} does not exist"
    df = pd.read_parquet(DATA_PARQUET)
    assert len(df) == 30000, f"Expected 30,000 rows, got {len(df)}"
    assert df['transaction_id'].nunique() == 30000, "Transaction IDs must be unique"

def test_break_prevalence_calibrated():
    df = pd.read_parquet(DATA_PARQUET)
    break_rate = df['is_break'].mean()
    assert 0.065 <= break_rate <= 0.080, f"Break rate {break_rate:.4f} outside expected range [6.5%, 8.0%]"

def test_no_null_values_in_critical_fields():
    df = pd.read_parquet(DATA_PARQUET)
    critical_fields = ['transaction_id', 'posting_date', 'entity', 'account_cat', 'source_system', 'amount_gl', 'is_break']
    for field in critical_fields:
        assert df[field].isnull().sum() == 0, f"Critical field {field} contains null values"

def test_chronological_ordering():
    df = pd.read_parquet(DATA_PARQUET)
    assert df['posting_date'].is_monotonic_increasing, "Transactions must be chronologically ordered by posting_date"
