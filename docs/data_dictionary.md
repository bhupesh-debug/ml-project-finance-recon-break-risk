# Enterprise Data Dictionary & Critical Data Element (CDE) Register
## Finance Reconciliation Analytics & Break-Risk Modeling Pipeline
**Target Organization:** DTCC CFO Organization / Financial Data Governance  
**Framework:** Basel Committee on Banking Supervision (BCBS 239) & SOX 404 Data Quality Standards  
**Version:** 1.0 | **Author:** Bhupesh Chandra Dimri

---

### 1. Data Schema & Critical Data Element (CDE) Matrix

| Column Name | Physical Type | Logical Type | CDE? | Nullable? | Valid Range / Allowed Values | Data Owner | Known at Posting? | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `transaction_id` | VARCHAR(36) | Identifier | Yes | No | UUID format (`TXN-xxxxxxxx`) | Financial Systems IT | Yes | Unique surrogate key identifying each reconciliation item. |
| `posting_date` | TIMESTAMP | Temporal | Yes | No | 2026-01-01 to 2026-10-31 | General Ledger Accounting | Yes | Chronological date/time when transaction was booked to the General Ledger. |
| `entity` | VARCHAR(30) | Categorical | Yes | No | `Corp`, `Settlement`, `Clearing`, `Data Svcs`, `Intl` | Legal Entity Controller | Yes | DTCC legal entity or operating subsidiary holding the account balance. |
| `account_cat` | VARCHAR(30) | Categorical | Yes | No | `Fees`, `Payroll`, `Vendor`, `Accruals`, `FX Reval`, `Intercompany` | Financial Reporting / Chart of Accounts | Yes | Functional General Ledger account category classifying the economic nature of the entry. |
| `source_system` | VARCHAR(30) | Categorical | Yes | No | `ERP`, `Billing`, `Payroll`, `Treasury` | Finance Technology Operations | Yes | Upstream sub-ledger or transaction processing engine originating the feed. |
| `is_manual_entry` | INTEGER | Binary Flag | Yes | No | `0` (Automated feed), `1` (Manual journal entry) | General Ledger Operations | Yes | Indicator distinguishing automated straight-through feeds from human manual adjustments. |
| `mapping_version_age_days`| INTEGER | Numeric (Days) | Yes | No | `0` to `365` days | Master Data Governance | Yes | Number of elapsed calendar days since the Chart-of-Accounts account-mapping rule version was updated. |
| `posting_lag_days` | INTEGER | Numeric (Days) | No | No | `0` to `30` days | Sub-Ledger Operations | Yes | Elapsed calendar days between economic transaction value date and GL booking date. |
| `days_to_period_end` | INTEGER | Numeric (Days) | Yes | No | `0` to `30` days | Month-End Close Coordination | Yes | Calendar days remaining until official month-end financial reporting close. |
| `prior_breaks_30d` | INTEGER | Count | Yes | No | `0` to `15` | Reconciliation Operations | Yes | Count of historical breaks recorded on the identical entity-account combination over trailing 30 days. |
| `vendor_dup_flag` | INTEGER | Binary Flag | Yes | No | `0` (Unique), `1` (Duplicate signature) | Accounts Payable Operations | Yes | Algorithmic indicator of identical vendor identifier and monetary amount booked within trailing 7 days. |
| `amount_gl` | DOUBLE | Numeric (USD) | Yes | No | `$0.01` to `$10,000,000.00` | Treasury & Financial Reporting | Yes | Absolute monetary value of the General Ledger transaction in USD. |
| `is_break` | INTEGER | Target (P1) | Yes | No | `0` (Matched / Reconciled), `1` (Reconciliation Break) | Reconciliation Operations | Target | Ground truth label indicating whether the transaction subsequently failed reconciliation during close. |
| `break_type` | VARCHAR(30) | Target (P2) | Yes | No | `none`, `timing`, `mapping_error`, `duplicate`, `rounding_fx`, `missing_feed` | Reconciliation Operations | Target | Multi-class root-cause taxonomy explaining the operational origin of the reconciliation break. |
| `abs_diff` | DOUBLE | Post-Recon | No | Yes (0.0 if matched) | `$0.00` to `$10,000,000.00` | Bank Reconciliation Team | **No (Post-Recon)** | Absolute monetary discrepancy between GL booking and counterparty/bank source record. |
| `pct_diff` | DOUBLE | Post-Recon | No | Yes (0.0 if matched) | `0.00` to `2.00` (Ratio) | Bank Reconciliation Team | **No (Post-Recon)** | Monetary variance expressed as a fraction of total General Ledger transaction value (`abs_diff / amount_gl`). |

---

### 2. Critical Data Element (CDE) Definitions & Governance SLAs

1. **`mapping_version_age_days` (CDE-01):**
   - **Quality Rule:** Must be <= 90 calendar days under Finance Master Data Service Level Agreement.
   - **Remediation Action:** Versions exceeding 90 days trigger automated notification to Chart-of-Accounts Governance for rule re-certification.
   
2. **`is_manual_entry` (CDE-02):**
   - **Quality Rule:** Mandatory dual-authorization sign-off for manual journals exceeding $250,000.
   - **Remediation Action:** Flagged in pre-close scoring with interaction multiplier during the final 3 days of close.

3. **`vendor_dup_flag` (CDE-03):**
   - **Quality Rule:** Zero tolerance for undetected duplicate disbursements.
   - **Remediation Action:** Triggers immediate `CRITICAL` queue priority and disbursement hold.

4. **`amount_gl` (CDE-04):**
   - **Quality Rule:** Monetary amount must be non-negative and non-null (`amount_gl > 0`).
   - **Remediation Action:** Transactions violating amount boundaries rejected at ingestion schema validation.
