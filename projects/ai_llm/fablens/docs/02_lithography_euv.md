# Lithography and EUV

Lithography prints circuit patterns onto a wafer coated with light-sensitive photoresist. A scanner projects the pattern from a photomask (reticle) through reduction optics, typically shrinking it 4x.

## Resolution
Resolution follows the Rayleigh criterion: CD = k1 * lambda / NA, where CD is the smallest printable feature (critical dimension), lambda is the light wavelength, NA is the numerical aperture of the optics, and k1 is a process factor. Smaller features need shorter wavelength, larger NA, or lower k1.

## DUV
Deep ultraviolet (DUV) scanners use 248 nm (KrF) or 193 nm (ArF) light. ArF immersion lithography places water between the lens and the wafer to raise NA to about 1.35. To print features below its single-exposure limit, chipmakers use multi-patterning, which adds steps, cost, and overlay risk.

## EUV
Extreme ultraviolet (EUV) lithography uses 13.5 nm light. The light is produced by hitting tiny tin droplets with a high-power CO2 laser to create a plasma. Because almost all materials absorb EUV light, the system runs in vacuum and uses reflective mirrors with molybdenum/silicon multilayer coatings instead of lenses. Masks are reflective too.

Current EUV systems use NA 0.33. High-NA EUV raises NA to 0.55 to print smaller features in a single exposure, using anamorphic optics that demagnify differently in the two directions.

ASML is the only supplier of EUV scanners, which makes them a critical part of the global chip supply chain.
