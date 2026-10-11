# Questions & Answers Register (Q&A Register)
## Reconciliation Break-Risk Scoring and Root-Cause Triage
**Project:** DTCC Finance Analytics & Innovation Associate Proof of Concept  
**Author:** Bhupesh Chandra Dimri | October 2026

---

### Section 1: Twelve Core Analytical Questions (Phase 1 & Phase 12)

#### Q-01: Which factors are associated with higher reconciliation-break risk?
- **Answer:** The primary statistical risk drivers in order of empirical impact are:
  1. `mapping_version_age_days`: Stale account-mapping tables (>90 days old) are the strongest predictor (drop in PR-AUC of ~0.12 when shuffled; odds ratio > 2.8x).
  2. `vendor_dup_flag`: Identical vendor identifier and monetary amount within 7 days (odds ratio ~ 3.8x, p < 0.001).
  3. `is_manual_entry`: Manual journals carry more than double the break odds of automated straight-through feeds (odds ratio ~ 2.2x).
  4. `close_manual_interaction`: Transactions booked manually within 3 days of period close carry an amplified interaction risk penalty.
  5. `posting_lag_ratio`: Posting lags exceeding the source system's operational median norm.
- **Evidence:** `reports/regression_results.md`, `figures/permutation_feature_importance.png`.
- **Business Implication:** Break risk is primarily driven by upstream master data staleness and manual intervention rather than transaction dollar size.

#### Q-02: Can regression and classification models predict breaks before financial close?
- **Answer:** Yes. Evaluated strictly on pre-close attributes without post-reconciliation leakage, binary classification models achieve a PR-AUC of 0.251 on a 7.88% imbalanced class (a 3.18x lift over the random baseline of 0.079) and an ROC-AUC of 0.747.
- **Evidence:** `reports/model_evaluation_report.md`, `src/model_training.py`.
- **Business Implication:** Operations teams can identify at-risk items 24-72 hours before reconciliation cutoff, shifting workload from fire-fighting during close to preventive triage before close.

#### Q-03: Which model performs best against the existing analyst heuristic?
- **Answer:** Both Logistic Regression and Random Forest substantially outperform the 3-rule analyst heuristic:
  - Logistic Regression achieves 0.251 PR-AUC and captures 33.2% of all breaks in the top 10% volume.
  - Analyst Heuristic achieves 0.179 PR-AUC and captures only 21.8% of breaks in the top 10% volume.
- **Evidence:** `figures/model_comparison_holdout.png`, `reports/model_evaluation_report.md`.
- **Business Implication:** The machine learning model captures 1.52x more breaks (+54 additional breaks per 6,000 items) than the heuristic using the exact same analyst review hours.

#### Q-04: Does a more complex model outperform logistic regression by a meaningful amount?
- **Answer:** No. Gradient Boosting achieved 0.208 PR-AUC (29.4% top-10% capture) and Random Forest achieved 0.237 PR-AUC (30.7% top-10% capture), compared to Logistic Regression at 0.251 PR-AUC (33.2% top-10% capture).
- **Evidence:** Out-of-sample holdout test on N=6,000 items (473 true breaks, standard error +/- 3.5%).
- **Business Implication:** In a regulated financial market infrastructure (SR 11-7 / SOX 404), an explainable, auditable Logistic Regression model is strictly preferred over complex ensembles because non-linear models do not provide a statistically meaningful performance advantage.

#### Q-05: How many breaks can analysts identify when reviewing only the highest-risk 10% of items?
- **Answer:** In the 6,000 holdout test set (containing 473 true breaks), reviewing the top 600 items (10% capacity) captures **157 true breaks (33.2% recall)** with a precision of **26.2%** and a **3.32x lift** over random queue sampling.
- **Evidence:** `reports/model_evaluation_report.md` Section 3.
- **Business Implication:** Concentrating review on the top decile allows Finance Operations to capture one-third of all month-end problems while bypassing 90% of clean straight-through volume.

#### Q-06: Which root causes can be classified reliably?
- **Answer:** 
  - `rounding_fx` is classified with exceptional precision (F1 = 1.00; precision 1.00, recall 1.00) because discrepancies strictly under $1.00 separate cleanly.
  - `duplicate` is classified with high fidelity (F1 = 0.97; precision 0.94, recall 1.00) via full-amount variance and vendor duplicate signatures.
  - `mapping_error` achieves solid classification (F1 = 0.76; precision 0.89, recall 0.66).
  - `timing` (F1 = 0.60) and `missing_feed` (F1 = 0.57) exhibit moderate confusion due to overlapping full-amount variances and lag patterns.
- **Evidence:** `reports/root_cause_report.md`, `figures/root_cause_confusion_matrix.png`.
- **Business Implication:** Rounding and duplicate categories are highly reliable candidates for automated workflow routing.

#### Q-07: Which reconciliation categories require human investigation versus controlled automatic clearing?
- **Answer:**
  - **Controlled Automatic Clearing:** Sub-$1.00 `rounding_fx` discrepancies ($abs\_diff < \$1.00$). Finance Policy 402 permits automated clearance to GL rounding variance accounts, safely eliminating 15-20% of queue volume.
  - **Mandatory Human Investigation:** `duplicate` disbursements, `missing_feed` batch omissions, and `mapping_error` re-assignments. These carry material dollar exposure and legal balance sheet implications requiring controller sign-off.
- **Evidence:** `src/triage_engine.py`, `docs/governance_controls.md`.
- **Business Implication:** Segmenting by root-cause dollar materiality frees significant analyst capacity while tightening internal controls over material risks.

#### Q-08: What is the business impact of refreshing stale mapping tables?
- **Answer:** In Scenario F simulation, enforcing a mandatory 60-day Chart-of-Accounts mapping refresh SLA reduced systemic predicted break risk across the portfolio by **46.7%** and prevented hundreds of transactions from escalating into the review queue.
- **Evidence:** `reports/simulation_results.md` Section 2.
- **Business Implication:** Upstream master data governance prevents more breaks than downstream reconciliation detection can ever resolve.

#### Q-09: What data-quality and governance controls are necessary?
- **Answer:**
  1. Ingestion schema validation across 12 Critical Data Elements (CDEs).
  2. Strict architectural quarantine preventing post-reconciliation discrepancy fields from leaking into pre-close features.
  3. Immutable write-once audit logging capturing analyst ID, timestamp, and override rationale for every disposition.
  4. Weekly Kolmogorov-Smirnov drift monitoring on feature distributions.
- **Evidence:** `docs/governance_controls.md`, `reports/data_quality_report.md`.
- **Business Implication:** Adherence to BCBS 239 and SOX 404 ensures the proof of concept satisfies financial market infrastructure audit standards.

#### Q-10: What is the best model for an explainable, controlled Finance environment?
- **Answer:** Regularized Binary Logistic Regression (`best_model.pkl`). It provides exact coefficient interpretability, transparent odds ratios, well-behaved calibration (Brier score 0.207), zero unexplainable interactions, and full parity with complex algorithms.
- **Evidence:** `docs/model_card.md`, `reports/regression_results.md`.
- **Business Implication:** Controllers and internal auditors can inspect and defend the model in regulatory examinations.

#### Q-11: How should the solution be deployed, monitored, and improved?
- **Answer:** 
  - **Deployment:** Nightly batch inference pipeline in Python/DuckDB scoring pending GL transactions and publishing to a Streamlit review queue.
  - **Monitoring:** Automated tracking of queue precision, recall at top-10%, analyst override frequency (>20% threshold alert), and feature drift.
  - **Improvement:** Monthly rolling-origin retraining incorporating verified analyst dispositions into ground-truth training sets.
- **Evidence:** `docs/lineage.md`, `src/dashboard.py`.
- **Business Implication:** Continuous feedback ensures the model adapts to changing accounting policies and seasonal close patterns.

#### Q-12: What additional evidence would be required before production deployment?
- **Answer:**
  1. Four-week parallel shadow pilot on live, non-synthetic DTCC General Ledger data.
  2. Formal Model Risk Management Committee (MRMC) sign-off under SR 11-7 standards.
  3. Verification that live upstream ERP and Billing pipelines deliver timestamps without latency or missing feeds.
  4. User Acceptance Testing sign-off from Reconciliation Operations leads across Jersey City and New York sites.
- **Evidence:** `docs/uat_test_cases.md`, `slides/project_deck.pptx` Slide 12.
- **Business Implication:** Mitigates operational risk before cutover to production operational queues.

---

### Section 2: Five Strategic Questions for DTCC Stakeholders & Hiring Managers

*(Formulated from the perspective of an incoming Finance Analytics & Innovation Associate to evaluate organizational readiness and strategic alignment)*

#### Candidate Question 1: Governed Asset Scope & Baseline Data Quality
- **Recommended Candidate Wording:** *"Which financial reporting cycles and Critical Data Elements (CDEs) are currently prioritized in scope for the CFO organization's governed-asset program, and what baseline data-quality frameworks are active today in the Enterprise Data Catalog?"*
- **Why It Matters:** Demonstrates understanding that analytics proofs of concept cannot scale without formal data ownership and CDE governance. Establishes the candidate's immediate project entry point.

#### Candidate Question 2: Finance-Technology Backlog Sharing & Agile Structure
- **Recommended Candidate Wording:** *"How do Finance Operations and Finance Technology collaborate on backlog prioritization—would the Associate sit within a joint Agile scrum team with dedicated sprint cycles for analytics and automation pilots?"*
- **Why It Matters:** Clarifies delivery velocity and organizational structure. Demonstrates fluency in Agile business analysis, sprint ceremonies, and cross-functional stakeholder management.

#### Candidate Question 3: Enterprise AI Guardrails & Proof-of-Concept Graduation
- **Recommended Candidate Wording:** *"What specific model governance and data classification guardrails apply to AI and LLM proofs of concept within DTCC's regulated perimeter, and what criteria determine whether an innovation pilot graduates into production?"*
- **Why It Matters:** Signals acute awareness of DTCC's systemic market infrastructure status, risk management culture, and the practical distinction between prototype experimentation and production readiness.

#### Candidate Question 4: Enterprise BI & Data Warehouse Platform Standardization
- **Recommended Candidate Wording:** *"As DTCC continues its data modernizations, what is the target architecture between Oracle Analytics Cloud / ADW and Snowflake / Power BI for executive reporting, and how should future analytics assets bridge across both stacks?"*
- **Why It Matters:** Directly addresses the dual tooling named in the job description (OAC/ADW vs Power BI/Snowflake). Shows architectural foresight and adaptability.

#### Candidate Question 5: Adoption Metrics & 6-Month Success Criteria
- **Recommended Candidate Wording:** *"How does the CFO leadership team measure adoption and business impact for new analytics assets, and what would a wildly successful outcome look like for this role after the first six months?"*
- **Why It Matters:** Aligns the candidate's personal performance KPIs with executive business value: dashboard adoption, hours automated, and governed reporting graduation.
