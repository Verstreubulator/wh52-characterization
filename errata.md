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

The published literature reports the opposite for capacitance sensors in soil:
water content is over-estimated in saline conditions, sometimes substantially,
because ionic conduction adds to the apparent permittivity (Skierucha & Wilczek,
2012).

Our measurements were taken with sensors submerged in water, which is not the
same situation. A submerged sensor is already at the top of its permittivity
range, and added conductivity damps the measurement instead of adding to it.

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
