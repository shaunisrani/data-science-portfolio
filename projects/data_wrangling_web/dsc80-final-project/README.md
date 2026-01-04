# League of Legends Gameplay Analysis: Wards vs. Dragons (DSC 80)

## Objective
Analyze competitive League of Legends match data to investigate how strategic behaviors—specifically vision control (wards placed) versus objective control (dragons taken)—relate to game outcomes and performance metrics. The project evaluates both statistical relationships and predictive signals while accounting for missing data and subgroup effects.

## Data
- Match-level competitive League of Legends data.
- Features include objective counts (e.g., dragons), vision metrics (wards placed), game duration, and outcome variables.
- Dataset contains structured missingness requiring explicit analysis rather than naive deletion.

## Methods & Skills Demonstrated

### Data Engineering & Validation
- Data ingestion and schema validation
- Explicit missingness analysis, including:
  - Identification of missingness patterns
  - Comparison of distributions between missing and non-missing groups
- Feature construction and transformation for downstream analysis

### Exploratory & Statistical Analysis
- Exploratory data analysis using distributions and visual summaries
- Hypothesis testing to evaluate differences between strategic behaviors
- Group-wise comparisons to assess how strategy correlates with outcomes

### Predictive Analysis
- Construction of baseline predictive models to estimate outcome likelihood
- Evaluation of model behavior across different feature subsets
- Interpretation of predictive signals rather than pure optimization

### Fairness / Subgroup Analysis
- Subgroup comparisons to examine whether relationships differ across:
  - Game length
  - Strategy emphasis (vision-heavy vs. objective-heavy playstyles)
- Analysis framed to detect asymmetric effects rather than claim causal fairness guarantees

### Communication & Deployment
- Generation of static, interactive visualizations
- Deployment of analysis results as a web-based data product using GitHub Pages
- Clear narrative documentation explaining analytical decisions and results

## Results
- Identified measurable relationships between vision control, objective control, and game outcomes.
- Demonstrated that strategic emphasis correlates differently with outcomes depending on game context.
- Predictive models provided interpretable baseline signals linking in-game behavior to results.
- Web-based artifacts allow exploration of missingness effects and distributional differences.

## Artifacts
- `notebooks/` — exploratory analysis, missingness evaluation, hypothesis testing, and modeling
- `src/` — reusable analysis and data processing code
- `site/` — deployed interactive visualizations (GitHub Pages)
- Project report (PDF), if included

## Notes
This project emphasizes methodological rigor, interpretability, and responsible analysis over leaderboard-style model tuning.
