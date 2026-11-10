# Defect Inspection and Review

Defects are flaws that can make a die fail. Fabs inspect wafers at many steps to find them early.

## Defect types
- **Particles**: foreign material landing on the wafer.
- **Pattern defects**: bridges, breaks, missing or extra features.
- **Scratches** from handling or polishing (CMP).
- **Stochastic defects**: random printing failures in EUV caused by the small number of photons and resist chemistry effects; they become more common as features shrink.

A **killer defect** is one that causes the die to fail. Not every defect kills a die; it depends on size, location, and layer.

## Inspection tools
- **Brightfield optical inspection**: high sensitivity, good for pattern defects.
- **Darkfield optical inspection**: fast, good for particles on unpatterned or simple layers.
- **E-beam inspection**: very high resolution but slow; used for small defects and voltage-contrast checks.

## Review and classification
Inspection finds candidate defects; **defect review** (often with SEM) images them so they can be classified by type. Automatic defect classification (ADC) uses machine learning to sort review images into classes, which speeds up root-cause analysis.

## Linking to yield
Defect density by layer is combined with kill ratios to predict yield loss and to rank which process steps to fix first.
