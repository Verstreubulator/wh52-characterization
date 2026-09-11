# Characterizing the Ecowitt WH52 Soil Sensor

Andreas Braunlich
September 2026

## Purpose

The purpose of this document is to describe what the Ecowitt WH52 soil sensor
appears to be, how it appears to work, and how it behaves in practice. It is
written from measurements taken on eight units operating at 915 MHz in northern
Idaho, most of them in service since July 2026.

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
| [data/captures/](data/captures/) | Raw radio captures, for checking the decode itself |

## Summary of findings

The WH52 reports soil moisture, soil temperature and electrical conductivity
over a 915 MHz radio link, running from a single AA cell. Beyond that, the
findings that seem most worth recording are these.

**Each probe is individually calibrated, and the differences are substantial.**
Four units measured across the same five moisture levels produced four different
conversion curves, with slopes spanning 9.82 to 10.39 counts per percent and zero
points spanning 604 to 635. In a single stirred solution the same four units
reported conductivity values 11 percent apart. Readings from different units are
not directly comparable without accounting for this.

**Neither end of the moisture scale is a soil condition.** Our data suggests 100
percent corresponds to a dielectric permittivity of roughly 75, which is water, and
0 percent to roughly 1.8, which is a little above air. Dry soil reads a few
percent, not zero, and field capacity falls well below the top of the scale.

**Conductivity measurement is auto-ranging.** The sensor moves through at least
ten gain ranges as conductivity rises, and reports which one it is using. The
indicator keeps changing after the conductivity reading itself has hit its
ceiling, so it is not derived from the transmitted value, and it is independent
of the arithmetic carry in how that value is packed. The conversion constant in
common use has only ever been checked in the lowest range.

**The 20-bit conductivity arithmetic is verified.** Raw captures taken either
side of the boundary locate it to within 11 µS/cm of where the arithmetic says
it should be. The captures cover every carry value the hardware can produce —
a fourth is impossible, because the 10,000 µS/cm limit stops the count 5,947
short of what it would need. The capture files themselves are included, so the
decode can be checked without any of our sensors.

**Conductivity is capped at 10,000 µS/cm.** This is a product limit rather than a
limit of the data field, which has unused headroom.

**Physical contact with the soil dominates every other source of error.** One
probe read 7 percent and then 14 percent in the same soil, before and after being
pressed in firmly.

**A reading taken in air is not a stable reference.** Carrying the same sensors to
a different room moved two of them by about two percentage points, while within a
session they repeat to within one count. In air the sensing volume includes the
bench, the packaging and the neighbouring sensors. A sensor freshly out of water
does read high, but we cannot say by how much or for how long, because our sessions
differed in placement as well as in time.

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
sat at nearly the same voltage, so a coincidence looked like a correlation. He
located it at byte 20 by looking at a wider range of voltages, renamed the
conductivity field, and wrote the fix himself as pull request 3668. He owns WH52
units on 868 MHz in Europe, which makes him the only person I know of who could
check any of this on different hardware.

**Benjamin Larsson (merbanan)** and the rtl_433 contributors wrote and maintain
the software that makes any of this possible, and reviewed the decoder that
started it. **gdt** reviewed the battery correction.

**Peter (pbkhrv)** maintains the rtl_433 Home Assistant add-on used for every
radio capture here.

The analysis, capture tooling and much of the reasoning were carried out with
**Claude (Anthropic)**. Several of the mistakes in [errata.md](errata.md) are its
own, and it found and corrected most of them.

## License

Documentation and data are released under CC BY 4.0. The parser in `tools/` is
released under the GPL, version 2 or later, to match rtl_433.
