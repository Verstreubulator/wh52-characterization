# Conclusions We Withdrew

This section records claims we made during the work and later had to take back.
They are here because the corrections are useful in themselves, and because
anyone repeating this work is likely to reach the same wrong conclusions in the
same order.

## The battery byte was in the wrong place

Our original decoder placed battery voltage at byte 15. All four sensors we had
were nearly new and sat between 1.56 and 1.62 volts, so byte 15 appeared to track
voltage across the four units. It was a coincidence produced by a small sample
with almost no variation in the quantity being measured.

vgabor99 found the real location at byte 20 by looking at a wider range of
voltages. We later confirmed it on our own hardware by comparing the same units
six weeks apart: byte 15 had not moved on any unit, while byte 20 had fallen on
every one.

The lesson is that a correlation across four samples of nearly identical value is
not evidence. We should have looked for variation within a single unit over time
before claiming anything.

## Byte 11 was reported as constant when it is not

We recorded byte 11 as fixed at `0x16` across a conductivity range of 5 to 340
µS/cm, which covered everything we had ever measured, and wrote it up as evidence
against the original guess that it was a range indicator.

Every one of those readings was below the first switching threshold. The
conclusion was drawn from a sample that could not have contained a
counter-example.

The original guess was correct.

## A validity filter hid the behavior it was supposed to protect

Having decided byte 11 was constant, we used it as a cheap check on frame
validity: any frame where it was not `0x16` was assumed corrupt and discarded.

When conductivity was raised past the first threshold and byte 11 changed, that
filter silently discarded every affected frame. The capture log went quiet on two
sensors while the production decoder continued reporting them correctly. It was
the owner who noticed that something had interfered with the decoding, not the
analysis.

A byte that is constant across your sample is a hypothesis, not an invariant.
Filtering on it guarantees you cannot observe its falsification. Frames should be
validated on the CRC and the checksum, which exist for that purpose.

## The moisture conversion was called exact when it was not

An early pass over 13 frames from six sensors, all between 12 and 27 percent
moisture, found that the formula `(raw − 610) × 3 / 32` reproduced every reported
percentage. It was written up as the firmware's conversion.

Adding our own upstream test captures, which reach 44 percent, broke it. Two
sensors sat 1.4 and 2.2 percentage points above that line. The apparent exactness
was an artifact of a narrow measurement band, and the truth is that each sensor
has its own conversion.

## The direction of the salinity effect was stated with unwarranted confidence

We measured reported moisture falling as conductivity rose and stated that saline
soil would therefore read drier than it is, pushing an irrigation controller
toward over-watering.

The measurement did not support it. It was taken with the sensors submerged in
water, which is not the situation the claim was about. A submerged sensor is
already at the top of its permittivity range, so added conductivity damps the
reading; in partly wet soil the same ions would add to apparent permittivity
instead, which is the opposite sign. We had measured one case and made a
statement about the other.

A later version of this entry said the published literature reports the opposite
direction in soil, citing Skierucha and Wilczek. We have only read that paper's
abstract and could not confirm it, so that attribution has been removed too. The
withdrawal stands on its own: we measured in water and spoke about soil.

We do not know which direction applies in soil, and should not have said we did.
What survives is that the effect was too small to measure anywhere near the
conductivity our own soil reaches.

## A threshold pattern was proposed and then abandoned

Early conductivity data appeared to show the range thresholds doubling, at roughly
625, 1,250 and 2,500 µS/cm. It fit the first four ranges.

It failed on the fifth. Range 4 spans raw counts 63,838 to 76,249, which straddles
65,536 without changing, ruling out any scheme based on powers of two. Linear
spacing does not fit either: the constraints from the two most tightly bracketed
boundaries are incompatible with range 1 still holding at 339 µS/cm.

Some of that irregularity is probably temperature, which was drifting through the
measurements while we were treating the thresholds as fixed. We have not
established a rule and the document says so rather than offering one.

## The raw value was assumed linear in permittivity

Converting raw values to permittivity on the assumption of a direct linear
relationship gave 20 percent water content for soil that had been dust the
previous day, and 57 percent for saturated soil.

Reflectometry instruments respond to the square root of permittivity, not to
permittivity. On that basis the same measurements give 5 percent and 40 to 50
percent, which are both reasonable. The error was ours, and the physically correct
form was available in any textbook.

## A dry-air reading was called an anchor before it was one

Having captured four sensors reading 0 to 1 percent in air, we described the set
as anchoring the bottom of the moisture scale. It does not.

The sensors had been rinsed under hot water a few hours earlier. Compared against
the same three units measured in air the previous night, before any of them had
been wetted, they read 20 to 50 counts high once temperature was accounted for.
That is up to five percentage points, on a measurement whose whole purpose was to
be a fixed point.

The mistake was treating a number that looked right, 0 percent in air, as
evidence that the measurement was clean. The percentage clamps at zero, so it
would have looked right across the entire range of the error.

Reading the same units again a day later separated what was happening. Most of the
offset was water and it evaporated. Roughly one percentage point did not, and
appears to be a deposit left by the tap water and the salt. The owner suggested
that before the data showed it.

What survives is a rule rather than an anchor: a sensor that has been wet is not a
dry-air reference for at least a day, and may hold about a point after that.

## The zero point was said to land on dry soil, and the arithmetic did not say that

Converting each sensor's fitted zero point to a permittivity, using air and water
as the two anchors, we reported values of 3.3 to 4.1 and observed that this is the
textbook range for dry mineral soil. Because the anchors were never fitted to soil,
we treated the coincidence as the strongest single piece of evidence that the raw
value tracks the square root of permittivity.

Recomputing it from the published data gives 1.7 to 1.9. The correct figure sits
just above air and well below dry soil, and the conclusion drawn from it does not
follow.

The error is not in the method or in the anchors. Applying the same calculation to
the soil levels reproduces the published table to within a few tenths, so the
machinery was right. The zero-point column corresponds to raw values around 690 to
715, which is 70 to 100 counts above the fitted zero point, or roughly 7 to 10
percent up the scale. We cannot reconstruct where those numbers came from.

What makes this worth recording is that the claim was checkable against data in
this repository the whole time, and nobody checked it, including us, until an audit
of the whole repository went looking. A number that agrees with a textbook is the
one most worth recomputing, not the least.

## A residue was inferred from a difference that placement can produce

Having withdrawn the dry-air anchor above, we replaced it with a second claim: that
most of the offset was water which evaporated in a day, and that a residual 8 to 13
counts, about one percentage point, was a deposit left by the tap water and salt.
The owner had suggested a deposit, the number was stable across three sensors, and
a never-wetted control appeared not to move at all.

Reading the same sensors again fifteen minutes later, after they had been carried
to a different place, moved two of them by 19 and 21 counts. Both then read below
their never-wetted baselines rather than above. The control moved 5 counts without
being touched.

The residual was the same size as the measurement's dependence on where the sensor
is sitting. We had three sessions and treated the difference between them as
time, when placement differed too.

This is the same error as the battery byte and the moisture formula, in a third
costume: a difference that could have had more than one cause was assigned to the
cause we were interested in. The control was supposed to guard against exactly
that, and it did not, because it was in a different place from the sensors it was
controlling for.

## Three numbers were published that no retained file supports

An audit of every quantitative claim in this repository against the data
published alongside it found three that a reader could not have checked, because
the measurements behind them were never kept.

**A temperature coefficient of 0.53 counts per degree**, from three sensors left in
air overnight. The warmer half of those readings is in no file we have. Fitting
every dry-air frame we did keep gives slopes of +2.47, −2.14, +0.71 and +0.94
counts per degree on the four units, with about thirty counts of scatter. The
figure was withdrawn rather than corrected, because the data does not support any
figure.

**A sensor reading 7 percent and then 14 percent** in the same soil before and
after being pressed in firmly. This was the headline example for contact being the
dominant error. No retained file contains it. The claim it was making is well
supported by four sensors in the same material differing by 6 to 8 points, which is
what the document says now.

**Readings in distilled water.** Cited as evidence that the conductivity floor is a
floor rather than a measurement. We have no record of taking them. The conclusion
stands on the dry-air readings alone and the distilled-water sentence is gone.

Separately, the range indicator was said to have been seen at 8, 12 and 13 while
conductivity was clamped at its ceiling. Range 8 occurs once in our record, at
6,040 µS/cm, which is not at the ceiling. The point being made survives on 12 and
13.

The common thread is that none of this was caught by writing carefully. It was
caught by running every number in the document against the files shipped with it,
which is a thing worth doing before publishing rather than after.

## Capture files were lost between listing them and fetching them

The radio node writes one raw capture per detected signal and keeps only about a hundred, so the pool
turns over in well under an hour when the band is busy.

Working through it in two steps — list the files containing the frames we wanted, then download those
files — lost three of them. They had rotated out in the seconds between the two commands.

Identifying and fetching has to be a single operation. Nothing important was lost, because the missing
files duplicated conditions already held, but it could as easily have been the only capture of a
condition that took an hour to set up.
