# Semiconductor Yield Basics

Yield is the fraction of manufactured units that work. Fabs track several kinds of yield:

- **Line yield**: share of wafers that survive the full process flow without being scrapped.
- **Die yield (sort yield)**: share of dies on a finished wafer that pass electrical wafer sort testing.
- **Final test yield**: share of packaged parts that pass final test.

Overall yield is roughly the product of these stages, so a small loss at each step compounds.

## Yield models
Yield models link defect density to die yield.

- **Poisson model**: Y = exp(-A * D0), where A is die area and D0 is defect density (defects per cm^2). It assumes defects are randomly and independently spread, so it tends to underestimate yield for large dies.
- **Murphy model**: averages over a distribution of defect densities across the wafer, giving higher predicted yield than Poisson for large dies.
- **Negative binomial (Stapper) model**: Y = (1 + A * D0 / alpha)^(-alpha). The clustering parameter alpha captures how defects cluster; small alpha means strong clustering, and as alpha grows large the model approaches Poisson.

Because yield falls quickly with die area, large chips such as GPUs are especially sensitive to defect density. Reducing D0 is one of the main levers for profitability in a fab.

## Yield learning
New process nodes start with low yield and improve through yield learning: finding defect sources, fixing tools and recipes, and tightening process windows. The speed of this learning curve strongly affects time to market and cost.
