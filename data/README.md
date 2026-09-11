# Data

The raw measurements behind every number in this repository. Both files were
recorded on September 9, 2026, from Ecowitt WH52 sensors operating at 915 MHz in
Coeur d'Alene, Idaho.

Five sensors appear. Four are identified by the position they occupy in a back
lawn, where they had been installed since July and from which they had been
temporarily removed for construction work. The fifth, `desk_spare`, is an unused
unit that sat indoors throughout and was never placed in soil or salt water; it
appears only incidentally.

Frames were captured with the flex decoder described in
[../decoder.md](../decoder.md) and parsed with
[../tools/wh52_parse.py](../tools/wh52_parse.py).

Both files are decoded frames rather than radio recordings. The recordings are in
[captures/](captures/), which has its own description; they were taken later the
same day and cover conditions these two files do not, including a properly dry
reference and the full span of the conductivity arithmetic.

The captures in [captures/](captures/) additionally include three sensors that
stayed in service throughout: `front_lawn_en`, `front_lawn_es` and `pear_tree`.

| Sensor | Device identifier |
|---|---|
| back_lawn_ne | 005b45 |
| back_lawn_nw | 0058ac |
| back_lawn_se | 005995 |
| back_lawn_sw | 005cb5 |
| desk_spare | 0070f4 |

## moisture-sweep-20260909.csv

Readings taken while moving all four back lawn sensors through six conditions:
open air, soil damp only with morning dew, ordinary garden soil not watered
overnight, soil from a sprinkler-watered area, thoroughly saturated soil, and
full submersion in water.

At each level all four sensors were placed in the same material, pressed in
firmly, and left at least three minutes. Readings were taken once the transmit
interval returned to roughly 70 seconds, which indicates the sensor considers the
reading stable.

| Column | Meaning |
|---|---|
| level | The condition described above |
| probe, device_id | Which sensor |
| moisture_pct | As reported by the sensor |
| m_raw | The raw measurement, 12 bits |
| temp_C, ec_uS_cm | As reported by the sensor |
| notes | Settling window, or why a value is missing |

One value is absent. The sensor `back_lawn_se` produced no raw frame at the
ordinary-soil level, because the radio saving the raw captures hears that
particular unit poorly. Its percentage is recorded and its raw value is not.

## reference-frames-202607.csv

Four frames from July 2026, two months before everything else here. They are the
decoded contents of `gfile001` and `gfile002`, the two sample captures we
contributed to `merbanan/rtl_433_tests` as pull request 508, and they are included
because the conversion fit in [../behavior.md](../behavior.md) uses one point per
sensor from them.

They matter more than four points normally would. They were taken two months
earlier, in a different season, by a different person doing a different job, and
they land on the same lines as the September data. That is the only evidence we
have that a sensor's conversion is a fixed property rather than something it
happened to be doing that morning.

The full payloads are here so nothing external is needed to check them.

## moisture-percent-20260909.csv

70 readings from the four back lawn sensors between 07:03 and 07:28 on September 9,
covering the first half of the moisture sweep. This came from the MQTT stream rather
than from the radio logs, so it carries the reported percentage and temperature but
**no raw value**. It is here because it is the only record of that window, and
because the insertion sequence quoted in [../behavior.md](../behavior.md) is in it.

## moisture-frames-20260909.csv

338 individual frames from the four back lawn sensors between 07:15 and 09:14 on
September 9, covering the second half of the moisture sweep. Unlike the file above,
which records one settled value per sensor per level, this is every frame the radio
decoded in that window.

It exists because the per-sensor conversion table in
[../behavior.md](../behavior.md) could not be reproduced from the settled values
alone; six points per sensor is not enough to pin a line down, and the published
table had been computed from a larger set that was never included here. These are
those frames. With them the fit reproduces.

Two warnings. This came from the filtered logger described below, so it is not
usable for anything concerning byte 11. And the sweep was still in progress, so
consecutive frames from one sensor are not independent samples of a fixed
condition; they are a sensor tracking soil that was being watered.

| Column | Meaning |
|---|---|
| time | Local time, Pacific |
| probe | Which sensor |
| moisture_pct, m_raw | As reported, and the raw measurement |
| temp_C, ec_uS_cm | As reported |

## conductivity-series-20260909.csv

1,016 frames recorded between 07:15 and 10:29 while conductivity was raised from
tap water at 319 µS/cm to the sensor's ceiling using ordinary table salt, and
lowered again by dilution to fill gaps in the range.

| Column | Meaning |
|---|---|
| time | Local time, Pacific |
| probe, device_id | Which sensor |
| moisture_pct, m_raw | As reported, and the raw measurement |
| temp_C, ec_uS_cm | As reported |
| byte11 | The conductivity range indicator, whole byte |
| ec_raw | The 20-bit conductivity count |
| byte8 | Carries the high bits of both the moisture and conductivity values |
| logger | Which capture program produced the row, see below |

### Two loggers, and a bias in the first

The rows are not homogeneous, and the difference matters.

**Two loggers overlapped, so the file contains duplicates.** 1,016 rows, 798
distinct transmissions; 169 transmissions were heard by both loggers and 49 logged
twice by one of them. Deduplicate on time, probe and values before counting
anything.

**Logger 1**, marked `1 (filtered)`, ran from 07:15:57 to 09:14:07. It discarded any
frame where byte 11 was not `0x16`, on the mistaken assumption that the byte was
constant and could serve as a validity check. It also did not record `ec_raw` or
`byte8`, so those columns are empty for its rows.

**Every row from logger 1 therefore reports byte 11 as `0x16` by construction.**
The absence of other values during that period is not evidence that none
occurred. In fact some did, and were thrown away. This is described in
[../errata.md](../errata.md).

**Logger 2**, marked `2 (unfiltered)`, ran from 08:00 to 10:29 and validated
frames on the checksum alone. Its rows carry all fields and no range filtering.
Any analysis of byte 11 should use logger 2 rows only.

### Caveats on the conductivity values

Salt quantities were not measured, and there was no reference conductivity meter.
The conductivity figures are the sensors' own readings. That is sufficient for the
questions asked of this data, which concern the sensor's internal behavior, but it
is not sufficient to calibrate the conversion itself.

Temperature across the valid rows spans 12.5 °C to 37.7 °C as the sensors moved
between outdoors and indoors and sat in the sun. This turned out to affect where the range
indicator switches, and is discussed in
[../interpretation.md](../interpretation.md).

One frame decodes to a temperature of 89.4 °C, a conductivity of 10 µS/cm on a
sensor lying in air, and byte 11 as `0x2c`, whose low nibble is 12 where every
other row in the file has 6. It passes the checksum and fails the CRC. It is left in deliberately, as an example
of why both check bytes should be verified.
