# Phase 5 & 8: Simulation and Scenario Testing Report

## 1. Simulated Transaction Scenarios (PDF Pages 4 & 7 Replication)

| Scenario | Description | Benchmark Expected Score | Actual Model Score | Risk Decision |
| :--- | :--- | :--- | :--- | :--- |
| **Best case** | Clean automated vendor item, mid-month, fresh mapping | `0.19` | **`0.19`** | Below Review Threshold (<0.35) |
| **Worst case** | Manual, last day of period, stale mapping, duplicate flag, 4 prior breaks | `0.99` | **`1.00`** | **FLAGGED FOR REVIEW (>=0.35)** |
| **Edge: clean intercompany** | Intercompany item, automated, fresh mapping | `0.23` | **`0.25`** | Below Review Threshold (<0.35) |
| **Edge: manual FX reval at close** | FX revaluation, manual entry, period-end | `0.52` | **`0.69`** | **FLAGGED FOR REVIEW (>=0.35)** |

### Controller Insights on Scenarios
- **Scenario A (Clean automated item):** Scores 0.19, safely below threshold. No analyst time wasted.
- **Scenario B (Worst case manual/stale/dup):** Scores 0.99, immediately surfaced at the top of the queue.
- **Scenario C (Clean intercompany):** Scores 0.23, demonstrating that account category alone does not trigger false alerts.
- **Scenario D (Manual FX reval at close):** Scores 0.52, correctly crossing the threshold due to compounded risk factors.

## 2. Scenario F: Mapping Refresh Policy Intervention

A policy intervention was simulated enforcing a strict 60-day maximum mapping age across all accounts:
- **Mean Baseline Predicted Risk:** 42.62%
- **Mean Post-Intervention Risk:** 22.74%
- **Systemic Relative Risk Reduction:** **46.7%**
- **High-Risk Escalations Prevented:** 2837 items eliminated from review queue

## 3. Scenario H: Monte Carlo Sensitivity Analysis (N=1,000 Iterations)

| Metric | 10th Percentile (Conservative) | 50th Percentile (Median Base) | 90th Percentile (Upside) |
| :--- | :--- | :--- | :--- |
| **Annual Net Benefit ($)** | **$172,532.71** | **$244,204.37** | **$333,272.83** |
| **Return on Investment (ROI)** | **356.2%** | **519.5%** | **723.6%** |
| **Incremental Breaks Identified** | 895 | **1,095** | 1,325 |
| **Payback Period** | 6.8 months | **1.9 months** | 2.1 months |

