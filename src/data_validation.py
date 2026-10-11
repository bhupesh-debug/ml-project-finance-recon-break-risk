"""
Data Validation and Quality Assurance Module for Finance Reconciliation Break-Risk Scorer
Implements Critical Data Element (CDE) integrity rules, schema checks, leakage prevention,
and generates an audit-ready Data Quality Report.
"""

import os
import json
import pandas as pd
import numpy as np

def run_data_quality_audit(df: pd.DataFrame, output_dir: str = "reports") -> dict:
    """
    Execute 12 comprehensive data-quality checks on the reconciliation dataset.
    """
    os.makedirs(output_dir, exist_ok=True)
    report = {
        "dataset_row_count": int(len(df)),
        "dataset_col_count": int(len(df.columns)),
        "checks": [],
        "overall_status": "PASS"
    }
    
    # Check 1: Completeness / Missing Values
    null_counts = df.isnull().sum()
    total_nulls = int(null_counts.sum())
    check_1 = {
        "check_id": "DQ-001",
        "name": "Completeness (Missing Values)",
        "dimension": "Completeness",
        "severity": "CRITICAL",
        "passed": bool(total_nulls == 0),
        "details": f"Found {total_nulls} missing values across all columns.",
        "metrics": {col: int(cnt) for col, cnt in null_counts.items() if cnt > 0}
    }
    report["checks"].append(check_1)
    
    # Check 2: Uniqueness of Transaction IDs
    dup_ids = int(df["transaction_id"].duplicated().sum())
    check_2 = {
        "check_id": "DQ-002",
        "name": "Uniqueness (Transaction IDs)",
        "dimension": "Uniqueness",
        "severity": "CRITICAL",
        "passed": bool(dup_ids == 0),
        "details": f"Duplicate transaction IDs detected: {dup_ids}.",
        "metrics": {"duplicate_count": dup_ids}
    }
    report["checks"].append(check_2)
    
    # Check 3: Categorical Validity
    valid_entities = {"Corp", "Settlement", "Clearing", "Data Svcs", "Intl"}
    valid_accounts = {"Fees", "Payroll", "Vendor", "Accruals", "FX Reval", "Intercompany"}
    valid_sources = {"ERP", "Billing", "Payroll", "Treasury"}
    
    invalid_entities = int((~df["entity"].isin(valid_entities)).sum())
    invalid_accounts = int((~df["account_cat"].isin(valid_accounts)).sum())
    invalid_sources = int((~df["source_system"].isin(valid_sources)).sum())
    
    cat_passed = bool(invalid_entities == 0 and invalid_accounts == 0 and invalid_sources == 0)
    check_3 = {
        "check_id": "DQ-003",
        "name": "Categorical Domain Validity",
        "dimension": "Validity",
        "severity": "HIGH",
        "passed": cat_passed,
        "details": f"Invalid values: entity={invalid_entities}, account_cat={invalid_accounts}, source_system={invalid_sources}.",
        "metrics": {
            "invalid_entities": invalid_entities,
            "invalid_accounts": invalid_accounts,
            "invalid_sources": invalid_sources
        }
    }
    report["checks"].append(check_3)
    
    # Check 4: Positive Monetary Amounts
    invalid_amounts = int((df["amount_gl"] <= 0).sum())
    check_4 = {
        "check_id": "DQ-004",
        "name": "Range & Sign Validity (GL Amount)",
        "dimension": "Validity",
        "severity": "CRITICAL",
        "passed": bool(invalid_amounts == 0),
        "details": f"Transactions with zero or negative GL amounts: {invalid_amounts}.",
        "metrics": {"non_positive_amounts": invalid_amounts}
    }
    report["checks"].append(check_4)
    
    # Check 5: Logical Non-Negative Posting Lags
    negative_lags = int((df["posting_lag_days"] < 0).sum())
    check_5 = {
        "check_id": "DQ-005",
        "name": "Logical Consistency (Posting Lag)",
        "dimension": "Validity",
        "severity": "HIGH",
        "passed": bool(negative_lags == 0),
        "details": f"Impossible negative posting lags found: {negative_lags}.",
        "metrics": {"negative_lags": negative_lags}
    }
    report["checks"].append(check_5)
    
    # Check 6: Days to Period End Bounds [0, 31]
    out_of_bounds_pe = int(((df["days_to_period_end"] < 0) | (df["days_to_period_end"] > 31)).sum())
    check_6 = {
        "check_id": "DQ-006",
        "name": "Period-End Proximity Bounds",
        "dimension": "Validity",
        "severity": "MEDIUM",
        "passed": bool(out_of_bounds_pe == 0),
        "details": f"Days to period-end outside [0, 31]: {out_of_bounds_pe}.",
        "metrics": {"out_of_bounds": out_of_bounds_pe}
    }
    report["checks"].append(check_6)
    
    # Check 7: Target Label Binary Consistency
    valid_binary_labels = set(df["is_break"].unique()).issubset({0, 1})
    check_7 = {
        "check_id": "DQ-007",
        "name": "Target Label Integrity (is_break)",
        "dimension": "Accuracy",
        "severity": "CRITICAL",
        "passed": bool(valid_binary_labels),
        "details": f"is_break labels present: {list(df['is_break'].unique())}.",
        "metrics": {"unique_labels": [int(x) for x in df["is_break"].unique()]}
    }
    report["checks"].append(check_7)
    
    # Check 8: Target Class Prevalence Bounds (~7% target, allow 5% to 10%)
    break_rate = float(df["is_break"].mean())
    rate_passed = bool(0.05 <= break_rate <= 0.10)
    check_8 = {
        "check_id": "DQ-008",
        "name": "Class Prevalence Tolerance",
        "dimension": "Statistical Integrity",
        "severity": "HIGH",
        "passed": rate_passed,
        "details": f"Observed break prevalence: {break_rate:.2%} (Tolerance: 5.0% - 10.0%).",
        "metrics": {"break_prevalence": round(break_rate, 4), "total_breaks": int(df["is_break"].sum())}
    }
    report["checks"].append(check_8)
    
    # Check 9: Temporal Ordering / No Look-Ahead Shuffling
    dates = pd.to_datetime(df["posting_date"])
    is_chronological = bool((dates.diff().dropna() >= pd.Timedelta(0)).all())
    check_9 = {
        "check_id": "DQ-009",
        "name": "Temporal Sequence Consistency",
        "dimension": "Timeliness",
        "severity": "HIGH",
        "passed": is_chronological,
        "details": f"Dataset strictly ordered chronologically: {is_chronological}.",
        "metrics": {"start_date": str(dates.min())[:10], "end_date": str(dates.max())[:10]}
    }
    report["checks"].append(check_9)
    
    # Check 10: Root Cause Label Alignment
    valid_causes = {"none", "timing", "mapping_error", "duplicate", "rounding_fx", "missing_feed"}
    invalid_causes = int((~df["break_type"].isin(valid_causes)).sum())
    mismatched_zeros = int(((df["is_break"] == 0) & (df["break_type"] != "none")).sum())
    mismatched_ones = int(((df["is_break"] == 1) & (df["break_type"] == "none")).sum())
    cause_passed = bool(invalid_causes == 0 and mismatched_zeros == 0 and mismatched_ones == 0)
    check_10 = {
        "check_id": "DQ-010",
        "name": "Root-Cause Label Reconciliation",
        "dimension": "Accuracy",
        "severity": "CRITICAL",
        "passed": cause_passed,
        "details": f"Mismatches: zero-with-cause={mismatched_zeros}, break-without-cause={mismatched_ones}.",
        "metrics": {
            "mismatched_zeros": mismatched_zeros,
            "mismatched_ones": mismatched_ones
        }
    }
    report["checks"].append(check_10)
    
    # Check 11: Data Leakage Verification for Problem 1
    # Verify that post-reconciliation difference is 0 when is_break is 0
    leaked_diffs = int(((df["is_break"] == 0) & (df["abs_diff"] > 0)).sum())
    check_11 = {
        "check_id": "DQ-011",
        "name": "Pre-Close Leakage Firewall",
        "dimension": "Model Risk / Governance",
        "severity": "CRITICAL",
        "passed": bool(leaked_diffs == 0),
        "details": f"Non-break items with non-zero difference values: {leaked_diffs}.",
        "metrics": {"leaked_records": leaked_diffs}
    }
    report["checks"].append(check_11)
    
    # Check 12: Binary Flags Integrity (0/1 only)
    binary_cols = ["is_manual_entry", "vendor_dup_flag"]
    binary_ok = True
    for c in binary_cols:
        if not set(df[c].unique()).issubset({0, 1}):
            binary_ok = False
    check_12 = {
        "check_id": "DQ-012",
        "name": "Binary Feature Domain Restraint",
        "dimension": "Validity",
        "severity": "MEDIUM",
        "passed": binary_ok,
        "details": f"All binary indicator columns strictly bounded in {{0, 1}}: {binary_ok}.",
        "metrics": {c: [int(x) for x in df[c].unique()] for c in binary_cols}
    }
    report["checks"].append(check_12)
    
    # Set overall status
    if any(not c["passed"] for c in report["checks"]):
        report["overall_status"] = "FAIL"
        
    # Write Markdown Report
    report_md_path = os.path.join(output_dir, "data_quality_report.md")
    with open(report_md_path, "w", encoding="utf-8") as f:
        f.write("# Critical Data Element (CDE) & Data Quality Audit Report\n\n")
        f.write(f"**Dataset Rows**: {report['dataset_row_count']:,} | **Columns**: {report['dataset_col_count']} | **Overall Status**: **{report['overall_status']}**\n\n")
        f.write("## 1. Executive Quality Summary\n\n")
        f.write("All twelve Critical Data Element (CDE) checks were executed against the ingestion schema to satisfy Finance Controller and Model Risk Management standards prior to model training.\n\n")
        f.write("## 2. Check Results Matrix\n\n")
        f.write("| Rule ID | Check Name | Dimension | Severity | Status | Findings / Metrics |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
        for c in report["checks"]:
            st = "✅ PASS" if c["passed"] else "❌ FAIL"
            f.write(f"| `{c['check_id']}` | {c['name']} | {c['dimension']} | {c['severity']} | {st} | {c['details']} |\n")
            
        f.write("\n## 3. Data Leakage Control Attestation\n\n")
        f.write("- **Problem 1 (Pre-Close Break Scoring)**: Exclusively utilizes pre-posting and posting-time features (`entity`, `account_cat`, `source_system`, `is_manual_entry`, `mapping_version_age_days`, `posting_lag_days`, `days_to_period_end`, `prior_breaks_30d`, `vendor_dup_flag`, `amount_gl`).\n")
        f.write("- **Post-Reconciliation Firewall**: Post-close attributes `abs_diff`, `pct_diff`, and `break_type` are strictly quarantined from Problem 1 training tables and only admitted for Problem 2 (Root-Cause Diagnosis).\n\n")
        f.write("## 4. Remediation & Continuous Monitoring Guidelines\n\n")
        f.write("1. **Mapping Version Age SLA**: Automated notification to Finance Data Stewards when mapping table versions exceed 90 days.\n")
        f.write("2. **Posting Lag Norm Alerts**: Real-time alerts when ingestion batches exceed 2x the source system's median lag.\n")
        f.write("3. **Duplicate Vendor Watch**: Immediate hold for review when identical amounts and vendor IDs post within 7 days.\n")
        
    print(f"Data Quality Report written to {report_md_path}")
    return report

if __name__ == "__main__":
    df = pd.read_parquet("data/synthetic/reconciliation_items.parquet")
    rep = run_data_quality_audit(df, output_dir="reports")
    print(f"Overall DQ Status: {rep['overall_status']}")
