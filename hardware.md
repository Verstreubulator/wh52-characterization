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

## Why we looked outside Ecowitt

Three attempts to find internal details produced nothing.

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
| Moisture | 0 to 100 percent, FDR | FDR, 0 to 100 percent |
| Probe material | Flame-retardant epoxy resin | FR-4 epoxy |
| Temperature compensation | Built in, coefficient adjustable, default 2 percent | Behavior consistent with 2 percent |

The temperature encoding is the detail that first drew our attention. Our sensors
transmit temperature as an unsigned value scaled by 0.1 with 40 subtracted, which
is exactly how one would encode a range of −40 to +80 °C without a sign bit. That
range is the published specification for this module family, and it is unlikely to
be a coincidence.

The conductivity ceiling is the second. Our four probes clamp at 10,000 µS/cm,
which matches the module specification, while the data field itself has room for
values four times larger. A limit set by specification rather than by field width
suggests the constraint comes from the sensing element.

The published register map for this module family also documents an EC temperature
compensation coefficient with a default of 2 percent per degree Celsius (Seeed
Technology, 2020). Our own measurements are consistent with that value, which is
discussed in [interpretation.md](interpretation.md).

## Where the hypothesis breaks down

The commodity module encodes temperature as a signed 16-bit value scaled by 0.01,
with no offset. Our sensors use an unsigned value scaled by 0.1 with a −40 offset.
These are different encodings of the same physical range.

This suggests the WH52 is not a Modbus module with a radio bolted to it. It is
more likely that Fine Offset uses the same sensing element and analog front end
with their own firmware, re-encoding the measurements for a shorter radio frame.
That is a common arrangement, but we cannot demonstrate it.

The commodity module also exposes several fields the WH52 does not transmit,
including a dielectric permittivity reading, salinity, total dissolved solids, and
a soil-type selector offering separate calibration curves for mineral, sandy, clay
and organic soils. If the WH52 shares the sensing element, those capabilities
likely exist inside it and are simply not sent over the radio.

## What would settle it

Opening a unit and photographing the board would answer the question in a few
minutes. We have not done this, because all eight of our sensors are in service
and we are unwilling to sacrifice one.
