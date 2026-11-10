# Statistical Process Control and Fault Detection

## Statistical process control (SPC)
SPC tracks key measurements over time on **control charts**. Each chart has a center line and control limits, usually at plus or minus three standard deviations. Points outside the limits, or unusual runs, signal that the process has shifted.

The **Western Electric rules** flag patterns such as one point beyond 3 sigma, two of three points beyond 2 sigma on the same side, or eight points in a row on one side of the center line.

**Process capability** compares process spread to specification limits. Cpk = min(USL - mean, mean - LSL) / (3 * sigma). A Cpk of 1.33 or higher is a common target.

## Fault detection and classification (FDC)
Process tools stream sensor data (pressure, temperature, RF power, gas flow) during every wafer run. FDC systems summarize these traces into features and compare them to normal behavior to detect faults in real time and classify their cause. Catching a fault early prevents many wafers from being misprocessed.

## Run-to-run (R2R) control
R2R control adjusts recipe settings between runs using recent metrology results, for example tuning exposure dose to hold CD on target as conditions drift.

## Virtual metrology
Virtual metrology predicts a measurement (such as film thickness or CD) from tool sensor data using a regression or ML model, so every wafer gets an estimate even when only a sample is physically measured.
