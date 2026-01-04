# Sleepiness & Diagnostic Group Prediction (COGS 108)

## Objective
Investigate how sleepiness-related measures and demographic/health variables relate to diagnostic group membership, and evaluate whether these features provide reliable predictive signal—while explicitly accounting for missing data, subgroup behavior, and statistical validity.

## Data
- Observational, tabular dataset used in the COGS 108 final group project.
- Key variable families include:
  - Sleepiness measures (e.g., Epworth Sleepiness Scale)
  - Demographic and health-related variables
  - Diagnostic group label used as the prediction target
- Dataset contains structured missingness requiring explicit analysis rather than naive row removal.

## Analytical Pipeline
1. Data cleaning, validation, and preprocessing  
2. Missingness analysis and bias assessment  
3. Exploratory and relational analysis  
4. Hypothesis testing of group differences  
5. Predictive modeling and evaluation  
6. Subgroup (fairness-style) diagnostics and interpretation

## Methods & Skills Demonstrated

### Data Engineering & Cleaning
- Validation of feature types, ranges, and consistency
- Reproducible preprocessing decisions documented across checkpoints
- Structured workflow supporting iterative analysis

### Missingness Analysis
- Quantified missingness across features
- Compared outcome distributions for missing vs. non-missing cohorts
- Tested associations between missingness and the prediction target
- Assessed potential bias introduced by missing data handling choices

### Exploratory Analysis
- Distributional analysis of sleepiness and health variables
- Correlation analysis among numeric features
- Group-wise comparisons stratified by diagnostic label
- Visualization-driven reasoning to motivate downstream tests and models

### Statistical Hypothesis Testing
- Formulated hypotheses regarding diagnostic group differences
- Applied appropriate statistical tests based on variable type and distribution
- Interpreted results with attention to effect size, uncertainty, and limitations

### Predictive Modeling
- Built a baseline classification model to predict diagnostic group
- Performed train/test splitting and evaluated model performance
- Interpreted model behavior and feature contributions
- Framed modeling results as signal evaluation rather than deployment

### Subgroup / Fairness Diagnostics
- Evaluated model performance across demographic subgroups
- Compared error rates and predictive behavior between groups
- Used subgroup results to assess potential bias and generalizability
- Avoided causal overclaims; analysis framed diagnostically

## Key Findings
- Sleepiness-related measures showed meaningful associations with diagnostic group membership.
- Missingness was not random for key variables and required explicit consideration.
- Predictive models captured interpretable signal but exhibited limitations consistent with observational data.
- Subgroup analyses highlighted areas where model performance differed, informing responsible interpretation.

## Artifacts
- `notebooks/` — proposal, checkpoints, and final analysis notebooks
- `images/` — diagnostic plots and visual summaries
- `results/` — exported outputs used in reporting
- `src/` — helper modules and utilities

## Notes
This project emphasizes analytical reasoning, data validation, and interpretability rather than model optimization.

