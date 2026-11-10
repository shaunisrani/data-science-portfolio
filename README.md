# Data Science Portfolio

Selected data science projects demonstrating rigorous data analysis, statistical reasoning, data engineering, and clear communication through reproducible artifacts.

## Featured Projects

### FabLens: Semiconductor Yield RAG Assistant + Agent
**LangChain RAG app and tool-calling agent with cited answers**
- Hybrid BM25 + FAISS retrieval; Claude or Mistral answers only from retrieved context
- Agents in LangChain and Semantic Kernel (Azure OpenAI) with tested tools: yield models, dies per wafer, Cpk
- Query logging for auditability; pytest + GitHub Actions CI with a retrieval quality gate
- Roadmap: public demo on Hugging Face Spaces
→ `projects/ai_llm/fablens/`

### AI App Scorecard
**Reusable accuracy scorecard for a team's AI apps**
- Scores retrieval, answer correctness, correct refusals, citations, and latency with quality gates
- Flags regressions against a baseline; plugs into any app via an adapter or HTTP
- Caught a real FabLens bug (0% correct refusals); after the fix, 78 → 98/100
→ `projects/ai_llm/ai-app-scorecard/`

### League of Legends Gameplay Analysis: Wards vs. Dragons (DSC 80)
**End-to-end data science project with modeling and deployment**
- Data engineering and validation with explicit missingness analysis
- Hypothesis testing, predictive analysis, and subgroup diagnostics
- Results communicated via a deployed, web-based data product (GitHub Pages)
→ `projects/data_wrangling_web/dsc80-final-project/`

### Sleepiness & Diagnostic Group Analysis (COGS 108)
**Statistical analysis and data-quality–focused project**
- Rigorous missingness investigation and bias assessment
- Exploratory analysis and hypothesis testing across diagnostic groups
- Emphasis on interpretability and responsible analysis of observational data
→ `projects/health_analytics/sleepiness-analysis/`

### Sensor-Based Time-Series Analysis (DSC 96)
**Report-driven signal and time-series analysis**
- Exploratory analysis of sensor data and temporal patterns
- Feature reasoning and diagnostic visualization
- Communicated findings through a structured analytical report
→ `projects/sensing_time_series/sensor-analysis/`

## Skills Demonstrated
- RAG, LangChain agents, FAISS, Claude API, Mistral AI, Gradio
- AI evaluation, quality gates, CI (pytest, GitHub Actions)
- Python, pandas, NumPy, scikit-learn, Jupyter
- Data cleaning, validation, and missingness analysis
- Exploratory data analysis and statistical hypothesis testing
- Predictive modeling and responsible subgroup evaluation
- Communication of results via reports, notebooks, and deployed artifacts

## Coursework Archive
Original coursework and supporting materials:  
→ `coursework/`
