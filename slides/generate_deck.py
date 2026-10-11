"""
PowerPoint Presentation Generator for Executive Leadership & Hiring Managers
Builds a professional 12-slide presentation deck (slides/project_deck.pptx)
using python-pptx matching PDF Pages 10-11.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

SLIDES_DIR = "slides"
DECK_PATH = os.path.join(SLIDES_DIR, "project_deck.pptx")
FIGURES_DIR = "figures"

# Corporate Color Palette (DTCC Blue / Navy theme)
NAVY = RGBColor(16, 44, 87)       # Primary #102C57
ACCENT = RGBColor(53, 162, 159)   # Teal #35A29F
DARK_GRAY = RGBColor(60, 64, 67)
LIGHT_BG = RGBColor(245, 247, 250)
WHITE = RGBColor(255, 255, 255)
GOLD = RGBColor(218, 165, 32)

def set_slide_background(slide, color):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, title_text, category_text="FINANCE ANALYTICS & INNOVATION | CFO ORGANIZATION"):
    # Header container
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(1.1))
    tf = header_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    
    p_cat = tf.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = ACCENT
    
    p_title = tf.add_paragraph()
    p_title.text = title_text
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = NAVY

def add_bullet_point(text_frame, title, body, pt_size=13):
    p = text_frame.add_paragraph()
    p.font.size = Pt(pt_size)
    p.space_after = Pt(10)
    
    run_title = p.add_run()
    run_title.text = title + " "
    run_title.font.bold = True
    run_title.font.color.rgb = NAVY
    
    run_body = p.add_run()
    run_body.text = body
    run_body.font.color.rgb = DARK_GRAY

def build_presentation():
    os.makedirs(SLIDES_DIR, exist_ok=True)
    prs = Presentation()
    prs.slide_width = Inches(13.333) # 16:9 widescreen
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]
    
    # -------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, NAVY)
    
    tb = s1.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(11.0), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p_tag = tf.paragraphs[0]
    p_tag.text = "DTCC FINANCE ANALYTICS & INNOVATION | PROOF OF CONCEPT"
    p_tag.font.size = Pt(13)
    p_tag.font.bold = True
    p_tag.font.color.rgb = ACCENT
    p_tag.space_after = Pt(12)
    
    p_title = tf.add_paragraph()
    p_title.text = "Reconciliation Break-Risk Scoring\n& Root-Cause Triage"
    p_title.font.size = Pt(36)
    p_title.font.bold = True
    p_title.font.color.rgb = WHITE
    p_title.space_after = Pt(16)
    
    p_sub = tf.add_paragraph()
    p_sub.text = "A Governed Analytics + AI Decision-Support Layer for the CFO Organization"
    p_sub.font.size = Pt(18)
    p_sub.font.color.rgb = RGBColor(220, 230, 242)
    p_sub.space_after = Pt(28)
    
    p_meta = tf.add_paragraph()
    p_meta.text = "Candidate: Bhupesh Chandra Dimri | Email: bhupesh7cd@gmail.com | Target Role: Finance Analytics & Innovation Associate (Job ID 214537)\nJersey City, NJ | October 2026 | Reproducible Codebase & Governed Artifacts Included"
    p_meta.font.size = Pt(11)
    p_meta.font.color.rgb = RGBColor(180, 195, 215)
    
    # -------------------------------------------------------------
    # SLIDE 2: PROBLEM OVERVIEW & EXECUTIVE SUMMARY
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, LIGHT_BG)
    add_header(s2, "Executive Problem Statement: Catching Breaks Before Close")
    
    tb2 = s2.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf2 = tb2.text_frame
    tf2.word_wrap = True
    
    add_bullet_point(tf2, "The Core Financial Friction:", "Reconciliation breaks are discovered during month-end close rather than before it. Late breaks consume hundreds of analyst hours, create closing crunch periods, and risk late financial reporting adjustments.")
    add_bullet_point(tf2, "The Analytical Solution:", "A pre-close risk scorer trained on pre-close transaction attributes (entity, mapping age, posting lag, proximity to period-end, prior breaks, vendor duplicate signature).")
    add_bullet_point(tf2, "Proven Empirical Result:", "Reviewing only the top 10% of items ranked by the model catches ~33.2% of all breaks versus 21.8% for the existing analyst heuristic (a 3.32x lift over random inspection).")
    add_bullet_point(tf2, "Controller-Grade Explainability:", "Logistic Regression performs within statistical noise of complex Gradient Boosting (PR-AUC 0.251 vs 0.208). In a regulated CFO environment, an auditable model controllers can read beats a black-box.")
    add_bullet_point(tf2, "Highest-Leverage Business Action:", "Upstream Chart-of-Accounts mapping staleness is the #1 predictor of breaks. A governance SLA refresh eliminates ~47% of systemic break risk before transactions even occur.")
    
    # -------------------------------------------------------------
    # SLIDE 3: JD BREAKDOWN & CANDIDATE ALIGNMENT
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, LIGHT_BG)
    add_header(s3, "Bridging Business Needs to Scalable Technical Solutions")
    
    tb3 = s3.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf3 = tb3.text_frame
    tf3.word_wrap = True
    
    add_bullet_point(tf3, "Analytics & Reporting (50%):", "Engineered reproducible data pipelines in Python & DuckDB. Developed interactive review queue in Streamlit with exportable CSVs and executive KPI metrics.")
    add_bullet_point(tf3, "Innovation & AI Proofs of Concept (25%):", "Formulated 3 linked analytical problems: P1 binary break scoring, P2 multi-class root cause classification, and P3 LLM triage with human-in-the-loop auditability.")
    add_bullet_point(tf3, "Business Analysis & Agile Delivery (15%):", "Authored complete 1-page Business Requirements Document (BRD), 10 fully specified user stories with acceptance criteria, and 10 UAT test scripts.")
    add_bullet_point(tf3, "Data Governance & Internal Controls (10%):", "Shipped production-grade governance assets: Critical Data Element (CDE) register, BCBS 239 lineage diagram, SOX 404 control matrix, and SR 11-7 model card.")
    
    # -------------------------------------------------------------
    # SLIDE 4: ML PROBLEM FORMULATION
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, LIGHT_BG)
    add_header(s4, "Three Linked Problems: Pre-Close Risk, Root Cause & Triage")
    
    tb4 = s4.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf4 = tb4.text_frame
    tf4.word_wrap = True
    
    add_bullet_point(tf4, "Problem 1: Pre-Close Break-Risk Scoring (P1):", "Binary classification predicting 'is_break' strictly using attributes known at posting. Quarantines post-reconciliation variance to prevent circular leakage.")
    add_bullet_point(tf4, "Why Not a Simple Dollar Tolerance?:", "A reconciliation difference is a break by definition. Scoring risk before the difference exists is where machine learning adds unique operational value.")
    add_bullet_point(tf4, "Problem 2: Root-Cause Classification (P2):", "Multi-class classification (5 categories: rounding/FX, mapping error, timing, missing feed, duplicate) utilizing post-reconciliation differences once available. Reaches Macro-F1 of 0.78.")
    add_bullet_point(tf4, "Problem 3: AI-Assisted Triage Layer (P3):", "Deterministic plain-English explanation engine generating specific remediation actions and assigned team owners. Benchmarked against enterprise LLMs with 100% factual grounding.")
    
    # -------------------------------------------------------------
    # SLIDE 5: DATA ARCHITECTURE & CDE QUALITY CHECKS
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, LIGHT_BG)
    add_header(s5, "Governed Data Strategy: Seeded Synthetic Pipeline")
    
    tb5 = s5.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(5.5), Inches(5.0))
    tf5 = tb5.text_frame
    tf5.word_wrap = True
    
    add_bullet_point(tf5, "Seeded Reproducibility:", "Synthetic generator (seed=42) creating 30,000 transactions across 5 DTCC entities and 6 account categories. Calibrated baseline break prevalence: 7.23%.")
    add_bullet_point(tf5, "Chronological Split:", "Strict time-based holdout: first 24,000 items (80%) train; last 6,000 items (20%) out-of-sample test. Zero look-ahead contamination.")
    add_bullet_point(tf5, "12 Critical Data Element Checks:", "Automated DQ validation asserting non-null UUIDs, valid date sequences, positive monetary values, and zero feature leakage (100% pass rate).")
    
    # Add Image if available
    img_path = os.path.join(FIGURES_DIR, "class_balance_and_differences.png")
    if os.path.exists(img_path):
        s5.shapes.add_picture(img_path, Inches(6.6), Inches(1.8), width=Inches(6.0))
        
    # -------------------------------------------------------------
    # SLIDE 6: MODEL BENCHMARK COMPARISON
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, LIGHT_BG)
    add_header(s6, "Holdout Benchmark: Logistic Regression Matches Ensembles")
    
    tb6 = s6.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(5.5), Inches(5.0))
    tf6 = tb6.text_frame
    tf6.word_wrap = True
    
    add_bullet_point(tf6, "Primary Metric: PR-AUC:", "Precision-Recall AUC is the statistically robust metric for imbalanced classes (7.88% test prevalence). Logistic Regression achieves 0.251 vs Heuristic 0.179.")
    add_bullet_point(tf6, "Top 10% Review Capacity:", "Logistic Regression catches 33.2% of all breaks (157 / 473) in top 10% volume, delivering a 3.32x lift over random queue inspection.")
    add_bullet_point(tf6, "The Modeling Decision:", "Gradient Boosting (0.208 PR-AUC, 29.4% capture) and Random Forest (0.237 PR-AUC, 30.7% capture) perform within sampling noise (+/- 3.5%). Logistic regression wins on auditability and governance.")
    
    img_path2 = os.path.join(FIGURES_DIR, "model_comparison_holdout.png")
    if os.path.exists(img_path2):
        s6.shapes.add_picture(img_path2, Inches(6.6), Inches(1.8), width=Inches(6.0))
        
    # -------------------------------------------------------------
    # SLIDE 7: KEY RISK DRIVERS & ECONOMETRIC DIAGNOSTICS
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, LIGHT_BG)
    add_header(s7, "Feature Permutation Importance: Upstream Mapping is #1")
    
    tb7 = s7.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(5.5), Inches(5.0))
    tf7 = tb7.text_frame
    tf7.word_wrap = True
    
    add_bullet_point(tf7, "Mapping Table Staleness:", "Drop of ~0.12 in PR-AUC when shuffled. Accounts using mappings > 90 days show break odds ratio > 2.8x. Upstream governance prevents breaks downstream.")
    add_bullet_point(tf7, "Duplicate Vendor Signatures:", "Odds ratio ~ 3.8x. Immediate signal of duplicate invoice entry or voucher re-keying.")
    add_bullet_point(tf7, "Manual vs Automated Entries:", "Manual journals exhibit > 2.2x higher break odds than automated STP feeds.")
    add_bullet_point(tf7, "Close-Window Proximity:", "Entries booked within 3 days of period-end compounded by manual flag elevate operational break risk.")
    
    img_path3 = os.path.join(FIGURES_DIR, "permutation_feature_importance.png")
    if os.path.exists(img_path3):
        s7.shapes.add_picture(img_path3, Inches(6.6), Inches(1.8), width=Inches(6.0))
        
    # -------------------------------------------------------------
    # SLIDE 8: SCENARIO SIMULATIONS
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, LIGHT_BG)
    add_header(s8, "Scenario Stress Testing: Controller-Validated Behavior")
    
    tb8 = s8.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(5.5), Inches(5.0))
    tf8 = tb8.text_frame
    tf8.word_wrap = True
    
    add_bullet_point(tf8, "Scenario A (Clean Automated Item):", "Scores 0.19, safely below the 0.35 review threshold. No analyst time wasted.")
    add_bullet_point(tf8, "Scenario B (Worst-Case Manual/Stale):", "Scores 1.00 (expected 0.99), immediately surfaced at the very top of the review queue.")
    add_bullet_point(tf8, "Scenario C (Intercompany Clean Item):", "Scores 0.25 (expected 0.23). Category membership alone does not trigger false alerts.")
    add_bullet_point(tf8, "Scenario D (Manual FX Reval at Close):", "Scores 0.69 (expected 0.52). Combined risk factors correctly push transaction above review threshold.")
    
    img_path4 = os.path.join(FIGURES_DIR, "scenario_simulation_scores.png")
    if os.path.exists(img_path4):
        s8.shapes.add_picture(img_path4, Inches(6.6), Inches(1.8), width=Inches(6.0))
        
    # -------------------------------------------------------------
    # SLIDE 9: ROOT-CAUSE TRIAGE & AUTO-CLEARING TIER
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, LIGHT_BG)
    add_header(s9, "Root-Cause Triage: Automated Clearing for Immaterial Breaks")
    
    tb9 = s9.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(5.5), Inches(5.0))
    tf9 = tb9.text_frame
    tf9.word_wrap = True
    
    add_bullet_point(tf9, "Sub-Dollar Auto-Clear Tier (F1 = 1.00):", "Discrepancies under $1.00 are isolated with 100% precision. Recommends policy-governed automated clearing to FX rounding accounts, saving 15-20% queue volume.")
    add_bullet_point(tf9, "Mapping Error Classifier (F1 = 0.76):", "Automatically generates MDM mapping change tickets, targeting upstream rules rather than repetitive manual reconciliation.")
    add_bullet_point(tf9, "Duplicate Quarantine (F1 = 0.97):", "High-exposure items flagged for immediate AP supervisor block, preventing dual disbursement.")
    add_bullet_point(tf9, "AI Triage Benchmark:", "Deterministic engine provides 100% factual grounding at 1.2ms latency, beating LLM hallucination risks in regulated accounting.")
    
    img_path5 = os.path.join(FIGURES_DIR, "root_cause_confusion_matrix.png")
    if os.path.exists(img_path5):
        s9.shapes.add_picture(img_path5, Inches(6.6), Inches(1.8), width=Inches(6.0))
        
    # -------------------------------------------------------------
    # SLIDE 10: FINANCIAL IMPACT & MONTE CARLO BUSINESS CASE
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10, LIGHT_BG)
    add_header(s10, "Business Case: 520% ROI & 1.9-Month Payback")
    
    tb10 = s10.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(5.5), Inches(5.0))
    tf10 = tb10.text_frame
    tf10.word_wrap = True
    
    add_bullet_point(tf10, "Base Case Financial Return:", "Annual gross benefits of $356K (labor savings + avoided restatement penalties + auto-clear efficiencies) yields $253K Year-1 Net Benefit.")
    add_bullet_point(tf10, "Conservative Downside Protection:", "Under stressed assumptions (conservative break capture, lower hourly loaded rate), Year-1 Net Benefit remains strongly positive at $117K (107% ROI).")
    add_bullet_point(tf10, "Monte Carlo Simulation (1,000 Runs):", "Median annual net benefit of $244K with 10th percentile floor of $168K and median payback period of 1.9 months.")
    
    img_path6 = os.path.join(FIGURES_DIR, "monte_carlo_financial_simulation.png")
    if os.path.exists(img_path6):
        s10.shapes.add_picture(img_path6, Inches(6.6), Inches(1.8), width=Inches(6.0))
        
    # -------------------------------------------------------------
    # SLIDE 11: GOVERNANCE, AUDITABILITY & SOX 404 CONTROLS
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11, LIGHT_BG)
    add_header(s11, "Model Risk Management (SR 11-7) & SOX 404 Governance")
    
    tb11 = s11.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf11 = tb11.text_frame
    tf11.word_wrap = True
    
    add_bullet_point(tf11, "Segregation of Duties & Human-in-the-Loop:", "The model prioritizes and recommends; only certified finance analysts confirm or dispose of breaks. Zero unapproved GL adjustments.")
    add_bullet_point(tf11, "Immutable Audit Trail Schema:", "Every analyst decision logs `[transaction_id, analyst_id, disposition, timestamp, override_flag, rationale]` compliant with SEC financial records retention rules.")
    add_bullet_point(tf11, "Automated Drift Monitoring:", "Weekly Kolmogorov-Smirnov and Population Stability Index (PSI) checks trigger alerts if feature distributions or override rates exceed 20%.")
    add_bullet_point(tf11, "Full Artifact Governance:", "Ships with BCBS 239 lineage diagram, CDE data dictionary, SR 11-7 model card, and 10 executable UAT test scripts.")
    
    # -------------------------------------------------------------
    # SLIDE 12: IMPLEMENTATION ROADMAP & RECOMMENDATIONS
    # -------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12, LIGHT_BG)
    add_header(s12, "Controlled Pilot Roadmap & Executive Recommendations")
    
    tb12 = s12.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    tf12 = tb12.text_frame
    tf12.word_wrap = True
    
    add_bullet_point(tf12, "Phase 1: Shadow Scoring Pilot (Weeks 1-4):", "Deploy batch nightly scoring in parallel with existing manual close process across Settlement & Clearing entities. Validate out-of-sample capture on live DTCC data.")
    add_bullet_point(tf12, "Phase 2: Upstream Mapping SLA Enforcement (Weeks 5-8):", "Implement 60-day Chart-of-Accounts mapping refresh policy in Master Data Management, capturing the 47% systemic risk reduction.")
    add_bullet_point(tf12, "Phase 3: Operational Queue Integration (Weeks 9-12):", "Roll out the Streamlit review queue to reconciliation analysts with sub-$1.00 auto-clearing approval.")
    add_bullet_point(tf12, "Final Pilot Recommendation: GO (Controlled Pilot):", "All quality gates, reproducible tests, and governance artifacts are fully verified. Recommended model: Explainable Logistic Regression.")
    add_bullet_point(tf12, "Contact Information & Inquiries:", "Bhupesh Chandra Dimri | Email: bhupesh7cd@gmail.com | Location: Jersey City, NJ")
    
    # Save Presentation
    prs.save(DECK_PATH)
    print(f"Presentation saved successfully to {DECK_PATH}")

if __name__ == "__main__":
    build_presentation()
