"""
Unit tests for triage rules, governance controls, and audit trail schema
"""

import os
import pytest
import pandas as pd
from src.triage_engine import rule_based_triage

def test_sub_dollar_auto_clearing_rule():
    row = pd.Series({
        'transaction_id': 'TXN-TEST-001',
        'break_type': 'rounding_fx',
        'amount_gl': 450.00,
        'abs_diff': 0.45,
        'mapping_version_age_days': 20,
        'is_manual_entry': 0,
        'days_to_period_end': 15,
        'vendor_dup_flag': 0
    })
    
    triage = rule_based_triage(row)
    assert triage['auto_clearing_eligible'] is True
    assert triage['priority'] == "LOW / AUTO-CLEAR"
    assert "strictly below the $1.00 materiality" in triage['evidence'][0]

def test_duplicate_vendor_critical_escalation():
    row = pd.Series({
        'transaction_id': 'TXN-TEST-002',
        'break_type': 'duplicate',
        'amount_gl': 15000.00,
        'abs_diff': 15000.00,
        'mapping_version_age_days': 25,
        'is_manual_entry': 1,
        'days_to_period_end': 5,
        'vendor_dup_flag': 1
    })
    
    triage = rule_based_triage(row)
    assert triage['priority'] == "CRITICAL"
    assert triage['auto_clearing_eligible'] is False
    assert "HOLD & ESCALATE" in triage['recommended_action']

def test_stale_mapping_remediation_rule():
    row = pd.Series({
        'transaction_id': 'TXN-TEST-003',
        'break_type': 'mapping_error',
        'amount_gl': 2500.00,
        'abs_diff': 120.00,
        'mapping_version_age_days': 140,
        'is_manual_entry': 0,
        'days_to_period_end': 2,
        'vendor_dup_flag': 0
    })
    
    triage = rule_based_triage(row)
    assert triage['priority'] == "HIGH" # Close window <= 3 days
    assert "REMEDIATE MAPPING" in triage['recommended_action']
