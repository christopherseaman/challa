# K01 Resubmission: Power Analysis Implementation Plan

## Overview
This document outlines the implementation plan for rigorous power calculations supporting two specific aims in South Asian sexual and reproductive health research.

## Current Status
- Project context: K01 resubmission with reviewer concerns about statistical rigor
- Previous errors identified: Wrong population assumptions, ignored survey design, treated dyadic data as independent
- Goal: Grant-ready power calculations with proper methodology

## Implementation Questions to Address

### Methodological Clarifications Needed:

#### Aim 1 (CHIS Decomposition Analysis):
1. **Baseline rates for additional outcomes**: 
   - IPV: 6% (specified)
   - Contraceptive use: What baseline rate to assume? (typical range 60-80% for this age group)
   - Contraceptive counseling: What baseline rate to assume? (typical range 40-70%)

2. **Effect size interpretation**:
   - OR = 1.15 specified as "minimum detectable effect" - is this the target effect we want 80% power to detect?
   - Or should we calculate what OR we CAN detect with 80% power given the sample size?

3. **Multiple comparisons strategy**:
   - FDR correction specified - should we show power both with/without correction?
   - Are all 3 outcomes primary, or is IPV the main outcome with others secondary?

#### Aim 3 (Dyadic APIM Analysis):
1. **Effect size specification**:
   - "Moderate actor effects" and "majority partner effects" - need specific OR values
   - Suggested: Actor OR = 1.5, Partner OR = 2.0 based on IPV literature?

2. **Analysis approach**:
   - Separate power calculations for actor vs partner effects?
   - Combined model power or individual effect power?

3. **Continuous exposure handling**:
   - Gender norms scale (1-5) - should we assume 1 SD change effect?
   - Or convert to dichotomous exposure for simpler interpretation?

## Implementation Plan

### Phase 1: Setup and Parameter Definition
- [ ] Define all baseline rates and effect sizes
- [ ] Set up Python environment with required packages
- [ ] Create parameter dictionaries for both aims

### Phase 2: Aim 1 Power Functions
- [ ] Implement survey-weighted logistic regression power calculation
- [ ] Account for design effect (effective n = 158)
- [ ] Handle multiple comparisons (FDR correction)
- [ ] Create sensitivity analysis functions

### Phase 3: Aim 3 Dyadic Power Functions  
- [ ] Implement APIM power calculation accounting for:
   - ICC between partners (0.3)
   - Correlation between partner exposures (0.4)
   - Distinguishable dyads structure
- [ ] Separate functions for actor and partner effects
- [ ] Account for reduced effective information due to clustering

### Phase 4: Analysis Outputs
- [ ] Power calculation result tables
- [ ] Sensitivity analysis plots
- [ ] Minimum detectable effect calculations
- [ ] Clear assumption documentation

### Phase 5: Validation and Documentation
- [ ] Compare results to established formulas/software where possible
- [ ] Create reproducible analysis scripts
- [ ] Document all assumptions and limitations

## Technical Approach

### Python Packages:
- `scipy.stats` - Statistical functions
- `statsmodels` - Power calculations, survey analysis
- `numpy/pandas` - Data manipulation
- `matplotlib/seaborn` - Visualization
- `sympy` (if needed) - Symbolic math for complex power formulas

### Key Methodological Considerations:
1. **Survey design effects**: Use effective sample size throughout
2. **Dyadic interdependence**: Implement variance inflation for clustered data
3. **Binary outcomes**: Use appropriate power formulas for logistic regression
4. **Multiple comparisons**: Show both corrected and uncorrected power
5. **Realistic effect sizes**: Base on published literature where possible

## Deliverables
1. Well-documented Python scripts
2. Power calculation summary tables
3. Sensitivity analysis visualizations
4. Minimum detectable effect summaries
5. Clear limitations and assumptions documentation

## Questions for Clarification

Before proceeding with implementation, please confirm:

1. **Baseline rates for Aim 1 outcomes** (contraceptive use and counseling)
2. **Target effect sizes for Aim 3** (actor and partner effects)
3. **Primary vs secondary outcomes** (affects multiple comparisons strategy)
4. **Preferred format for outputs** (tables, plots, etc.)

This plan ensures we address all methodological concerns while creating grant-ready power calculations.