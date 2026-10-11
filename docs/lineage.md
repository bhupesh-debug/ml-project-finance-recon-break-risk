# End-to-End Data Lineage & Pipeline Architecture
## Reconciliation Break-Risk Scorer and Root-Cause Triage
**Target Organization:** DTCC CFO / Financial Technology Architecture  
**Standards:** BCBS 239 Data Lineage Governance & Auditability  
**Author:** Bhupesh Chandra Dimri | October 2026

---

### 1. Visual Pipeline Flowchart

```mermaid
flowchart TD
    subgraph S1["1. Source Transaction Systems"]
        A1["ERP Sub-Ledger (Oracle Fusion)"]
        A2["Billing Feeds (Clearing / Depository)"]
        A3["Payroll Feeds (Workday / ADP)"]
        A4["Treasury Cash Management"]
    end

    subgraph S2["2. Ingestion & Quality Validation"]
        B1["DuckDB Ingestion Layer"]
        B2["12 CDE Schema Validation Rules"]
        B3["Data Quality Audit Log"]
    end

    subgraph S3["3. Feature Store & Quarantine Firewall"]
        C1["Pre-Close Features (Parquet)"]
        C2["Engineered Features (Top 5 Drivers)"]
        C3["Post-Recon Quarantine Firewall (abs_diff, pct_diff)"]
    end

    subgraph S4["4. Model Inference & Risk Scoring"]
        D1["Logistic Regression Scorer (best_model.pkl)"]
        D2["Review Capacity Thresholding (Top 10%)"]
        D3["Root-Cause Classifier (5 Categories)"]
    end

    subgraph S5["5. Actionable Review & Triage Delivery"]
        E1["Interactive Streamlit Review Queue"]
        E2["Deterministic Rule Triage Engine"]
        E3["Executive Power BI / Tableau KPI View"]
    end

    subgraph S6["6. Governed Feedback & Audit Ledger"]
        F1["Analyst Disposition Form (Confirm/Dismiss)"]
        F2["Immutable Audit Table (SOX 404)"]
        F3["Continuous Model & Feature Drift Monitoring"]
    end

    A1 --> B1
    A2 --> B1
    A3 --> B1
    A4 --> B1
    B1 --> B2
    B2 --> B3
    B2 --> C1
    C1 --> C2
    C1 -. Quarantined .-> C3
    C2 --> D1
    D1 --> D2
    D2 --> E1
    C3 --> D3
    D3 --> E2
    E1 --> E2
    E2 --> E3
    E1 --> F1
    F1 --> F2
    F2 --> F3
    F3 -. Retraining Signal .-> D1
```

---

### 2. Lineage Transformation Stages

#### Stage 1: Source Ingestion
- **Extracts:** Daily incremental journal files extracted from ERP, Billing, Payroll, and Treasury systems.
- **Protocol:** Nightly batch SFTP / Kafka ingestion into raw staging directory.
- **Audit Verification:** Hash sum verification and record counts checked against source transmission manifests.

#### Stage 2: Schema & CDE Validation
- **Engine:** Python / DuckDB SQL.
- **Rules:** 12 CDE integrity checks: non-null transaction IDs, valid date sequences, entity taxonomy validation, positive monetary values, and lag boundaries.
- **Exception Routing:** Malformed records routed to dead-letter quarantine table with alerts issued to IT Operations.

#### Stage 3: Feature Engineering & Pre-Close Firewall
- **Storage:** Snappy-compressed Apache Parquet feature store.
- **Top 5 Transformations:**
  1. `is_close_window`: Boolean indicator for `days_to_period_end <= 3`.
  2. `close_manual_interaction`: Interaction term crossing close window with manual journal flag.
  3. `mapping_stale_flag`: Indicator for `mapping_version_age_days > 90`.
  4. `posting_lag_ratio`: Transaction posting lag divided by historical source system median lag.
  5. `log_amount_gl`: Natural logarithm of monetary balance (`log1p`).
- **Firewall:** Strict physical isolation of post-reconciliation discrepancy attributes (`abs_diff`, `pct_diff`) preventing circular leakage into Problem 1.

#### Stage 4: Scoring & Multi-Class Classification
- **Batch Frequency:** Nightly batch inference (executed at 02:00 EST).
- **Execution:** Vectorized Scikit-Learn pipeline scoring 100% of pending items in < 5 seconds.
- **Outputs:** Probability score (`risk_score` $\in [0, 1]$), review priority tier (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`), and predicted root cause.

#### Stage 5: Delivery & Analyst Workflow
- **Interfaces:** Streamlit operational queue for reconciliation analysts; Power BI summary dashboard for Controllers.
- **Triage Action:** Rule-based deterministic explanation engine generating plain-English root cause summary and remedial recommendation.

#### Stage 6: Feedback Loop & Model Governance
- **Audit Logging:** Every analyst action (`Confirm Break`, `Dismiss False Alarm`, `Reclassify Cause`, `Auto-Clear Approved`) is persisted with analyst ID and timestamp.
- **Retraining Cycle:** Monthly rolling-origin model recalibration incorporating verified analyst ground truth.
- **Drift Detection:** Kolmogorov-Smirnov statistical tests executed weekly to identify feature drift in mapping age and posting lag distributions.
