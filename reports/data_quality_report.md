# Critical Data Element (CDE) & Data Quality Audit Report

**Dataset Rows**: 30,000 | **Columns**: 16 | **Overall Status**: **PASS**

## 1. Executive Quality Summary

All twelve Critical Data Element (CDE) checks were executed against the ingestion schema to satisfy Finance Controller and Model Risk Management standards prior to model training.

## 2. Check Results Matrix

| Rule ID | Check Name | Dimension | Severity | Status | Findings / Metrics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DQ-001` | Completeness (Missing Values) | Completeness | CRITICAL | ✅ PASS | Found 0 missing values across all columns. |
| `DQ-002` | Uniqueness (Transaction IDs) | Uniqueness | CRITICAL | ✅ PASS | Duplicate transaction IDs detected: 0. |
| `DQ-003` | Categorical Domain Validity | Validity | HIGH | ✅ PASS | Invalid values: entity=0, account_cat=0, source_system=0. |
| `DQ-004` | Range & Sign Validity (GL Amount) | Validity | CRITICAL | ✅ PASS | Transactions with zero or negative GL amounts: 0. |
| `DQ-005` | Logical Consistency (Posting Lag) | Validity | HIGH | ✅ PASS | Impossible negative posting lags found: 0. |
| `DQ-006` | Period-End Proximity Bounds | Validity | MEDIUM | ✅ PASS | Days to period-end outside [0, 31]: 0. |
| `DQ-007` | Target Label Integrity (is_break) | Accuracy | CRITICAL | ✅ PASS | is_break labels present: [np.int64(0), np.int64(1)]. |
| `DQ-008` | Class Prevalence Tolerance | Statistical Integrity | HIGH | ✅ PASS | Observed break prevalence: 7.23% (Tolerance: 5.0% - 10.0%). |
| `DQ-009` | Temporal Sequence Consistency | Timeliness | HIGH | ✅ PASS | Dataset strictly ordered chronologically: True. |
| `DQ-010` | Root-Cause Label Reconciliation | Accuracy | CRITICAL | ✅ PASS | Mismatches: zero-with-cause=0, break-without-cause=0. |
| `DQ-011` | Pre-Close Leakage Firewall | Model Risk / Governance | CRITICAL | ✅ PASS | Non-break items with non-zero difference values: 0. |
| `DQ-012` | Binary Feature Domain Restraint | Validity | MEDIUM | ✅ PASS | All binary indicator columns strictly bounded in {0, 1}: True. |

## 3. Data Leakage Control Attestation

- **Problem 1 (Pre-Close Break Scoring)**: Exclusively utilizes pre-posting and posting-time features (`entity`, `account_cat`, `source_system`, `is_manual_entry`, `mapping_version_age_days`, `posting_lag_days`, `days_to_period_end`, `prior_breaks_30d`, `vendor_dup_flag`, `amount_gl`).
- **Post-Reconciliation Firewall**: Post-close attributes `abs_diff`, `pct_diff`, and `break_type` are strictly quarantined from Problem 1 training tables and only admitted for Problem 2 (Root-Cause Diagnosis).

## 4. Remediation & Continuous Monitoring Guidelines

1. **Mapping Version Age SLA**: Automated notification to Finance Data Stewards when mapping table versions exceed 90 days.
2. **Posting Lag Norm Alerts**: Real-time alerts when ingestion batches exceed 2x the source system's median lag.
3. **Duplicate Vendor Watch**: Immediate hold for review when identical amounts and vendor IDs post within 7 days.
