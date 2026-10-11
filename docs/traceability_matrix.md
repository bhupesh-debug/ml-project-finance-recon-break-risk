# Requirements Traceability Matrix (RTM)
## Project: Reconciliation Break-Risk Scorer and Root-Cause Triage
**Target Organization:** DTCC CFO Organization  
**Author:** Bhupesh Chandra Dimri | October 2026

---

### End-to-End Requirement-to-Evidence Traceability Matrix

| Req ID | Requirement Description | Phase / Category | Implementation Module | Evidence & Validation Artifact | Test Reference | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **REQ-01** | Pre-close break risk scoring (`is_break`) | P1: Machine Learning | `src/model_training.py` | `models/best_model.pkl`, `reports/model_evaluation_report.md` | `test_models.py` | **COMPLETE** |
| **REQ-02** | Root-cause classification (5 categories) | P2: Machine Learning | `src/root_cause_classifier.py` | `models/root_cause_classifier.joblib`, `reports/root_cause_report.md` | `test_models.py` | **COMPLETE** |
| **REQ-03** | AI-assisted triage with plain-English explanation | P3: Decision Support | `src/triage_engine.py` | `reports/triage_engine_report.md`, `reports/triage_audit_log_sample.json` | `test_governance.py` | **COMPLETE** |
| **REQ-04** | Chronological 80/20 time-based holdout split | Data Pipeline | `src/feature_engineering.py` | `data/processed/train.parquet`, `data/processed/test.parquet` | `test_feature_engineering.py` | **COMPLETE** |
| **REQ-05** | Pre-close leakage prevention firewall | Governance / Data | `src/data_validation.py` | `reports/data_quality_report.md` (Check 12) | `test_data_generator.py` | **COMPLETE** |
| **REQ-06** | Top 5 domain-engineered features | Feature Engineering | `src/feature_engineering.py` | `data/processed/feature_metadata.json` | `test_feature_engineering.py` | **COMPLETE** |
| **REQ-07** | Econometric Logistic Regression with Odds Ratios | Phase 4: Regression | `src/regression_analysis.py` | `reports/regression_results.md`, `reports/regression_coefficients.csv` | `test_models.py` | **COMPLETE** |
| **REQ-08** | Continuous OLS investigation effort modeling | Phase 4: Regression | `src/regression_analysis.py` | `reports/regression_results.md` (Section 2) | Script execution | **COMPLETE** |
| **REQ-09** | Reconcile PDF benchmark claims (PR-AUC, Capture) | Phase 6: Model Validation | `src/model_training.py` | `figures/model_comparison_holdout.png`, `reports/model_evaluation_report.md` | Script execution | **COMPLETE** |
| **REQ-10** | Permutation Feature Importance ranking | Phase 6: Explainability | `src/model_training.py` | `figures/permutation_feature_importance.png` | Script execution | **COMPLETE** |
| **REQ-11** | Transaction Scenario Simulations (A to D) | Phase 5: Simulation | `src/simulation.py` | `figures/scenario_simulation_scores.png`, `reports/simulation_results.md` | Script execution | **COMPLETE** |
| **REQ-12** | Mapping Refresh Intervention (Scenario F) | Phase 5: Simulation | `src/simulation.py` | `reports/simulation_results.md` (Section 2) | Script execution | **COMPLETE** |
| **REQ-13** | Review Capacity Stress Test (Scenario G) | Phase 5: Simulation | `src/model_training.py` | `reports/model_evaluation_report.md` (Section 3) | Script execution | **COMPLETE** |
| **REQ-14** | Monte Carlo Sensitivity Analysis (1,000 runs) | Phase 5: Simulation | `src/simulation.py` | `figures/monte_carlo_financial_simulation.png`, `reports/simulation_results.md` | Script execution | **COMPLETE** |
| **REQ-15** | Controller-Grade 3-Scenario Business Case (ROI) | Phase 7: Business Impact | `src/business_case.py` | `reports/financial_impact_table.csv`, `reports/business_case_model.md` | Script execution | **COMPLETE** |
| **REQ-16** | Sub-Dollar Auto-Clearing Rule Tier | Phase 8: Operational Triage | `src/triage_engine.py` | `reports/triage_engine_report.md` | `test_governance.py` | **COMPLETE** |
| **REQ-17** | Interactive Streamlit Review Queue Dashboard | Delivery & Presentation | `src/dashboard.py` | Runnable Streamlit App (`src/dashboard.py`) | Interactive validation | **COMPLETE** |
| **REQ-18** | Comprehensive Data Dictionary & CDE List | Phase 9: Governance | `docs/data_dictionary.md` | `docs/data_dictionary.md` | Inspection | **COMPLETE** |
| **REQ-19** | End-to-End Data Lineage & Architecture Diagram | Phase 9: Governance | `docs/lineage.md` | `docs/lineage.md` (Mermaid diagram) | Inspection | **COMPLETE** |
| **REQ-20** | SR 11-7 Compliant Model Card | Phase 9: Governance | `docs/model_card.md` | `docs/model_card.md` | Inspection | **COMPLETE** |
| **REQ-21** | SOX 404 Internal Controls & Governance Protocol | Phase 9: Governance | `docs/governance_controls.md` | `docs/governance_controls.md` | Inspection | **COMPLETE** |
| **REQ-22** | Business Requirements Document (10 User Stories) | Phase 11: Business Analyst| `docs/business_requirements.md`| `docs/business_requirements.md` | Inspection | **COMPLETE** |
| **REQ-23** | User Acceptance Testing (UAT) Test Plan | Phase 11: Business Analyst| `docs/uat_test_cases.md` | `docs/uat_test_cases.md` (10 test scripts) | Inspection | **COMPLETE** |
| **REQ-24** | Automated Unit Test Suite | Phase 10: Engineering | `tests/` | Pytest test execution logs | Pytest suite | **COMPLETE** |
| **REQ-25** | Executive Presentation Slide Deck (12 Slides) | Phase 13: Presentation | `slides/generate_deck.py` | `slides/project_deck.pptx` | Deck inspection | **COMPLETE** |
