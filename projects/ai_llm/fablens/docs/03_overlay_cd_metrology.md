# Overlay and CD Metrology

Metrology measures what was printed so the process can be kept on target.

## Critical dimension (CD)
CD is the width of a key feature, such as a transistor gate or line. CD is measured with:
- **CD-SEM**: a scanning electron microscope images features top-down. Accurate but slow and can damage resist.
- **Scatterometry (optical CD, OCD)**: shines light on a periodic target and fits the measured spectrum to a model. Fast and non-destructive.

## Overlay
Overlay is how well one patterned layer aligns to the layers below it. Overlay error is measured on dedicated targets, using image-based overlay or diffraction-based overlay. Poor overlay can cause shorts or opens between layers and is a major yield detractor, especially with multi-patterning.

## Process window
A **focus-exposure matrix (FEM)** wafer is exposed with a grid of focus and dose settings. The **process window** is the range of focus and dose where CD stays within specification. A larger process window means the process is more robust to normal variation.

## Using metrology data
Metrology results feed back into the scanner as corrections (for example per-field or per-wafer overlay corrections). Sampling more points improves control but costs measurement time, so fabs balance sampling density against throughput.
