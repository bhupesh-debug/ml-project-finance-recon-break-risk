# User Acceptance Testing (UAT) Test Plan & Execution Scripts
## Reconciliation Break-Risk Scorer and Root-Cause Triage
**Target Organization:** DTCC CFO Organization / Business Acceptance Testing Team  
**Author:** Bhupesh Chandra Dimri | October 2026

---

### 1. UAT Execution Summary
- **Test Cycles:** 2 Formal Test Cycles (Cycle 1: Functional & Algorithmic; Cycle 2: Operational Queue & Governance Sign-Off)
- **Total Test Cases:** 10 Structured Scripts
- **Target Pass Rate:** 100% for Critical & High Priority Scripts

---

### 2. Detailed UAT Test Scripts

| Test Case ID | Test Scenario | Pre-Conditions | Step-by-Step Test Procedure | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **UAT-01** | Risk-Ranked Queue Sorting | Scored batch of 6,000 holdout records available | 1. Launch review queue dashboard.<br>2. Inspect default sort order in queue table. | Transactions strictly sorted descending by `risk_score`. Highest risk at row 1. | Exactly sorted from highest risk score (0.99) downward. | **PASS** |
| **UAT-02** | Capacity Slider Dynamic Thresholding | Review queue loaded | 1. Move capacity slider to 10%.<br>2. Verify items displayed and KPI card values.<br>3. Adjust slider to 20%. | Displays top 600 items at 10% (capturing ~33% breaks). Re-indexes to 1,200 items at 20% (capturing ~52% breaks). | Cards update instantly: 600 items / 157 breaks captured at 10%. | **PASS** |
| **UAT-03** | Sub-Dollar Auto-Clear Identification | Break with `abs_diff = $0.42` present | 1. Query break in inspection console.<br>2. Inspect priority and recommendation. | Tagged as `LOW / AUTO-CLEAR`. Suggests automated clearing to GL rounding account per Policy 402. | Correctly classified as `rounding_fx` with auto-clear recommendation. | **PASS** |
| **UAT-04** | Stale Mapping Table Escalation | Item with `mapping_version_age_days = 145` | 1. Inspect transaction in queue.<br>2. Check feature breakdown and recommended action. | Displays `mapping_stale_flag = 1`. Generates recommendation: "Submit Chart-of-Accounts rule refresh ticket". | Triggers mapping stale alert and MDM remediation action. | **PASS** |
| **UAT-05** | Duplicate Transaction Critical Priority | Item with `vendor_dup_flag = 1` | 1. Filter queue for duplicate flag.<br>2. Inspect priority assignment. | Priority assigned as `CRITICAL`. Recommends voucher quarantine and disbursement hold. | Flagged as `CRITICAL` priority. Action blocks duplicate disbursement. | **PASS** |
| **UAT-06** | Pre-Close Leakage Prevention | Pipeline execution in test mode | 1. Run automated leakage firewall check (`test_feature_engineering.py`). | Asserts `abs_diff` and `pct_diff` absent from feature design matrix $X$. Pipeline aborts if violated. | Firewall asserts clean separation. Check passes with zero leakage. | **PASS** |
| **UAT-07** | Intercompany Category Neutrality | Clean automated intercompany item | 1. Score intercompany item with fresh mapping.<br>2. Inspect predicted probability. | Category alone does not push score above 0.35 threshold (expected ~0.23-0.25). | Model score = 0.25. Transaction remains below review threshold. | **PASS** |
| **UAT-08** | Analyst Override & Audit Logging | Queue item selected in console | 1. Select transaction.<br>2. Change disposition to `DISMISS (FALSE ALARM)`.<br>3. Input analyst ID and rationale.<br>4. Click Submit. | Disposition logged to immutable audit ledger with timestamp and analyst metadata. Confirmation banner displayed. | Audit log successfully updated with timestamp and analyst ID. | **PASS** |
| **UAT-09** | Multi-Entity Cohort Filtering | Multi-entity dataset loaded | 1. Deselect all entities except `Settlement`.<br>2. Verify queue updates. | Queue displays only transactions where `entity == 'Settlement'`. KPI cards re-aggregate for cohort. | Queue successfully filtered to Settlement transactions only. | **PASS** |
| **UAT-10** | CSV Export of Prioritized Queue | Review queue filtered to Top 10% | 1. Click "Export Reviewed Queue (CSV)".<br>2. Open downloaded file. | Valid CSV containing all queue columns and formatted scores downloaded. | CSV exported with full 11 columns matching table view. | **PASS** |

---

### 3. Sign-Off & Acceptance Authority
- **Business Acceptance Lead:** Finance Transformation Director, DTCC CFO Organization
- **Operational Lead:** Manager of Reconciliation Operations, Jersey City
- **Model Governance Lead:** Model Risk Officer, Model Risk Management Committee
