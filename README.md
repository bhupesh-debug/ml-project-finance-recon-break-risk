# Finance Reconciliation Break-Risk Scorer and Root-Cause Triage
### A Governed Machine Learning & AI Proof of Concept for the CFO Organization
**Target Organization:** DTCC CFO Organization / Financial Operations  
**Author:** Bhupesh Chandra Dimri | October 2026  
**Target Role:** Finance Analytics & Innovation Associate (Jersey City, NJ | Job ID 214537)

---

## 📌 Executive Summary
Corporate financial close processes are frequently delayed by late-discovered reconciliation discrepancies ("breaks") between General Ledger (GL) postings and upstream operational feeds. This project delivers an end-to-end, reproducible, controller-grade machine learning solution that:
1. **Predicts break risk pre-close** using attributes known at posting time, strictly preventing post-reconciliation circular data leakage.
2. **Prioritizes analyst review capacity:** Reviewing only the top 10% of items ranked by the model captures **33.2% of all breaks** (a **3.32x lift** over random queue sampling), outperforming today's 3-rule heuristic by 1.52x.
3. **Classifies root causes into 5 categories** (Macro-F1: 0.78), enabling automated policy clearing for sub-$1.00 rounding discrepancies and instant escalation for duplicate disbursements.
4. **Delivers auditable business value:** Base case Year-1 net financial benefit of **$253,400** with a **520% ROI** and a **1.9-month payback period** (confirmed across 1,000 Monte Carlo simulation runs).
5. **Provides institutional governance:** Ships with SR 11-7 model cards, BCBS 239 lineage diagrams, Critical Data Element (CDE) registers, SOX 404 control matrices, and immutable human-in-the-loop audit logs.

> **Key Modeling Finding:** Binary Logistic Regression performed within statistical noise of complex Gradient Boosting (PR-AUC 0.251 vs 0.208). In a regulated CFO environment, an auditable, transparent model that controllers can verify beats an opaque black-box algorithm.

---

## 📁 Repository Structure
```
ml-project-finance-recon-break-risk/
├── README.md                           # Project overview, benchmark results, instructions
├── requirements.txt                    # Exact pinned dependencies
├── .gitignore                          # Git ignore rules
├── data/
│   ├── raw/                            # Reference taxonomy and extracts
│   ├── processed/                      # Feature-engineered train/test Parquet tables
│   │   ├── train.parquet               # First 80% chronological observations (N=24,000)
│   │   ├── test.parquet                # Last 20% chronological holdout (N=6,000)
│   │   └── feature_metadata.json       # Feature definitions and split metadata
│   └── synthetic/                      # Seeded synthetic generator outputs
│       ├── reconciliation_items.parquet # 30,000 generated items (7.23% break rate)
│       ├── reconciliation_items.csv     # CSV export
│       ├── reconciliation.duckdb        # Embedded DuckDB database
│       └── schema.md                   # Column schema specification
├── docs/
│   ├── business_requirements.md        # 1-page BRD + 10 user stories with acceptance criteria
│   ├── data_dictionary.md              # 16 fields, CDE register, ownership, valid ranges
│   ├── lineage.md                      # BCBS 239 Source -> Ingestion -> Score lineage (Mermaid)
│   ├── model_card.md                   # SR 11-7 / OCC 2011-12 compliant Model Card
│   ├── governance_controls.md          # SOX 404 internal controls, override policy, drift rules
│   ├── uat_test_cases.md               # 10 formal User Acceptance Testing (UAT) scripts
│   └── traceability_matrix.md          # Requirement-to-test traceability matrix
├── figures/                            # High-resolution publication figures (300 DPI)
│   ├── class_balance_and_differences.png
│   ├── break_rates_by_operational_drivers.png
│   ├── chronological_break_rate_trend.png
│   ├── model_comparison_holdout.png    # Recreates PDF Page 6 bottom chart
│   ├── permutation_feature_importance.png # Recreates PDF Page 6 top chart
│   ├── logistic_regression_pr_calibration.png
│   ├── root_cause_confusion_matrix.png
│   ├── scenario_simulation_scores.png  # Recreates PDF Page 7 bottom chart
│   └── monte_carlo_financial_simulation.png
├── models/
│   ├── best_model.pkl                  # Production candidate pipeline (Logistic Regression)
│   ├── logistic_regression.joblib      # Serialized Logistic Regression pipeline
│   ├── random_forest.joblib            # Serialized Random Forest pipeline
│   ├── gradient_boosting.joblib        # Serialized Gradient Boosting pipeline
│   └── root_cause_classifier.joblib    # Multi-class 5-category classifier
├── reports/
│   ├── data_quality_report.md          # Ingestion validation & 12 CDE check results
│   ├── regression_results.md           # Econometric Logit, Odds Ratios, CIs, VIF, OLS
│   ├── regression_coefficients.csv     # Exported coefficients table
│   ├── model_evaluation_report.md      # Out-of-sample benchmark comparison & lift tables
│   ├── model_comparison_metrics.json   # Machine-readable evaluation metrics
│   ├── root_cause_report.md            # Multi-class precision, recall, F1-scores
│   ├── triage_engine_report.md         # Rule vs LLM triage benchmark & latency
│   ├── triage_audit_log_sample.json    # Human-in-the-loop audit disposition logs
│   ├── simulation_results.md           # Scenarios A-D, Mapping intervention, Monte Carlo
│   ├── business_case_model.md          # Controller-grade 3-scenario ROI model
│   ├── financial_impact_table.csv      # Exported financial case metrics
│   ├── qa_register.md                  # Complete answers to 12 analytical & 5 DTCC questions
│   └── comprehensive_project_report.md # Full 17-section executive and technical report
├── slides/
│   ├── generate_deck.py                # Python-pptx generator script
│   └── project_deck.pptx               # 12-slide executive presentation
├── src/
│   ├── data_generator.py               # Seeded synthetic generator (seed=42)
│   ├── data_validation.py              # Ingestion CDE validator & leakage firewall
│   ├── feature_engineering.py          # Top 5 engineered features & time-based split
│   ├── eda.py                          # Exploratory data analysis & figure generator
│   ├── regression_analysis.py          # Statsmodels Logit & OLS impact modeling
│   ├── model_training.py               # Candidate model training & benchmark evaluation
│   ├── root_cause_classifier.py        # 5-class root cause classifier
│   ├── triage_engine.py                # Rule-based triage + LLM comparison layer
│   ├── simulation.py                   # Stress testing & Monte Carlo simulations
│   ├── business_case.py                # Financial ROI, 3-yr NPV, sensitivity matrix
│   └── dashboard.py                    # Interactive Streamlit review queue console
└── tests/
    ├── test_data_generator.py          # Unit tests for dataset size, prevalence, nulls
    ├── test_feature_engineering.py     # Unit tests for split order and leakage firewall
    ├── test_models.py                  # Unit tests for model inference and probability bounds
    └── test_governance.py              # Unit tests for triage rules and auto-clearing
```

---

## 📊 Benchmark Results Summary (Holdout Test N=6,000)

| Model | PR-AUC | Top 10% Capture | Top 10% Lift | ROC-AUC | Brier Score | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Logistic Regression** | **0.251** | **33.2%** (157 / 473) | **3.32x** | **0.747** | 0.207 | **Recommended Production Model** |
| **Random Forest** | 0.237 | 30.7% (145 / 473) | 3.07x | 0.746 | 0.203 | Challenger |
| **Gradient Boosting** | 0.208 | 29.4% (139 / 473) | 2.94x | 0.731 | 0.196 | Challenger |
| **Analyst Heuristic (3 Rules)** | 0.179 | 21.8% (103 / 473) | 2.18x | 0.711 | 0.129 | Legacy Baseline |
| **Random Baseline** | 0.079 | 9.7% | 0.97x | 0.505 | 0.331 | Null Reference |

### Root-Cause Classification Results (Holdout Breaks N=473)
- **Rounding / FX:** Precision: 1.00 | Recall: 1.00 | **F1: 1.00** (Eligible for Auto-Clear)
- **Duplicate:** Precision: 0.94 | Recall: 1.00 | **F1: 0.97** (Immediate Disbursement Hold)
- **Mapping Error:** Precision: 0.89 | Recall: 0.66 | **F1: 0.76** (MDM Mapping Change Ticket)
- **Overall Macro-F1:** **0.78** (PDF benchmark target: ~0.81)

---

## 🚀 How to Run & Reproduce

```bash
# 1. Clone or navigate to the repository
cd ml-project-finance-recon-break-risk

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate synthetic data & run quality checks
python src/data_generator.py
python src/data_validation.py

# 4. Run feature engineering (80/20 chronological split)
python src/feature_engineering.py

# 5. Generate visual insight charts
python src/eda.py

# 6. Fit econometric regression & diagnostics
python src/regression_analysis.py

# 7. Train and benchmark candidate models
python src/model_training.py

# 8. Train root-cause multi-class classifier
python src/root_cause_classifier.py

# 9. Execute AI triage engine & LLM benchmark
python src/triage_engine.py

# 10. Run scenario simulations & Monte Carlo
python src/simulation.py

# 11. Run financial business case model
python src/business_case.py

# 12. Run automated test suite (14 passing tests)
python -m pytest -v

# 13. Generate 12-slide executive presentation deck
python slides/generate_deck.py

# 14. Launch interactive review queue dashboard
streamlit run src/dashboard.py
```

---

## 🛡️ Governance & Model Risk Compliance
This project strictly adheres to:
- **Federal Reserve SR 11-7 / OCC Bulletin 2011-12:** Complete Model Card (`docs/model_card.md`), rigorous out-of-sample holdout validation, parameter stability checks, and disclosed limitations.
- **Sarbanes-Oxley (SOX) Section 404:** Automated pre-close leakage firewalls, strict segregation of duties, human-in-the-loop disposition authority, and immutable audit logs.
- **BCBS 239 Data Governance:** Complete Data Dictionary with Critical Data Elements (`docs/data_dictionary.md`) and Source-to-Score lineage (`docs/lineage.md`).

---

## 👤 Author & Contact
**Bhupesh Chandra Dimri**  
Target Role: Finance Analytics & Innovation Associate, DTCC (Job ID 214537)  
Email: [bhupesh7cd@gmail.com](mailto:bhupesh7cd@gmail.com)  
Location: Jersey City, NJ | October 2026
