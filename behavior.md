# What We Measured

Everything in this section is observation. The conditions are given so that the
numbers can be judged, and the raw frames are in [data/](data/).

## Method

Four sensors were run through a sequence of moisture levels on September 9, 2026,
while they were out of the ground during construction work. The levels were open
air, soil damp only with morning dew, ordinary garden soil that had not been
watered overnight, soil from an area watered by sprinklers, thoroughly saturated
soil, and finally full submersion in water. All four sensors were placed in the
same material at each level, pressed in firmly, and left for at least three
minutes before readings were taken.

Conductivity was then raised in stages using ordinary table salt, from tap water
at 319 µS/cm to the sensor's ceiling, and afterward lowered again by dilution to
fill gaps. Salt quantities were not measured. There was no external conductivity
meter; the conductivity values are the sensors' own readings.

The soil is rocky, with stones up to about an inch, and the top two inches have
been amended with compost and manure. It was noted during the work that the soil
is still water-repellent, which means moisture is unlikely to have been evenly
distributed within any sample.

Frames were captured over the radio using a flex decoder, described in
[decoder.md](decoder.md). A total of 1,016 valid frames were recorded during the
conductivity work and a further set during the moisture sweep.

## Moisture

### Each sensor has its own conversion curve

The sensors transmit both a raw measurement and a percentage. Fitting the raw
value against the reported percentage for each unit across the full sweep gives
four different straight lines.

| Sensor | Points | Counts per 1 percent | Raw at 0 percent | Raw at 100 percent | Largest residual |
|---|---|---|---|---|---|
| ne | 37 | 10.37 | 624 | 1661 | 0.52 points |
| nw | 28 | 10.14 | 618 | 1633 | 0.46 points |
| se | 32 | 10.06 | 607 | 1613 | 0.51 points |
| sw | 38 | 9.86 | 640 | 1625 | 0.53 points |

The fit uses every unclamped frame in
[data/moisture-frames-20260909.csv](data/moisture-frames-20260909.csv), the settled values in
[data/moisture-sweep-20260909.csv](data/moisture-sweep-20260909.csv), and one point per sensor from
[data/reference-frames-202607.csv](data/reference-frames-202607.csv), which is the
decoded contents of the two July captures contributed to `rtl_433_tests`. Clamped readings, meaning anything at 0
or 100 percent, are excluded because the raw value keeps moving there while the percentage does not.
Those July points were taken two months earlier and land on the same lines, which is worth more than the
residuals: the conversion is a stable property of each unit rather than a state it was in that morning.

Each line is straight to better than half a percentage point across a span of 0 to
96 percent, which is the limit of what the sensor's whole-number output can
resolve. There is no curvature to be found.

The differences between units are larger than the fit error. Slopes differ by 5.2
percent and zero points by 33 counts, which is about three percentage points of
moisture. Two sensors sitting four counts apart in the same soil reported readings
three percentage points apart, and did so again two hundred counts higher up the
scale.

This cannot be explained by the soil differing between spots. A sensor's raw value
and its percentage come from the same reading of the same place, so any local
difference moves both together along that sensor's own line.

### The percentage saturates before the raw value does

Submerged in water, all four sensors reported exactly 100 percent while their raw
values ranged from 1646 to 1690, in each case above that unit's own fitted 100
percent point. The raw value continues to rise after the percentage has stopped.

One frame captured a sensor mid-immersion reading 96 percent at a raw value of
1593, which is an unclamped reading near the top of the range. Its fitted line
predicts 96.2 percent. A second sensor produced a similar reading later the same
morning at 1585, also reporting 96 percent.

### We could not measure a temperature effect

An earlier version of this document reported 0.53 counts per degree Celsius, from three sensors left in
air overnight. Those three pairs of readings are not in any file we kept, and the figure does not survive
contact with the data that is here.

Fitting raw against temperature over every dry-air frame in
[data/conductivity-series-20260909.csv](data/conductivity-series-20260909.csv) gives this.

| Sensor | Frames | Temperature range | Slope | Largest residual |
|---|---|---|---|---|
| ne | 48 | 14.7 to 34.7 °C | +2.47 counts/°C | 30 counts |
| nw | 41 | 19.9 to 25.5 °C | −2.14 | 29 |
| se | 74 | 16.4 to 24.0 °C | +0.71 | 28 |
| sw | 50 | 14.4 to 35.2 °C | +0.94 | 26 |

The slopes disagree with each other in magnitude and in sign, and the scatter around each line is about
thirty counts, which is three percentage points. **There is no temperature coefficient to be had from
this data.** The next section explains why the scatter is that large.

We are not claiming the sensor is insensitive to temperature. It is a reasonable thing to expect, the
manufacturer's module documents temperature compensation for conductivity, and our own conductivity
work is consistent with a 2 percent per degree correction there. We are saying only that we cannot
measure an effect on the moisture reading, and that nobody should take a number from us for it.

### The air reading is not reproducible

The reason the scatter above is thirty counts is that a reading taken in air is not one condition.

The cleanest evidence is two sessions fifteen minutes apart on September 10. Both were a full day after
the sensors had last been wet, both indoors, and the reported temperatures differ by less than three
degrees. Between them the sensors were picked up and carried to a different place.

| Sensor | Before | After | Change |
|---|---|---|---|
| nw | 590 at 22.6 °C | 588 at 23.4 °C | −2 |
| se | 583 at 22.5 °C | 566 at 25.4 °C | **−17** |
| sw | 614 at 22.8 °C | 593 at 22.5 °C | **−21** |

Seventeen and twenty-one counts is about two percentage points.

Within either session the same sensor barely moves. Four frames from `se` minutes apart read 565, 566,
566, 566. An indoor spare that was never picked up read 586, 586 and 591 across both days. So this is not
noise in the measurement; it is the measurement correctly reporting that its surroundings changed.

In hindsight this is what the instrument is for. It responds to the permittivity of whatever is in its
sensing volume, and in air that includes the bench it is lying on, its packaging, and the other three
sensors beside it.

**An air reading is worth about twenty counts, or two percentage points, unless the physical arrangement
is fixed and repeated.** That is the same order as the spread between units. Doing better would need the
sensor held clear of surfaces in a jig it returns to every time, and we have not built one.

### What we tried to conclude from the dry-air work, and could not

We rinsed the sensors after the conductivity work and read them in air over two days, intending to find
out whether a sensor that has been wet reads high, and for how long. We published two answers in turn and
both are withdrawn. They are in [errata.md](errata.md), and the short version is here because the reason
we failed is more useful than the answers were.

The readings we have are these, as measured, with no correction applied.

| Sensor | Air, never wetted | Hours after the rinse | One day later | Fifteen minutes after that |
|---|---|---|---|---|
| ne | 572 at 11.8 °C | — | — | 576 at 23.1 °C |
| nw | 575 at 12.0 °C | 630 at 37.5 °C | 590 at 22.6 °C | 588 at 23.4 °C |
| se | 564 at 11.2 °C | 614 at 36.3 °C | 583 at 22.5 °C | 566 at 25.4 °C |
| sw | 597 at 12.0 °C | 620 at 37.2 °C | 614 at 22.8 °C | 593 at 22.5 °C |
| spare, never wetted | 583 at 23.5 °C | 586 at 25.4 °C | 586 at 25.1 °C | 591 at 25.2 °C |

Every column differs from the next in two ways at once. The sensors were wet for less time, and they were
at a different temperature, and in one case they had also been moved. With no temperature coefficient and
no control over placement, none of those differences can be assigned to a cause. **A sensor freshly out
of water may well read high. We cannot show it from this.**

The design fault was ours and it is simple. We changed more than one thing between measurements, then
treated the difference as evidence about the thing we were interested in.

### Where a sensor sits matters more than what it is

Four sensors were placed in the same material at the same time, at each level of the sweep. They did not
agree.

| Level | ne | nw | se | sw | Spread |
|---|---|---|---|---|---|
| Dew-damp soil | 8 % | 10 % | 14 % | 11 % | 6 points |
| Ordinary soil | 26 | 22 | 29 | 26 | 7 |
| Sprinkler-watered | 26 | 27 | 34 | 31 | 8 |
| Saturated | 63 | 63 | 60 | 56 | 7 |

This is not the per-unit conversion. A sensor's raw value and its percentage come from the same reading
of the same spot, so a conversion error moves both together along that sensor's own line and cancels.
What is left is a real difference in what each sensor was sitting in: how firmly it went in, what it
happened to be touching, and how the water was distributed in soil that was still water-repellent.

The same effect is visible while a sensor is going into the ground. From the MQTT log, `sw` at ten-second
intervals:

```
07:15:21   0 %
07:15:31   5 %
07:15:41   9 %
07:15:51  31 %
```

It is the same mechanism as the air result above. The sensor reports the permittivity of its
surroundings, and its surroundings are decided by how it is placed.

### What the errors add up to

Only the rows we can support from the published data.

| Source | Size | Where it is shown |
|---|---|---|
| Where a sensor sits, in the same material | up to 8 points | the table above |
| Between units, at the same raw value | about 3 points | 33 counts of zero-point spread |
| Placement of one sensor in air | about 2 points | 17 to 21 counts |
| Conductivity, below 300 µS/cm | not detectable | conductivity section below |
| Temperature | not measurable | slopes disagree in sign |

An earlier version of this table led with a single sensor reading 7 percent and then 14 percent after
being pressed in firmly. That reading is in no file we kept, and we have replaced it with the four-sensor
comparison, which says the same thing and can be checked.

## Conductivity

### The reading has a floor near 5 µS/cm

Sensors in dry air report 4.7 to 5.4 µS/cm, and never lower. Air has no
conductivity to speak of, so this is the bottom of the scale rather than a
measurement, and values near 5 should be read that way.

An earlier version of this document also cited readings in distilled water. We
have no record of that measurement and have removed it.

This matters for interpreting dry soil, which also reads near 5.

### The reading is capped at 10,000 µS/cm

With enough salt added, all four sensors reported between 10,001.9 and 10,002.9
µS/cm and stayed there for five minutes. The raw values behind those readings span
24 counts, a difference of 0.01 percent.

These are sensors that disagree with each other by 11 percent at every other
level. Agreement that close is a ceiling, not a measurement.

### Units disagree with each other by about 11 percent

In one well-stirred solution the four sensors reported the following, and held the
same rank order at every level tested during the day.

| Sensor | Conductivity in one solution |
|---|---|
| sw | 4,031 to 4,051 µS/cm |
| ne | 4,061 to 4,161 |
| se | 4,415 to 4,445 |
| nw | 4,485 to 4,515 |

### The measurement auto-ranges

The sensor reports which of several gain ranges its conductivity front end is
using. Raising conductivity from 5 µS/cm to the ceiling moved this indicator
through ten distinct values.

| Range indicator | Conductivity observed | Frames | Sensors submerged |
|---|---|---|---|
| 1 | 4.7 to 360 µS/cm | 665 | all four |
| 2 | 907 to 1,079 | 32 | all four |
| 3 | 1,331 to 2,028 | 44 | all four |
| 4 | 2,273 to 2,979 | 32 | all four |
| 5 | 3,101 to 3,576 | 33 | all four |
| 6 | 4,031 to 4,990 | 84 | all four |
| 7 | 4,700 to 5,357 | 54 | all four |
| 8 | 6,040 | 1 | one |
| 12 | 10,007 | 1 | one |
| 13 | 10,001 to 10,004 | 69 | all four |

Ranges 9 through 11 were not observed. Conductivity was raised in a single large
step through that region and we did not return to fill it.

Range 1 counts include 665 frames, but 260 of those come from a capture program
that discarded frames where the indicator was not 1. See [data/](data/) for why
that portion of the record is not evidence of anything.

**The indicator continues to change after the conductivity reading has stopped.**
At the 10,000 µS/cm ceiling, where all four sensors report the same clamped value,
the indicator was observed at 12 and then at 13. Whatever it is counting is still
rising after the transmitted conductivity has saturated. Range 8 appears once in
our record, at 6,040 µS/cm, which is below the ceiling; an earlier version of this
document listed it among the clamped readings by mistake.

The indicator does not rescale the conductivity value. The underlying count rises
continuously through every transition, with no jump or change of slope. Range four
ends at 76,249 counts and range five begins at 79,386.

Each sensor switches ranges at its own conductivity value, which follows from the
units disagreeing with each other by 11 percent.

The ranges overlap when expressed as reported conductivity. Range 6 was observed
as high as 4,990 µS/cm and range 7 as low as 4,700. This is discussed in
[interpretation.md](interpretation.md).

### Conductivity depresses the moisture reading, above a threshold

With sensors fully submerged, so that water content could not change, raising
conductivity lowered the reported moisture.

| Sensor | Raw at 280 µS/cm | at 1,000 | at 1,400 | at 2,500 | Total change |
|---|---|---|---|---|---|
| ne | 1689 | 1582 | 1512 | 1421 | −268 |
| se | 1649 | 1573 | 1473 | 1406 | −243 |
| sw | 1671 | 1574 | 1527 | 1442 | −229 |
| nw | 1595 | 1517 | 1477 | 1393 | −202 |

Below about 300 µS/cm the effect could not be detected. One sensor, which was the
only one not saturated at the top of its scale in clean water, read 1609 at 4.8
µS/cm and 1623 at 309 µS/cm. That is a small movement in the opposite direction
and is within the noise of the measurement.

Our own soil measures between 5 and 230 µS/cm, which places it entirely within the
region where we could not detect the effect.

We would not extend these numbers to soil. The measurements were taken in water,
and the published literature reports the opposite sign in soil. This is discussed
in [interpretation.md](interpretation.md) and in [errata.md](errata.md).

## Raw signal captures — verifying the conductivity arithmetic

A second session on the afternoon of September 9 recorded raw IQ captures at controlled
conductivities, specifically to test the parts of the conductivity decode that ordinary readings never
reach. Conductivity was raised from tap water with table salt in four stages while all four back lawn
sensors sat in the same cup, and a fifth condition was captured afterwards with the sensors rinsed and
dry. Seventy-four capture files were kept, of which seventy-two contain at least one frame passing both check
bytes. They are in [data/captures/](data/captures/) with their decodes in `INVENTORY.csv`. Thirty of them
are the dry-air work described above.

The conductivity value is a 20-bit number assembled from three bytes, and the top four bits live in the
same byte as part of the moisture measurement. Those top bits are zero below 2,560 µS/cm, which is above
anything soil produces — so in normal use that part of the arithmetic is never exercised, and an error
there would be invisible.

| Range indicator | Carry bits | Frames | Conductivity |
|---|---|---|---|
| 1 | 0 | 49 | 5 µS/cm |
| 4 | 0 | 7 | 2,191 – 2,333 |
| 5 | **1** | 4 | 3,405 – 3,739 |
| 7 | **1** | 8 | 4,940 – 5,112 |
| 7 | **2** | 2 | 5,122 – 5,132 |
| 13 | **3** | 4 | 10,002 – 10,008 |

Moisture across the set spans 0 % to 98 %, and the raw moisture measurement 565 to 1,603, so the whole
of the reported scale is represented.

### The carry boundary, located to 11 µS/cm

The first four bits of the carry change when the underlying count crosses 131,072, which is exactly
5,120.0 µS/cm. Because the four sensors disagree with each other by about 11 %, they straddled that
boundary while sitting in the same cup:

| Sensor | count | conductivity | carry bits |
|---|---|---|---|
| `back_lawn_nw` | 130,854 | 5,111.5 µS/cm | 1 |
| `back_lawn_se` | 131,131 | 5,122.3 | 2 |

277 counts apart, taken seconds apart in one solution, **and the theoretical boundary falls between
them**. The disagreement between units, which is a nuisance everywhere else, is useful here.

### The range indicator and the carry are independent

Range 7 contains frames with carry bits of both 1 and 2. The range did not change when the count crossed
the 16-bit boundary.

These two mechanisms are easy to conflate, since both change as conductivity rises. They are not related:
the range indicator reflects a switch on the analogue side, and the carry is arithmetic in how the value
is packed.

### Carry bits of 4 cannot occur

A carry value of 4 would require a count of 262,144, which is 10,240 µS/cm. The sensor clamps at 10,000,
and the highest count we ever recorded is 256,197 — short by 5,947.

**So 3 is the maximum the hardware can produce**, and captures covering 0, 1, 2 and 3 cover every value
that exists rather than merely a good sample of them.

## Radio behavior

**Each reading is sent twice, 43 milliseconds apart.** Every raw capture that contains a decodable frame
contains it twice, with an identical payload. Measured across 25 pairs the interval is 43.2 to 43.4
milliseconds, which is tight enough to be a fixed firmware delay rather than anything adaptive. Neither
copy carries a flag distinguishing it from the other, so a receiver sees the same reading arrive twice
and should expect that.

The sensors transmit approximately every 70 seconds when readings are stable, and
approximately every 10 seconds while a reading is changing. The return to the
slower interval is a reliable indication that a sensor has settled, and we used it
as the stopping condition throughout the moisture sweep.
