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
[decoder.md](decoder.md). The conductivity work produced 1,016 rows, but two loggers
ran concurrently for part of it and heard many of the same transmissions, so the
rows contain 218 duplicates. **798 distinct transmissions.** Counts below are of
distinct transmissions, not rows.

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

The fit uses frames between 2 and 70 percent with conductivity below 300 uS/cm, in
[data/moisture-frames-20260909.csv](data/moisture-frames-20260909.csv), the settled values in
[data/moisture-sweep-20260909.csv](data/moisture-sweep-20260909.csv), and one point per sensor from
[data/reference-frames-202607.csv](data/reference-frames-202607.csv), which is the
decoded contents of the two July captures contributed to `rtl_433_tests`. Clamped readings, meaning anything at 0
or 100 percent, are excluded because the raw value keeps moving there while the percentage does not.
Those July points were taken two months earlier and land on the same lines, which is worth more than the
residuals: the conversion is a stable property of each unit rather than a state it was in that morning.

The largest residual on each line is about half a percentage point, the limit of
what a whole-number output can resolve, and there is no curvature to be found. The
fitted points span 2 to 64 percent on ne, 2 to 96 on nw, 2 to 61 on se and 2 to 57
on sw, so only one unit is fitted near the top and the raw-at-100-percent column is
an extrapolation for the other three.

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
values ranged from 1646 to 1669, in each case at or above that unit's own fitted
100 percent point. The raw value continues to rise after the percentage has stopped.

`back_lawn_nw` reported 96 percent three times that morning, at raw 1593, 1594 and
1585, each an unclamped reading near the top of its range. Its fitted line predicts
96.1 percent at 1593. Two other sensors also reported 96 percent, `se` at 1571 to
1574 and `sw` at 1588, which is the per-unit spread again rather than a
disagreement.

### We could not measure a temperature effect

An earlier version of this document reported 0.53 counts per degree Celsius, from three sensors left in
air overnight. Those three pairs of readings are not in any file we kept, and the figure does not survive
contact with the data that is here.

Fitting raw against temperature over every dry-air frame in
[data/conductivity-series-20260909.csv](data/conductivity-series-20260909.csv) gives this.

| Sensor | Frames | Temperature range | Slope | Largest residual |
|---|---|---|---|---|
| ne | 34 | 14.7 to 34.7 °C | +2.69 counts/°C | 31 counts |
| nw | 28 | 19.9 to 25.5 °C | −1.86 | 28 |
| se | 56 | 16.4 to 24.0 °C | +0.05 | 26 |
| sw | 31 | 14.4 to 35.2 °C | +0.79 | 26 |

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
| Conductivity, below 300 µS/cm | not detectable in our data; up to about 5 points in water in vgabor99's | conductivity section below, and the 868 MHz section |
| Temperature | not measurable | slopes disagree in sign |

An earlier version of this table led with a single sensor reading 7 percent and then 14 percent after
being pressed in firmly. That reading is in no file we kept, and we have replaced it with the four-sensor
comparison, which says the same thing and can be checked.

## Conductivity

### The reading has a floor near 5 µS/cm

Across the 32 frames we can positively place in air, being the five air rows of the
sweep and the dry-air captures, conductivity reads **4.6 to 5.2 µS/cm**. Air has no
conductivity to speak of, so this is the bottom of the scale rather than a
measurement, and values near 5 should be read that way.

Two earlier versions of this paragraph were wrong. One cited readings in distilled
water, which we have no record of taking. The other gave 4.7 to 5.4 from a pool
that included frames taken between submersions rather than in air.

This matters for interpreting dry soil, which also reads near 5.

### Out of water, the two measurements come apart

Lifted straight out of the salt solution, the moisture reading collapses within a
single transmission. At a steady 20 to 21 °C, without the sensor being moved:

```
back_lawn_se   08:24:50  raw 1406      08:26:01  raw 606   →  590 over the next 71 s
back_lawn_nw   08:02:59  raw 1517      08:04:12  raw 641   →  625 over the next 4 min
```

About eight hundred counts in roughly seventy seconds, then a slow drift of a
count or two per transmission. So a sensor that is visibly wet reads at the dry end
of the moisture scale almost immediately.

Conductivity does not follow it. Taking every frame in the conductivity series
where a sensor was out of the solution, 164 of 199 read at the floor and the other
35 range from 15 µS/cm up to 2,272, a film of solution still bridging the
electrodes. **A moisture reading near zero does not mean a sensor is dry or
clean.** Conductivity is the measurement that notices.

There is a consequence worth stating, because it cuts against a story we were
tempted by. A sensor a few minutes out of water reads 590 to 641 here, and the same
sensors after a full day of drying read 583 to 614. Those bands overlap almost
entirely. **Whatever makes a wetted sensor read high, waiting a day does not
visibly improve on waiting five minutes**, which is part of why we could not
demonstrate a drying effect at all.

### The reading is capped at 10,000 µS/cm

With enough salt added, all four sensors reported between 10,001.9 and 10,002.9
µS/cm and stayed there for five minutes. The raw values behind those readings span
24 counts, a difference of 0.01 percent.

These are sensors that disagree with each other by 11 percent at every other
level. Agreement that close is a ceiling, not a measurement.

### In one stirred solution the four sensors disagreed by 11 percent

| Sensor | Conductivity in one solution |
|---|---|
| sw | 4,031 to 4,051 µS/cm |
| ne | 4,061 to 4,161 |
| se | 4,415 to 4,445 |
| nw | 4,485 to 4,515 |

**That is one solution at one moment, and it should not be generalised.** Taking
every three-minute window in which all four sensors reported, the apparent
disagreement ranges from under 1 percent to over 20, and the order changes
constantly. The exact tally depends on how the windows are aligned, which is why we
give none: one alignment gives fifteen orderings in twenty-four windows, another
twelve in twenty-three. What is robust is that no ordering persists.

Most of those windows are during salt addition, when the solution was not
necessarily uniform, so they are not clean measurements of anything. That is the
point. **The only window we can defend is the stirred one above**, and a single
window cannot tell you whether the difference is a fixed property of each unit.

An earlier version of this document said the rank order held all day. It does not,
and the claim is withdrawn.

### The measurement auto-ranges

The sensor reports which of several gain ranges its conductivity front end is
using. Raising conductivity from 5 µS/cm to the ceiling moved this indicator
through ten distinct values. vgabor99's units showed thirteen; see the
868 MHz section below.

The one frame that fails the CRC is excluded from this table; it decodes to range 2 at 10 µS/cm and 89 °C,
and is described in [data/](data/).

| Range indicator | Conductivity observed | Frames | Sensors submerged |
|---|---|---|---|
| 1 | 4.7 to 360 µS/cm | 451 | all four |
| 2 | 907 to 1,079 | 28 | all four |
| 3 | 1,331 to 2,028 | 44 | all four |
| 4 | 2,273 to 2,979 | 32 | all four |
| 5 | 3,101 to 3,576 | 33 | all four |
| 6 | 4,031 to 4,990 | 84 | all four |
| 7 | 4,700 to 5,357 | 54 | all four |
| 8 | 6,040 | 1 | one |
| 12 | 10,007 | 1 | one |
| 13 | 10,001 to 10,004 | 69 | all four |

Ranges 9 through 11 were not observed. Conductivity was raised in a single large
step through that region and we did not return to fill it. vgabor99's data fills
that gap.

Range 1 counts 451 transmissions, but 334 of those come from a capture program
that discarded frames where the indicator was not 1. See [data/](data/) for why
that portion of the record is not evidence of anything.

**The indicator moves with the reported conductivity, in all but one step.**
Taking the 798 distinct transmissions in order per sensor, the indicator changes
101 times, and in 100 of those it moves in the same direction as the reported
conductivity. The one exception is the ceiling frame described below.

That count excludes one frame, and the exclusion matters enough to state. The
series was logged with checksum validation only, and one frame in it decodes to
89.4 °C on the indoor spare probe with byte 11's low nibble at 0xc rather than the
0x6 it carries everywhere else, including in all 77 CRC-checked capture readings.
Keeping it gives 102 changes of 103, because it invents two transitions of its own.
`tools/verify_claims.py` recomputes both figures.

**The indicator continues to change after the conductivity reading has stopped.**
At the 10,000 µS/cm ceiling, where all four sensors report the same clamped value,
the indicator was observed at 13 for 69 frames and at 12 for one. What it is
counting therefore moves while the transmitted value does not.

Two cautions about that single frame. It is the **last** submerged frame, at
10:25:20, after every one of the 69 range-13 frames, so the indicator fell rather
than rose; an earlier version of this document said it rose. And it comes from the
logger that kept no payload, so its CRC cannot be checked. The conclusion that the
indicator is not a function of the transmitted value rests on one unverifiable
frame. Range 8 appears once in our record, at 6,040 µS/cm, which is below the
ceiling and not part of this.

The indicator does not rescale the conductivity value. The counts either side of a
transition are continuous with those within it: range four ends at 76,249 and range
five begins at 79,386, with no discontinuity. We cannot say more than that. Salt was
added in unmeasured steps, so there is no independent variable to plot against, and
we have frames inside only one transition.

Each sensor switches ranges at its own conductivity value, which follows from the
units disagreeing with each other by 11 percent.

The ranges overlap when expressed as reported conductivity. Range 6 was observed
as high as 4,990 µS/cm and range 7 as low as 4,700. This is discussed in
[interpretation.md](interpretation.md).

### Conductivity depresses the moisture reading, above a threshold

With sensors fully submerged, so that water content could not change, raising
conductivity lowered the reported moisture. Temperature and placement changed too:
the columns span 15.7 to 21.3 degrees, and the sensors were lifted out and
re-inserted between stages. This is not a controlled series and we cannot correct
for either.

For each sensor and each conductivity below, the frame taken is the submerged one whose conductivity is
nearest that value. The conductivity actually reached is given underneath, because the salt was added in
steps and none of these are exact.

| Sensor | Raw at ~280 µS/cm | at ~1,000 | at ~1,400 | at ~2,500 | Change |
|---|---|---|---|---|---|
| ne | 1689 | 1582 | 1492 | 1421 | −268 |
| se | 1673 | 1573 | 1473 | 1406 | −267 |
| sw | 1669 | 1574 | 1528 | 1442 | −227 |
| nw | 1595 | 1476 | 1475 | 1393 | −202 |

The conductivities those frames were actually at, in the same order: ne 299, 1007, 1443, 2524; se 279,
1017, 1402, 2534; sw 278, 997, 1402, 2494; nw 299, 998, 1361, 2574.

In our data, below about 300 µS/cm the effect could not be detected. One sensor, which was the
only one not saturated at the top of its scale in clean water, read 1609 at 4.8
µS/cm and 1623 at 309 µS/cm. That is a small movement in the opposite direction
and is within the noise of the measurement.

The soil in our sweep measured between 5 and 137 µS/cm, which places it entirely
within the region where we could not detect the effect. That was a lack of data
rather than a finding. vgabor99's 868 MHz series has many more readings at low
conductivity, and in water it does show the effect there; see below.

We would not extend these numbers to soil. The measurements were taken in water,
which is not the situation the claim would be about. This is discussed
in [interpretation.md](interpretation.md) and in [errata.md](errata.md).

## On a second band: vgabor99's measurements at 868 MHz

**Everything in this section was measured by vgabor99**, on five European 868 MHz
units on October 11, 2026. The files are in
[data/vgabor99-868-20261011/](data/vgabor99-868-20261011/), unchanged, with a
summary of the method; the method in their own words is in their comment linked
from there. The analysis below is ours, and `tools/verify_claims.py` recomputes
its figures from their files.

The five sensors sat together in a cardboard rig over a plastic container, 4 cm
apart, with the blades almost fully submerged once water was added. They were read dry,
then in distilled water, then through salt steps from about 5 µS/cm to the
ceiling, and finally each was held in open air, clear of everything. Three are
older units (`007713`, `007da9`, `00846a`) and two newer (`0077b2`, `0080d9`); in
vgabor99's words, the older three are most likely a single batch and the newer
two most likely a different one.

The files hold 1,394 payloads that pass both check bytes, which make 972 distinct
transmissions. Every one of those payloads decodes, under the byte map in
[decoder.md](decoder.md), to the same values the production decoder reported for
it. **The frame layout is the same on 868 MHz.**

Three cautions apply throughout. The blades were not fully submerged, so the water
readings do not compare with ours. Conductivity rose with time, so time and
conductivity are hard to separate. And the conductivity figures are the sensors'
own, as they are in our work.

### The range indicator takes at least thirteen values

| Range indicator | Conductivity observed | Units |
|---|---|---|
| 1 | 4.9 to 350.0 µS/cm | all five |
| 2 | 310.0 to 1,049.8 | all five |
| 3 | 1,090 to 1,799 | all five |
| 4 | 1,850 to 2,700 | all five |
| 5 | 2,670 to 3,546 | all five |
| 6 | 3,541 to 4,860 | all five |
| 7 | 4,310 to 5,355 | all five |
| 8 | 5,473 to 6,609 | all five |
| 9 | 6,522 to 7,969 | all five |
| 10 | 7,671 to 9,099 | all five |
| 11 | 8,760 to 10,010 | all five |
| 12 | 10,001 to 10,007 | four |
| 13 | 10,001 to 10,005 | the two newer units |

Ranges 9 to 11, which our own series skipped, appear on every unit, and every
unit passed through 1 to 11 in order; `007da9` later fell back once from 12 to 11.
That makes thirteen values seen in all, where we had seen ten.

The first change is where we could not place it. Three units read 309.9 µS/cm in
range 1 and 310.0 in range 2, the same point on all three. `0077b2` stayed in
range 1 up to 350.0 and then reported 340.0 in range 2, a lower reading after
switching up. `007da9` was still in range 1 at 350.0 when the low run ended and in
range 2 at 400.8 when the high run began, so its switch lies somewhere between.
On their units, then, the first threshold differs from unit to unit, at nearly
the same temperature. Three of our four units held range 1 up to about 360, which
fits that, though where our units switched we cannot tell, and our temperatures
varied; see [interpretation.md](interpretation.md).

Within the two runs the indicator changed 57 times and moved the same way as the
reported conductivity 53 times. Three of the four exceptions came at the ceiling,
where the indicator rose while the reading stayed pinned near 10,000, and the
fourth is `0077b2`'s 350.0 to 340.0. So the indicator also keeps moving after the
reading has clamped, as it did on ours. At the ceiling ours fell once; theirs
rose three times, in frames that pass both check bytes.

Both newer units reached 13, while the older three stopped at 11 or 12. Two units
cannot tell a batch difference from ordinary differences between units.

### Conductivity is reported in steps of about 10 µS/cm

In range 1 the reported values fall into 35 tight clusters, from the floor at
about 5 µS/cm up to 350.0, with none missing. Adjacent clusters are 9.75 to 10.45 µS/cm apart, an
evenly spaced grid fits them at 10.14 µS/cm, and within a cluster the reading
varies by less than 1 µS/cm. vgabor99 pointed this out in their postscript: the
low run covered nearly every value the range can report.

Our own data shows the same grid, which we had never noticed. Our range-1
readings fall on 25 of its steps, 9.90 to 10.45 µS/cm apart, and fit it at 10.12
µS/cm. So this is not an 868 MHz quirk. In ranges 2 to 10 of vgabor99's data the
smallest gaps between readings are also 8.9 to 10.1 µS/cm, so the step does not
grow with the range, at least up to range 10. Near the ceiling, in ranges 11 and
12, some readings are closer together.

### The newer units report moisture as the percentage, re-encoded

On `0077b2` and `0080d9`, every transmission satisfies

```
moisture_raw = 192 + round(14.52 × moisture_pct)
```

202 of 202 and 186 of 186. In air both read exactly 192, nowhere near the 564 to
597 our units read in air. **On these two units the raw field carries nothing
beyond the percentage.** The older three behave like ours: they send, on average, two
to four different raw values for each reported percentage, which is a real
measurement.

The newer units only ever reported 0 percent or 95 to 100 percent in this test,
so the formula is shown at those values only. Because their raw value follows the
percentage, they say nothing about the salt effect below: `0077b2`'s reading
actually rose as salt was added above about 260 µS/cm, from 95 percent to 100. Their bytes 14 and 21 also differ
from every other unit's; see [decoder.md](decoder.md).

### The older units match ours

Held in open air, the older units read 581, 605 to 611, and 586 to 587. Ours, never
wetted, read 564 to 597. Dry in the rig earlier the same day they read 581, 606,
and 585 to 586: the same within a count or two, apart from one 611 from `007da9`.
In two different arrangements hours apart, lying in the rig and held by hand,
their air reading held. Ours moved by up to 21 counts when the sensors were
carried to another room.

The same straight-line fit we used for our own units, applied to their frames,
gives each older unit's firmware line.

| Sensor | Points | Counts per 1 percent | Raw at 0 percent | Raw at 100 percent |
|---|---|---|---|---|
| `007713` | 46 | 9.41 | 617 | 1558 |
| `007da9` | 71 | 10.02 | 643 | 1645 |
| `00846a` | 82 | 10.01 | 623 | 1625 |

The frames are different, though. Ours were 2 to 70 percent below 300 µS/cm;
every one of theirs lies between 70 and 99 percent, in salt water that had pulled
the reading down. So these are not moisture levels. They show how the firmware
turns raw into percent, and the zero point is a long extrapolation. Two of the
three fall inside our range, 9.86 to 10.37 counts per percent, and `007713` has
the lowest slope of the seven units fitted, though from a different part of the
scale. `tools/wh52_868_analysis.py` fits the other way round, raw against percent
plus a half, and so prints slightly different values for the same conversion.

### In water, salt lowers the raw moisture reading from the first doses

The raw moisture reading first fell without any salt. In distilled water,
`00846a` fell from 1629 to 1590 over 17 minutes while its conductivity stayed at 5
to 6 µS/cm. We read that as the probe settling after it was wetted, which is an
inference. `007713` fell by a similar amount, from 1631 to 1594, but salt reached
it during that time (its reading rose from 5 to 16), so it is not a clean case.

After that, with conductivity between about 16 and 350 µS/cm, the raw reading fell
as salt was added.

| Sensor | 16 to 350 µS/cm | 400 to 3,000 µS/cm |
|---|---|---|
| `007713` | −0.183 counts per µS/cm | −0.075 |
| `007da9` | −0.180 | −0.090 |
| `00846a` | −0.159 | −0.083 |

The effect is about twice as steep at low conductivity as above 400. Divided by
each unit's counts per percent, it comes to 5 to 6 percentage points between 16
and 320 µS/cm, if all of it is the salt.

**We think it is mostly the salt, but cannot prove it.** Conductivity rose
steadily through the run, so time and conductivity are confounded, and some of the
settling may have continued. On `007713` the reading also drifted down while the
conductivity held within one step, so part of its fall may be time. On `00846a` it
did not, which makes that unit the cleanest case. This is also water, on partly submerged blades. It says nothing about the
direction in soil.

### At high conductivity the depression reverses

Median raw moisture of the older units, fully in the water, by conductivity:

| Sensor | 4,000 to 5,500 µS/cm | 5,500 to 7,000 | 7,000 to 9,990 | at the ceiling |
|---|---|---|---|---|
| `007713` | 1324 | 1357 | 1423 | 1481 |
| `007da9` | 1367 | 1392 | 1473 | 1537 |
| `00846a` | 1326 | 1357 | 1446 | 1498 |

The reading is lowest at 4,000 to 5,500 µS/cm and climbs steadily from there. The
climb begins well below the ceiling, so it is not produced by the conductivity
value clamping. Our own units read higher at the ceiling too; see
[interpretation.md](interpretation.md).

### Five units in one solution

Taking every moment in the low run when all five units had settled above 150
µS/cm, 36 in all, the highest reading exceeded the lowest by 11 to 21 percent,
with a median of 15.5. Our four units differed by 11 percent in our one stirred
solution, at the low end of their range. One caution: early in the run the cup was not
well mixed. The units first read 15 µS/cm or more at times from 11:45 to 11:57,
so some of the spread may be the solution rather than the sensors.

## Raw signal captures — verifying the conductivity arithmetic

A second session on the afternoon of September 9 recorded raw IQ captures at controlled
conductivities, specifically to test the parts of the conductivity decode that ordinary readings never
reach. Conductivity was raised from tap water with table salt in four stages while all four back lawn
sensors sat in the same cup, and a fifth condition was captured afterwards with the sensors rinsed and
dry. Seventy-four capture files were kept and all seventy-four contain at least one frame passing both
check bytes. They are in [data/captures/](data/captures/) with their decodes in `INVENTORY.csv`: 77
readings, 69 of them distinct payloads, 29 of them dry air.

The conductivity value is a 20-bit number assembled from three bytes, and the top four bits live in the
same byte as part of the moisture measurement. Those top bits are zero below 2,560 µS/cm, which is above
anything soil produces — so in normal use that part of the arithmetic is never exercised, and an error
there would be invisible.

| Range indicator | Carry bits | Frames | Conductivity |
|---|---|---|---|
| 1 | 0 | 52 | 5 µS/cm |
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
| `back_lawn_se` | 131,132 | 5,122.3 | 2 |

278 counts apart, taken seconds apart in one solution, **and the theoretical boundary falls between
them**. The disagreement between units, which is a nuisance everywhere else, is useful here.

### The range indicator and the carry are independent

Range 7 contains frames with carry bits of both 1 and 2. The range did not change when the count crossed
the 16-bit boundary.

These two mechanisms are easy to conflate, since both change as conductivity rises. They are not related:
the range indicator reflects a switch on the analogue side, and the carry is arithmetic in how the value
is packed.

### Carry bits of 4 cannot occur

A carry value of 4 would require a count of 262,144, which is 10,240 µS/cm. The sensor clamps at 10,000,
and the highest count we ever recorded is 256,198 — short by 5,946.

**So 3 is the maximum the hardware can produce**, and captures covering 0, 1, 2 and 3 cover every value
that exists rather than merely a good sample of them.

## Radio behavior

**Each reading is sent twice, about 43 milliseconds apart.** Of the 77 readings in the captures, 39 appear
twice within their own file and 38 once, the single ones mostly because 28 of the captures are only 65.5
milliseconds long. We cannot pin the last digit of the interval: rtl_433's decode timestamps give 43.2 to
43.4 milliseconds over 25 pairs, and independent burst detection gives 43.0 to 44.0 over 39 pairs with
about 0.3 milliseconds of its own jitter. Both are tight enough for a fixed firmware delay rather than
anything adaptive. Neither copy carries a flag distinguishing it from the other, so a receiver sees the
same reading arrive twice and should expect that.

The sensors transmit approximately every 70 seconds when readings are stable, and
approximately every 10 seconds while a reading is changing. The return to the
slower interval is a reliable indication that a sensor has settled, and we used it
as the stopping condition throughout the moisture sweep.
