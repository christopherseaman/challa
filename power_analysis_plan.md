# Power Analysis Implementation Plan

This document outlines the implementation plan for rigorous power calculations supporting two specific aims for the K01 resubmission on South Asian sexual and reproductive health.

## Parameter Definitions

**Aim 1: CHIS Decomposition Analysis**
- Sample size: n = 237 South Asians
- Design effect: DEFF = 1.5 (effective n ≈ 158)
- Alpha: α = 0.1
- Baseline outcome rates: IPV = 6% (power-limiting); contraceptive use and counseling treated as secondary.
- Target OR for MDE: OR = 1.15 for power curves; actual effect size of interest calibrated.

**Aim 3: Dyadic APIM Analysis**
- Number of couples: n = 200
- ICC between partners: ICC = 0.3
- Baseline IPV rate: 20%
- Target ORs: Actor = 1.4; Partner = 1.6
- Alpha: α = 0.1

## Phase 1: Setup & Environment

1. Install required Python packages:
   ```bash
   pip install numpy pandas scipy statsmodels matplotlib seaborn
   ```
2. Create `config.py` (or parameter dictionary) containing study parameters.

## Phase 2: Aim 1 Power Functions

- Implement two-sample proportion power with design effect:
  - Function: `two_sample_proportion_power(n1, n2, p1, p2, alpha, design_effect)`
- Implement `min_detectable_OR(n1, n2, p2, power, alpha, design_effect)`.
- Incorporate multiple comparisons:
  - FDR (Benjamini-Hochberg) and Bonferroni adjustments.

## Phase 3: Aim 3 Dyadic Power Functions

- Implement APIM power using variance inflation:
  - Function: `dyadic_power_apim(n_couples, p_baseline, actor_OR, partner_OR, icc, alpha)`
- Separate calculations for actor and partner effects.

## Phase 4: Analysis Outputs

- Generate result tables:
  - Power vs OR for Aim 1 and Aim 3.
  - Power vs sample size sensitivity.
  - Minimum detectable OR at 80% power.
- Visualize:
  ```mermaid
  flowchart TD
    A[Phase 1: Setup & Parameter Definition] --> B[Aim 1 parameters]
    B --> B1[n_SA = 237; DEFF = 1.5; α = 0.1; p_others = 0.06; p_SA = 0.10]
    A --> C[Aim 3 parameters]
    C --> C1[n_couples = 200; ICC = 0.3; baseline IPV = 20%]
    C --> C2[Actor OR=1.4; Partner OR=1.6; α = 0.1]
    A --> D[Aim 1 Power Functions]
    D --> D1[two_sample_proportion_power]
    D --> D2[min_detectable_OR]
    A --> E[Aim 3 Dyadic Functions]
    E --> E1[dyadic_power_apim]
    A --> F[Analysis Outputs]
  ```

## Phase 5: Validation & Documentation

- Cross-check critical functions against APIMPowerR or simulation.
- Document assumptions and limitations.
- Prepare reproducible scripts and README.

## Deliverables

1. Python scripts with functions for Aim 1 and Aim 3.
2. Result tables and power curves saved as CSV and PNG.
3. Markdown report summarizing methods, results, and assumptions.

## Assumptions

- Survey design effect = 1.5.
- ICC for dyadic clustering = 0.3.
- Baseline IPV rates: 6% (CHIS) and 20% (dyadic).
- Significance threshold α = 0.1.

## Next Steps

- Review code implementation in Code mode.
- Validate with empirical or simulation checks.
- Integrate outputs into grant application.