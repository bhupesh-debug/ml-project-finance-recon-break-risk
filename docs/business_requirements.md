# Business Requirements Document (BRD)
## Project: Pre-Close Reconciliation Break-Risk Scorer and Root-Cause Triage (PoC)
**Target Organization:** DTCC CFO / Finance Operations Organization  
**Author:** Bhupesh Chandra Dimri  
**Date:** October 2026 | **Version:** 1.0 (Production-Ready PoC)

---

### 1. Executive Summary & Problem Statement
During month-end financial close, corporate finance operations teams reconcile millions of General Ledger (GL) postings against upstream operational and banking feeds (Billing, Payroll, Treasury, Clearing). Historically, reconciliation breaks (discrepancies) are discovered *after* close begins, causing intense manual investigation spikes, overtime costs, late reporting adjustments, and heightened audit risk. 

This project delivers a pre-close machine learning and decision-support pipeline that:
1. Predicts break risk prior to financial close using attributes known at transaction posting time.
2. Prioritizes the daily review queue by predicted break risk, allowing analysts to capture >33% of all breaks by inspecting only the top 10% of items (a 3.3x+ lift over random inspection).
3. Classifies identified breaks into five root causes with an automated policy-clearing tier for sub-$1.00 rounding differences.
4. Establishes a governed audit trail with human-in-the-loop oversight compliant with SOX 404 and SR 11-7 standards.

---

### 2. Business Objectives & Key Performance Indicators (KPIs)
- **KPI-1 (Capture at Top 10%):** Capture >= 30% of true reconciliation breaks by reviewing no more than 10% of daily transaction volume.
- **KPI-2 (Labor Optimization):** Reduce manual investigation time by >= 1.5 hours per pre-identified break.
- **KPI-3 (Root Cause Triage Accuracy):** Achieve >= 0.75 Macro-F1 across 5 root cause categories (`rounding_fx`, `mapping_error`, `timing`, `missing_feed`, `duplicate`).
- **KPI-4 (Auto-Clearing Efficiency):** Safely auto-clear 100% of sub-$1.00 rounding variances under pre-approved financial policy.
- **KPI-5 (Audit & Governance Compliance):** 100% immutable logging of analyst dispositions and model override rationales.

---

### 3. User Stories & Acceptance Criteria

#### US-01: Risk-Ranked Daily Review Queue
- **As a** Finance Reconciliation Analyst,
- **I want** the system to sort pending reconciliation transactions each morning by their predicted break risk probability,
- **So that** I can direct my limited daily review capacity (e.g., top 10%) toward the items most likely to fail close.
- **Acceptance Criteria:**
  - Given a scored batch of transactions, items must be ranked strictly descending by predicted break probability (`risk_score`).
  - Filtering by Legal Entity, Account Category, and Review Priority must be supported.
  - Review queue response time must be under 1.5 seconds.
- **Test Evidence:** `src/dashboard.py` Tab 1 Review Queue; `tests/test_feature_engineering.py`.

#### US-02: Sub-Dollar Auto-Clearing Tier
- **As a** Finance Controller,
- **I want** reconciliation differences strictly under $1.00 (`abs_diff < 1.00`) classified as `rounding_fx` to be automatically routed to an auto-clearing queue,
- **So that** my team does not spend human labor investigating immaterial rounding fractions.
- **Acceptance Criteria:**
  - Items with `abs_diff < 1.00` must be tagged as `LOW / AUTO-CLEAR`.
  - System must generate an automated journal voucher record with timestamp and rule ID.
  - No item >= $1.00 may be auto-cleared.
- **Test Evidence:** `src/triage_engine.py` auto-clear logic; `reports/triage_engine_report.md`.

#### US-03: Upstream Stale Mapping SLA Alert
- **As a** Financial Master Data Steward,
- **I want** transactions using Chart-of-Accounts (COA) mapping versions older than 90 days flagged with a `mapping_stale_flag`,
- **So that** we can proactively recertify mapping rules before they trigger bulk reconciliation breaks.
- **Acceptance Criteria:**
  - Mapping age must be calculated as `current_date - mapping_version_timestamp`.
  - Any item with `mapping_version_age_days > 90` must receive risk inflation and a remedial ticket prompt.
- **Test Evidence:** `src/feature_engineering.py` mapping flags; Scenario F simulation.

#### US-04: Duplicate Transaction Quarantine
- **As an** Accounts Payable & Treasury Supervisor,
- **I want** transactions matching identical vendor IDs and monetary amounts within a trailing 7-day window flagged as `CRITICAL`,
- **So that** duplicate payment disbursements can be blocked prior to bank settlement.
- **Acceptance Criteria:**
  - `vendor_dup_flag == 1` items must trigger `CRITICAL` review priority regardless of account category.
  - Recommended action must instruct voucher quarantine and disbursement block.
- **Test Evidence:** `src/triage_engine.py`; `src/simulation.py` Worst-Case Scenario B.

#### US-05: Plain-English AI-Assisted Triage Explanations
- **As a** Senior Reconciliation Analyst,
- **I want** each flagged transaction to display a plain-English explanation detailing *why* it was flagged,
- **So that** I understand the risk drivers without needing to interpret raw statistical coefficients.
- **Acceptance Criteria:**
  - The explanation must cite at least two concrete observable features (e.g., mapping age, close proximity, manual entry).
  - Triage suggestions must include an explicit next action and assigned team owner.
- **Test Evidence:** `src/triage_engine.py` rule-based triage output; Streamlit inspection console.

#### US-06: Human-in-the-Loop Audit Disposition Logging
- **As an** Internal Controls & SOX Compliance Officer,
- **I want** every analyst decision (Confirm, Dismiss, Reclassify, Auto-Clear) captured in an immutable audit ledger,
- **So that** model usage adheres to SOX 404 internal reporting controls and Model Risk Management standards.
- **Acceptance Criteria:**
  - Log schema must record `[transaction_id, analyst_id, disposition, timestamp, override_flag, rationale]`.
  - Records must be append-only and queryable for regulatory audit.
- **Test Evidence:** `src/triage_engine.py` audit log schema; `reports/triage_audit_log_sample.json`.

#### US-07: Pre-Close Data Leakage Prevention Firewall
- **As a** Model Risk Officer (SR 11-7),
- **I want** strict programmatic quarantine of post-reconciliation discrepancy amounts (`abs_diff`, `pct_diff`) from the pre-close risk model,
- **So that** the model does not suffer from circular data leakage.
- **Acceptance Criteria:**
  - Automated unit test must assert that `abs_diff`, `pct_diff`, and `break_type` are absent from `X_train` and `X_test` in Problem 1.
- **Test Evidence:** `src/data_validation.py` check 12; `tests/test_feature_engineering.py`.

#### US-08: Time-Based Chronological Holdout Validation
- **As a** Quantitative Risk Analyst,
- **I want** model training and testing evaluated strictly on a chronological time-split (first 80% train, last 20% test),
- **So that** model performance reflects real-world forward-looking out-of-sample deployment.
- **Acceptance Criteria:**
  - Max training date must precede Min test date.
  - Zero random shuffling across temporal boundaries.
- **Test Evidence:** `src/feature_engineering.py` split logic; `reports/model_evaluation_report.md`.

#### US-09: Model Explainability & Controller Auditability
- **As a** Chief Accounting Officer,
- **I want** the primary production model to be fully explainable with verifiable odds ratios and standard errors,
- **So that** external auditors and regulators can inspect and validate the scoring mechanism.
- **Acceptance Criteria:**
  - Logistic regression must serve as the primary explainable baseline.
  - Non-linear ensemble models (Random Forest, Gradient Boosting) must only be recommended if they beat the explainable baseline by a statistically significant margin (>0.05 PR-AUC).
- **Test Evidence:** `src/regression_analysis.py`; `reports/regression_results.md`.

#### US-10: Executive KPI & Capacity Sensitivity Dashboard
- **As a** Finance Transformation Director,
- **I want** an interactive executive dashboard displaying break capture rates across 5%, 10%, 15%, 20%, and 30% review capacities,
- **So that** Finance Leadership can dynamically allocate analyst staffing during close cycles.
- **Acceptance Criteria:**
  - Dynamic capacity slider updating items reviewed, true breaks captured, precision, and lift in real time.
- **Test Evidence:** `src/dashboard.py` sidebar slider; `reports/simulation_results.md`.

---

### 4. Prioritized Product Backlog
| ID | User Story Title | Business Value | Risk Reduction | Implementation Effort | Sprint / Phase |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **US-01** | Risk-Ranked Review Queue | Critical | High | Medium | Phase 1 (Core) |
| **US-07** | Pre-Close Leakage Firewall | Critical | Extreme | Low | Phase 1 (Core) |
| **US-08** | Chronological Holdout Split | Critical | High | Low | Phase 1 (Core) |
| **US-09** | Model Explainability (Logit) | Critical | High | Medium | Phase 1 (Core) |
| **US-02** | Sub-Dollar Auto-Clearing | High | Medium | Low | Phase 2 |
| **US-03** | Stale Mapping SLA Alerts | High | High | Low | Phase 2 |
| **US-04** | Duplicate Quarantine | High | High | Low | Phase 2 |
| **US-05** | Plain-English AI Triage | High | Medium | Medium | Phase 2 |
| **US-06** | Human-in-the-Loop Audit Log | High | Extreme | Low | Phase 3 (Governance) |
| **US-10** | Executive KPI Dashboard | Medium | Medium | Medium | Phase 3 (Delivery) |
