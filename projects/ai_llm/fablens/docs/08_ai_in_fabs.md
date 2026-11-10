# AI and Data in Semiconductor Manufacturing

Fabs generate huge volumes of data from tools, metrology, inspection, and test. AI helps turn that data into decisions.

## Main use cases
- **Yield prediction**: models predict wafer or die yield from upstream process and metrology data, so problems are caught before final test.
- **Root-cause analysis**: ML ranks which tools, chambers, recipes, or parameters are most associated with yield loss.
- **Virtual metrology** and **predictive maintenance** (see related documents).
- **Defect classification**: computer vision sorts SEM review images and wafer maps.
- **Computational lithography**: optical proximity correction (OPC) and inverse lithography adjust mask shapes so the printed pattern matches the design; ML speeds up these heavy simulations.

## Holistic lithography
Lithography performance is improved by linking three parts in a loop: computational lithography (designing the mask and settings), metrology (measuring the result), and the scanner (applying corrections). Feeding data across the loop lets the system correct errors faster and widen the process window.

## Challenges
- Data lives in many separate systems and formats.
- Labels are scarce and classes are imbalanced (failures are rare).
- Processes drift, so models must be monitored and retrained.
- Fab data is highly confidential, so AI systems need strong governance and access control.

Large language models and retrieval-augmented generation (RAG) can help engineers search procedures, reports, and past root-cause findings in plain language.
