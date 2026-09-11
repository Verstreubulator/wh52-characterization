# What the WH52 Probably Contains

This section is inference. We have not opened a WH52, and everything below rests
on published specifications for other products and on the behavior we observed.
It should be read as a reasonable hypothesis rather than an established fact.

## What Ecowitt publishes

Ecowitt describes the WH52 as a three-in-one soil sensor measuring moisture,
temperature and electrical conductivity. The published details are sparse. The
measurement method is given as frequency domain reflectometry (FDR), the probe
material as FR-4 glass-reinforced epoxy, and the housing as ABS. A built-in
thermistor measures soil temperature, and conductivity is measured across a pair
of electrodes (Ecowitt, n.d.).

The sensor runs from a single AA cell. Our units report battery voltages between
1.48 and 1.62 volts, consistent with an alkaline cell in normal service.

The battery compartment is sealed twice, with a cap inside the outer cap. We
looked because water ingress was a candidate explanation for sensors reading wet
in air after a rinse. All four had been held under a running hot tap and all four
were dry inside. Whatever is causing that offset is on the blades, not in the
housing.

We have not tested the seal in any deliberate way, and this says nothing about how
it behaves after a few winters buried in wet soil.

## Why we looked outside Ecowitt

Two attempts to find internal details produced nothing.

No teardown of the WH52 appears to exist. Searches of teardown sites, electronics
forums and the rtl_433 project history returned no photographs or component
identifications.

The United States FCC publishes internal photographs for radio devices as a
condition of certification. Fine Offset Electronics holds grantee code WA5, and
filings exist for the WH51, WH53, WH31, WH32, WH40 and many other products. We
found no filing for the WH52 under any identifier we could locate. For the WH51,
which is the closest sibling, internal photographs are published but the schematic
and block diagram are marked confidential and are not available (FCC, n.d.).

The manufacturer has not been contacted.

## The commodity module hypothesis

A category of soil sensor is sold openly by several vendors under names such as
S-Temp&VWC&EC-02 and S-Soil MTEC-02. These are RS-485 Modbus devices rather than
radio devices, but their published specifications match the WH52 closely.

| Specification | Commodity module | Our WH52 measurements |
|---|---|---|
| Temperature range | −40 to +80 °C | Encoded with a −40 offset |
| Conductivity range | 0 to 10,000 µS/cm | Hard ceiling at 10,000 µS/cm |
| Moisture | 0 to 100 percent of saturation | 0 to 100 percent |
| Temperature compensation | Built in, adjustable, register default 2 percent per °C | Behavior consistent with 2 percent |

The manual does not say how the module measures moisture. It says only that the
method "is in line with international standards", so the comparison above is of
range, not of technique.

The temperature encoding first drew our attention, and on checking it turned out to
carry no weight. Our sensors transmit temperature as an unsigned value scaled by 0.1
with 40 subtracted. So do the WH5, WH24, WH25, WH32, WH40 and WH0530, none of which
contain a soil module: `fineoffset.c` applies the same `(raw − 400) × 0.1` to all of
them. It is Fine Offset's house convention, not evidence of a shared sensing
element. The comments in that file give the resulting range as −40 to +60 °C, and
Ecowitt's own WH52 manual specifies −40 to +60, not the module's −40 to +80.

What remains is the conductivity ceiling.

The conductivity ceiling is the second. Our four probes clamp at 10,000 µS/cm,
which matches the module specification, while the data field itself has room for
values four times larger. A limit set by specification rather than by field width
suggests the constraint comes from the sensing element.

The published register map for this module family also documents an EC temperature
compensation coefficient at register `0x0022`, adjustable from 0 to 10 percent,
with a default of 2 percent (Seeed Technology, 2020). Our own measurements are consistent with that value, which is
discussed in [interpretation.md](interpretation.md).

## Where the hypothesis breaks down

**The probes are not made of the same thing.** The module's manual gives the probe
material as an anti-corrosion alloy electrode, with flame-retardant epoxy resin as
the sealing compound. The WH52's blades are FR-4, which is a printed circuit board
laminate. An earlier version of this document had the epoxy in the matching column,
which was a misreading: it is the module's sealant, not its probe.

The commodity module encodes temperature as a signed 16-bit value scaled by 0.01,
with no offset: register `0x0000`, `-4000` to `8000` for −40.00 to 80.00 °C. Our
sensors use an unsigned value scaled by 0.1 with a −40 offset. These are different
encodings of the same physical range.

This suggests the WH52 is not a Modbus module with a radio bolted to it. It is
more likely that Fine Offset uses the same sensing element and analog front end
with their own firmware, re-encoding the measurements for a shorter radio frame.
That is a common arrangement, but we cannot demonstrate it.

The commodity module also exposes several fields the WH52 does not transmit: a
dielectric permittivity reading at register `0x0005`, salinity at `0x0003`, total
dissolved solids at `0x0004`, and a soil-type selector at `0x0020` offering
separate calibration curves for mineral, sandy, clay and organic soils. If the WH52 shares the sensing element, those capabilities
likely exist inside it and are simply not sent over the radio.

## What would settle it

Opening a unit and photographing the board would answer the question in a few
minutes. We have one spare that has never been planted, so this is a choice rather
than an impossibility. We would rather keep a working spare than have the answer,
which is worth stating plainly since it is the obvious next step and we are not
taking it.
