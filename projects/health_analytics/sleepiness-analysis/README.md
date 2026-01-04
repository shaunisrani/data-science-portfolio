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

### Data Cleaning & Engineering
- Validation of feature types, ranges, and consistency
- Transparent preprocessing decisions documented across project checkpoints
- Reproducible notebook-based workflow

### Missingness Analysis
- Quantified missingness across features
- Compared distributions of key variables between missing and non-missing cohorts
- Tested associations between missingness and diagnostic group
- Assessed potential bias introduced by different missing-data handling choices

### Exploratory Analysis
- Distributional analysis of sleepiness and health variables
- Correlation analysis among numeric features
- Group-wise comparisons stratified by diagnostic label
- Visualization-driven reasoning to motivate downstream statistical tests

### Statistical Hypothesis Testing
- Formulated hypotheses regarding differences between diagnostic groups
- Selected appropriate statistical tests based on variable type and distribution
- Interpreted results with attention to effect direction, uncertainty, and limitations

## Key Findings
- Sleepiness-related measures exhibited meaningful differences across diagnostic groups.
- Missingness was not random for key variables and required explicit consideration.
- Group-level statistical comparisons revealed patterns consistent with existing domain expectations, while highlighting limitations of observational data.

## Artifacts
- `notebooks/` — proposal, checkpoints, and final analysis notebooks
- `images/` — diagnostic plots and visual summaries
- `results/` — exported outputs used in reporting
- `src/` — helper modules and utilities

## Notes
This project emphasizes analytical reasoning, data validation, and interpretability rather than model optimization.

