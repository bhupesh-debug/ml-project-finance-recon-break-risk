# Model Card: Reconciliation Break-Risk Scorer (SR 11-7 Compliant)
## Production Candidate: Logistic Regression Binary Classifier (`best_model.pkl`)
**Target Organization:** DTCC CFO Organization / Model Risk Management (MRM)  
**Governance Framework:** Federal Reserve SR 11-7 / OCC Bulletin 2011-12 & SOX 404  
**Author:** Bhupesh Chandra Dimri | **Date:** October 2026 | **Version:** 1.0

---

### 1. Model Overview & Purpose
- **Model Name:** Pre-Close Reconciliation Break-Risk Scorer
- **Model Type:** L2-Regularized Binary Logistic Regression with Preprocessing Pipeline
- **Primary Objective:** Estimate the conditional probability $P(Y=1 | X)$ that an unclosed general ledger transaction will result in an unreconciled break during month-end close.
- **Decision Context:** Prioritize limited daily analyst review capacity toward the highest-risk items, capturing >= 30% of breaks by inspecting the top 10% of items.
- **Release Version:** 1.0 (Proof of Concept graduating to Controlled Pilot)

---

### 2. Intended Use & Scope
- **Primary Intended Use:** Automated risk scoring and prioritization of pending General Ledger transactions across 5 DTCC operating entities (`Corp`, `Settlement`, `Clearing`, `Data Svcs`, `Intl`).
- **Target User:** Financial Operations Reconciliation Analysts, Accounting Managers, and Controllers.
- **Out-of-Scope / Prohibited Uses:**
  - Cannot be used for automated journal blocking without human review.
  - Cannot be used for external financial reporting adjustments without controller sign-off.
  - Cannot ingest post-reconciliation difference amounts at scoring time (strict leakage restriction).

---

### 3. Quantitative Performance & Validation

Evaluated on an out-of-sample chronological holdout dataset of 6,000 transactions (last 20% of timeline, 473 true breaks, 7.88% prevalence):

| Metric | Logistic Regression | Challenger: Random Forest | Challenger: Gradient Boosting | Analyst Heuristic (3 Rules) | Benchmark Target |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **PR-AUC (Primary)** | **0.251** | 0.237 | 0.208 | 0.179 | **~0.26** |
| **ROC-AUC** | **0.747** | 0.746 | 0.731 | 0.711 | **~0.75** |
| **Capture at Top 10%** | **33.2%** (157 / 473) | 30.7% (145 / 473) | 29.4% (139 / 473) | 21.8% (103 / 473) | **~36%** |
| **Capture at Top 20%** | **52.6%** (249 / 473) | 49.3% (233 / 473) | 48.0% (227 / 473) | 38.5% (182 / 473) | **~50%** |
| **Precision at Top 10%**| **26.2%** | 24.2% | 23.2% | 17.2% | **~26%** |
| **Lift at Top 10%** | **3.32x** | 3.07x | 2.94x | 2.18x | **~3.6x** |
| **Brier Calibration Score** | 0.207 | 0.203 | 0.196 | 0.129 | < 0.25 |

#### Reconciling Model Choice
Logistic Regression is selected as the primary production model over tree-based ensembles because:
1. **Statistical Equivalence:** Non-linear models do not exhibit statistically meaningful performance gains over Logistic Regression (PR-AUC 0.251 vs 0.208-0.237).
2. **Auditability & Explainability:** Regulators (Federal Reserve, SEC) and financial auditors require exact odds ratio derivations and parameter significance testing (all p < 0.001 for key drivers).
3. **Execution Portability:** Scored via standard vector arithmetic in SQL/DuckDB, removing heavyweight C++ library dependencies in regulated production enclaves.

---

### 4. Input Features & Preprocessing Pipeline
- **Numerical Scaled Predictors:** `mapping_version_age_days`, `posting_lag_days`, `days_to_period_end`, `prior_breaks_30d`, `amount_gl`, `log_amount_gl`, `posting_lag_ratio`.
- **Engineered Binary Indicators:** `is_manual_entry`, `vendor_dup_flag`, `is_close_window`, `close_manual_interaction`, `mapping_stale_flag`, `mapping_very_stale_flag`, `high_prior_breaks_flag`.
- **Categoricals (One-Hot Encoded with First Dropped):** `entity`, `account_cat`, `source_system`.
- **Scaling:** `StandardScaler` fitted strictly on chronological training records (preventing train-test contamination).

---

### 5. Key Risk Drivers & Odds Ratios (Econometric Interpretation)
1. **`mapping_version_age_days` (Top Risk Driver):** Drop in PR-AUC of ~0.12 when shuffled. Mapping versions > 90 days show odds ratio inflation > 2.8x.
2. **`vendor_dup_flag`:** Odds ratio ~ 3.8x. Elevates break risk substantially; indicative of double billing or improper manual re-keying.
3. **`is_manual_entry`:** Odds ratio ~ 2.2x. Confirms that human manual adjustments carry more than double the break odds of automated feeds.
4. **`close_manual_interaction`:** Interaction term capturing compound risk when manual entries occur within 3 days of period close.

---

### 6. Limitations, Assumptions & Known Biases
- **Synthetic Data Generation Bias:** Synthetic training data encodes specific logistic and interaction relationships. Model weights must be recalibrated when retraining on real production GL data.
- **Concept Drift at Year-End Close:** Month-end close dynamics may differ from annual close cycles (Q4 close) where manual adjustments spike.
- **Unobservable Feed Outages:** Total source-system feed failures without journal entries cannot be predicted pre-close by definition. Post-recon batch count validation controls remain essential.

---

### 7. Governance, Monitoring & Incident Escalation
- **Drift Monitoring:** Weekly Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) tests on feature distributions.
- **Retraining Trigger:** Recalibration triggered if PR-AUC drops below 0.20 or top-10% capture drops below 25% for two consecutive close cycles.
- **Model Owner:** Principal Finance Analytics & ML Architect.
- **Reviewing Authority:** DTCC Model Risk Management Committee (MRMC).
