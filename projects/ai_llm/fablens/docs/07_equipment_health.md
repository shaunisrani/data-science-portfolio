# Equipment Health and Predictive Maintenance

Fab tools are expensive, so keeping them running matters for cost and output.

## Key metrics
- **OEE (overall equipment effectiveness)** = availability x performance x quality.
- **MTBF (mean time between failures)** and **MTTR (mean time to repair)** describe reliability and how fast tools come back online.
- **Throughput**: wafers per hour. For lithography scanners, throughput is a core performance figure.

## Maintenance strategies
- **Reactive**: fix after failure. Causes unplanned downtime.
- **Preventive**: service on a fixed schedule. Can replace parts that still had life left.
- **Predictive**: use sensor data and models to estimate when a part will fail and service it just in time.

## ML for equipment health
Anomaly detection models (for example isolation forests, autoencoders, or statistical baselines) learn normal sensor behavior and flag drift. Remaining useful life (RUL) models estimate time to failure from degradation trends. Combining equipment logs, alarms, and sensor traces gives better predictions than any single source.

## Tool matching
When many tools run the same step, small differences between them cause variation. Tool matching compares tools on the same metrics and adjusts them so they produce equivalent results.
