# Characterizing the Ecowitt WH52 Soil Sensor

Andreas Braunlich
September 2026, revised October 2026

## Purpose

The purpose of this document is to describe what the Ecowitt WH52 soil sensor
appears to be, how it appears to work, and how it behaves in practice. It is
written from measurements taken on eight units operating at 915 MHz in northern
Idaho, most of them in service since July 2026. Since October 2026 it also draws on
measurements of five 868 MHz units made by vgabor99, which are kept in their own
folder and credited wherever they are used.

This is not a specification. Ecowitt publishes very little about this sensor, no
teardown appears to exist, and the manufacturer has not been consulted. What
follows is what we were able to observe from outside the device, together with
the inferences we drew and the reasoning behind them.

The material is separated into three kinds of statement, and the separation is
deliberate:

- **What we measured.** Numbers taken from the sensors, with the conditions they
  were taken under. Most were replicated across four units.
- **What the specifications suggest.** Inferences drawn from published
  documentation for similar hardware. These depend on the assumption that the
  WH52 shares a sensing module with those products, which we have not proven.
- **What our data suggests.** Inferences drawn from our own measurements. These
  are our own reasoning and should be read as such.

Where a claim rests on a single probe, a single reading, or an assumption, it is
said so in the text.

## Contents

| File | Contents |
|---|---|
| [hardware.md](hardware.md) | What the sensor probably contains, and the limits of that inference |
| [behavior.md](behavior.md) | What we measured, and under what conditions |
| [interpretation.md](interpretation.md) | What our data suggests, with the evidence for each claim |
| [decoder.md](decoder.md) | The byte layout, and how to read the raw fields yourself |
| [errata.md](errata.md) | Conclusions we reached and later had to withdraw |
| [sources.md](sources.md) | References |
| [data/](data/) | The raw frames behind every number in this document |
| [data/vgabor99-868-20261011/](data/vgabor99-868-20261011/) | vgabor99's 868 MHz measurements, unchanged, with their method |
| [tools/verify_claims.py](tools/verify_claims.py) | Recomputes every figure from that data |
| [tools/wh52_868_analysis.py](tools/wh52_868_analysis.py) | Prints a fuller summary of vgabor99's files |
| [data/captures/](data/captures/) | Raw radio captures, for checking the decode itself |

## Summary of findings

The WH52 reports soil moisture, soil temperature and electrical conductivity
over a 915 MHz radio link, running from a single AA cell. Beyond that, the
findings that seem most worth recording are these.

**Each probe is individually calibrated, and the differences are substantial.**
Four units measured across the same soil levels produced four different conversion
curves, with slopes spanning 9.86 to 10.37 counts per percent and zero points
spanning 607 to 640. Readings from different units are not directly comparable without accounting for
this, and four readings from two months earlier land on the same lines, so the
conversion is a fixed property of each unit rather than a state it was in. In a
single stirred solution the same four units reported conductivity values 11 percent
apart, though we have only that one clean observation of it. Five 868 MHz units
measured by vgabor99 in one solution differed by 11 to 21 percent.

**Neither end of the moisture scale is a soil condition.** Our data suggests 100
percent corresponds to a dielectric permittivity of roughly 75, which is water, and
0 percent to roughly 1.8, which is a little above air. Dry soil reads a few
percent, not zero, and field capacity falls well below the top of the scale.

**Conductivity measurement is auto-ranging.** The sensor moves through at least
thirteen gain ranges as conductivity rises, and reports which one it is using. We
saw ten. vgabor99's five units all passed through ranges 1 to 11 in order, and
some reached 12 and 13 at the ceiling. The first change comes at
different points on different units: 310 µS/cm on three of theirs, and above
350 on three of ours. The
indicator takes two different values while the conductivity reading sits at its
ceiling, so it does not appear to be derived from the transmitted value. On our
data that rested on a single frame we cannot check; vgabor99's checked frames show
the indicator rising three times while the reading stayed at the ceiling. It is independent of the arithmetic
carry in how that value is packed. What the indicator is counting,
and where its thresholds fall, we could not work out.

**Conductivity is reported in steps of about 10 µS/cm.** vgabor99's readings fill
every step of that grid from 5 to 350 µS/cm, and ours fall on the same grid. A
change smaller than about 10 µS/cm is not resolved.

**Not every unit's raw moisture value is a measurement.** On two newer 868 MHz
units the raw value is the percentage re-encoded, at least at 0 and 95 to 100
percent, the only values they reported, so there it adds nothing. The same two
units differ from all the others in bytes 14 and 21, which probably mark a
revision.

**In water, salt lowers the moisture reading from the first doses**, on
vgabor99's three older units: from about 16 µS/cm, steepest at low conductivity,
and reversing well below the 10,000 µS/cm ceiling. Our own data had too few
readings at low conductivity to see it. None of this says what happens in soil.

**The 20-bit conductivity arithmetic is verified.** Raw captures taken either
side of the boundary locate it to within 11 µS/cm of where the arithmetic says
it should be. The captures cover every carry value the hardware can produce —
a fourth is impossible, because the 10,000 µS/cm limit stops the count 5,947
short of what it would need. The capture files themselves are included, so the
decode can be checked without any of our sensors.

**Conductivity is capped at 10,000 µS/cm.** This is a product limit rather than a
limit of the data field, which has unused headroom.

**Where a probe sits matters more than which probe it is.** Four units placed in
the same material at the same time reported readings 6 to 8 percentage points
apart, at every level. That spread is not the per-unit conversion, which cancels.

**A reading taken in air is not a stable reference.** Carrying the same probes to
a different place moved two of them by about two percentage points, while within a
session they repeat to within one count. In air the sensing volume includes the
bench, the packaging and the neighbouring probes. vgabor99's older units gave the same air
reading to within a few counts in two different arrangements, hours apart.

**We could not measure a temperature effect on the moisture reading.** Fitting
every dry-air frame gives slopes that disagree in sign between units, with scatter
larger than any effect. An earlier version of this document gave a figure; it is
withdrawn.

## Checking it yourself

Every figure in these documents should be recomputable from the CSV files in
[data/](data/). There is a script that does it:

```
python tools/verify_claims.py
```

It reports one line per claim and exits non-zero if any fails. It exists because we
published three numbers that no file supported, and reading the documents carefully
had not caught any of them. Anything it does not cover is either a citation, or a
judgement we have tried to label as one.

## A note on confidence

We are not soil scientists and we do not have laboratory equipment. Conductivity
was raised with table salt and estimated by the sensors themselves; there was no
external reference instrument. Moisture levels were described qualitatively and
verified against published permittivity values rather than against gravimetric
samples. The measurements are repeatable and internally consistent, and we have
tried to be clear about what they do and do not establish, but they are the work
of a homeowner with a software radio rather than a laboratory.

Corrections are welcome, and the raw data is included so that anyone who wants to
check the reasoning can do so.

## Acknowledgements

This work rests on other people's, and the parts that are not mine should be
easy to find rather than buried.

**vgabor99** corrected the battery decode. The original decoder placed battery
voltage at byte 15, which was wrong; all four of the units it was derived from
sat at nearly the same voltage, so a coincidence looked like a correlation. They
located it at byte 20 by looking at a wider range of voltages, renamed the
conductivity field, and wrote the fix themselves as pull request 3668. They run the
868 MHz European variant of the sensor (rtl_433 pull request 3636, comment), which
made them the only person we knew of who could check any of this on different
hardware. Until then, everything here came from 915 MHz units of one garden.

vgabor99 has since done exactly that, twice. In September they showed on two
868 MHz units that byte 15 does not change with battery voltage (see the errata).
In October they ran five 868 MHz units through a distilled-water salt series and an
open-air check, and sent the files
([merbanan/rtl_433_tests#519](https://github.com/merbanan/rtl_433_tests/pull/519#issuecomment-6112095570)).
That dataset found ranges 9 to 11, the 10 µS/cm steps, the newer units' re-encoded
moisture value and the low-conductivity effect, and it corrected three things we
had published. It is included here, unchanged, with their permission, in
[data/vgabor99-868-20261011/](data/vgabor99-868-20261011/). The measurements are
theirs; the analysis, and any mistakes in it, are ours.

**Benjamin Larsson (merbanan)** and the rtl_433 contributors wrote and maintain
the software that makes any of this possible. **Christian Zuckschwerdt** reviewed
the decoder that started this, and later corrected the test expectations after the
battery fix landed. **gdt** reviewed and merged the battery correction.

**Peter (pbkhrv)** maintains the rtl_433 Home Assistant add-on used for every
radio capture here.

The analysis, capture tooling and much of the reasoning were carried out with
**Claude (Anthropic)**. Several of the mistakes in [errata.md](errata.md) are its
own, and it found and corrected most of them.

## License

Documentation and data are released under CC BY 4.0. The parser in `tools/` is
released under the GPL, version 2 or later, to match rtl_433.
