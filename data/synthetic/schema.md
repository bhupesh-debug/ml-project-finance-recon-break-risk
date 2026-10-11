# Synthetic Reconciliation Dataset Schema

| Column Name | Physical Type | Logical Type | Known at Posting? | Description |
| :--- | :--- | :--- | :--- | :--- |
| `transaction_id` | VARCHAR | Identifier | Yes | Unique reconciliation transaction identifier |
| `posting_date` | TIMESTAMP | Date | Yes | Transaction posting timestamp (chronological) |
| `entity` | VARCHAR | Categorical | Yes | Legal entity or business line (Corp, Settlement, Clearing, Data Svcs, Intl) |
| `account_cat` | VARCHAR | Categorical | Yes | GL account category (Fees, Payroll, Vendor, Accruals, FX Reval, Intercompany) |
| `source_system` | VARCHAR | Categorical | Yes | Ingestion feed origin (ERP, Billing, Payroll, Treasury) |
| `is_manual_entry` | INTEGER | Binary (0/1) | Yes | Manual journal adjustment (1) vs. automated straight-through feed (0) |
| `mapping_version_age_days` | INTEGER | Numeric | Yes | Days elapsed since current chart-of-accounts mapping rule was refreshed |
| `posting_lag_days` | INTEGER | Numeric | Yes | Elapsed calendar days between economic transaction date and GL booking |
| `days_to_period_end` | INTEGER | Numeric | Yes | Calendar days remaining until month-end financial close |
| `prior_breaks_30d` | INTEGER | Numeric | Yes | Historical break count for same entity/account over trailing 30 days |
| `vendor_dup_flag` | INTEGER | Binary (0/1) | Yes | Algorithmic indicator of identical vendor & amount within trailing 7 days |
| `amount_gl` | DOUBLE | Numeric (USD) | Yes | General Ledger transaction monetary value in USD |
| `is_break` | INTEGER | Binary (0/1) | Target (P1) | Ground truth reconciliation break status (1 = break, 0 = matched) |
| `break_type` | VARCHAR | Categorical | Target (P2) | Root cause classification: none, timing, mapping_error, duplicate, rounding_fx, missing_feed |
| `abs_diff` | DOUBLE | Numeric (USD) | Post-recon Only | Absolute monetary discrepancy between GL and source record |
| `pct_diff` | DOUBLE | Numeric (Ratio) | Post-recon Only | Discrepancy expressed as a fraction of GL transaction amount |
