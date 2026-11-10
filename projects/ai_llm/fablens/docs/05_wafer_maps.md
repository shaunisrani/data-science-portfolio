# Wafer Maps and Spatial Patterns

A wafer map shows the pass/fail result (or a measurement) for every die at its position on the wafer. Spatial patterns on wafer maps point to specific root causes.

## Common signatures
- **Center**: failures concentrated in the middle, often linked to deposition or etch uniformity.
- **Edge ring / edge local**: failures near the edge, often from edge bead, chuck, or thermal effects.
- **Donut**: a ring between center and edge.
- **Scratch**: a line of failing dies from handling or CMP.
- **Cluster (local)**: a tight group of failures from a particle or local defect.
- **Random**: scattered failures with no pattern, typical of random defects.

## Machine learning on wafer maps
Wafer map patterns can be classified automatically. Convolutional neural networks (CNNs) treat the map as an image and learn the patterns. The public WM-811K dataset contains about 811,000 wafer maps from real production, of which a small share are labeled with nine pattern classes; it is heavily imbalanced, so data augmentation and class weighting are common.

Clustering methods can also group unlabeled maps to find new failure signatures. Linking a detected pattern to the tools and chambers that processed those wafers (commonality analysis) helps engineers find the root cause quickly.
