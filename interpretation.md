# What Our Data Suggests

This section is our own reasoning about the measurements in
[behavior.md](behavior.md). Each claim is given with the evidence that supports it
and with the reason it might be wrong. None of it has been confirmed against a
reference instrument or against the manufacturer.

## The raw moisture value appears to track refractive index

The sensor uses frequency domain reflectometry, which measures how the surrounding
material affects an electrical signal. The physical quantity being sensed is the
dielectric permittivity of the soil, usually written as epsilon. Air has a
permittivity of 1, dry mineral soil between 2.5 and 4, and water about 78.5 at
room temperature.

Both air and water readings are available for all four of our sensors, which gives
two anchor points of known permittivity per unit. Fitting a straight line between
them and then asking where the sensor's own zero percent point falls produces the
following.

| Sensor | Permittivity at reported 0 percent | at reported 100 percent |
|---|---|---|
| ne | 1.89 | 78.5 |
| nw | 1.72 | 74.0 |
| se | 1.73 | 74.3 |
| sw | 1.73 | 73.3 |

The 100 percent point lands near the permittivity of water, not of saturated soil.
Saturated soil is generally between 30 and 40, and none of these are close to it.

The zero point lands just above air. Dry mineral soil is 2.5 to 4, and all four
sensors put their reported zero below that. Expressed on each sensor's own scale,
air falls at −5.0, −4.2, −4.3 and −4.4 percent, which is then clamped to zero. The
four agree to better than a point, which is more consistent than most things we
have measured.

**So the reported percentage is a linear scale from a little above air to water.**
Neither end is a soil condition. One hundred percent is not field capacity and not
saturation. Zero percent is not dry soil either; dry soil reads a few percent, and
our own dew-damp soil read 8 to 14.

An earlier version of this document put the zero point at a permittivity of 3.3 to
4.1 and called that dry mineral soil, treating the coincidence as the strongest
evidence for the model below. That was arithmetic error rather than interpretation,
and it is described in [errata.md](errata.md).

### The relationship is with the square root of permittivity, not permittivity

Our first attempt assumed the raw value was proportional to permittivity directly.
Converting our soil measurements on that basis and applying Topp's equation, which
is the standard conversion from permittivity to volumetric water content (Topp et
al., 1980), gave 20 percent water content for soil that had been dust the previous
day and had only taken dew. Saturated soil came out at 57 percent. Neither is
credible.

Reflectometry instruments measure propagation velocity or frequency shift, and both
vary with the square root of permittivity rather than with permittivity itself.
Repeating the calculation on that basis gives the following.

| Level | Permittivity | Topp water content | Sensor's own reading |
|---|---|---|---|
| Dew-damp soil | 3.8 to 5.4 | 5.0 to 9.0 percent | 8 to 14 percent |
| Ordinary soil | 8.8 to 10.6 | 16.5 to 20.0 | 22 to 26 |
| Sprinkler-watered soil | 10.6 to 13.8 | 20.0 to 25.6 | 26 to 34 |
| Saturated soil | 24.7 to 38.1 | 39.7 to 49.9 | 56 to 63 |

Dry mineral soil is generally 2 to 8 percent water content by volume, field
capacity 25 to 35 percent, and saturation 40 to 50 percent. Every level falls
where soil physics says it should, using two anchors that were never fitted to
soil.

**We take this as evidence that the raw value is linear in the square root of
permittivity.** The reasoning is circumstantial: it rests on the resulting numbers
being physically sensible rather than on any direct measurement of permittivity.
It is also weaker than it was, because the zero-point coincidence we used to cite
alongside it turned out to be an arithmetic mistake. What survives is the soil
column above, and the fact that the linear-permittivity alternative fails badly on
the same data.

The dew-damp result is still perhaps one to three points higher than the soil
warranted, and Topp's equation is fitted for mineral soils and is known to read
high in organic ones. Our top two inches are compost and manure.

### What this would mean in practice

If the relationship holds, a sensor can be placed on an absolute scale using two
measurements anyone can make: its raw reading in air, and its raw reading
submerged in water. Both are physical constants rather than fitted values, which
would make readings from different units comparable without individually
calibrating each one.

We have not verified this against a gravimetric soil sample, which is the
measurement that would settle it.

There is a serious practical difficulty with the air anchor, and it is worse than
the one we first described.

The air reading is not reproducible. Carrying the same sensors from one room to
another, with nothing else changed, moved two of them by 19 and 21 counts, which is
about two percentage points. Within a single session the same sensors repeat to
within one count, so the instrument is fine; what changes is what is near it. In
air, the sensing volume contains whatever the sensor is resting on and whatever is
beside it.

Two percentage points is the same order as the spread between units that this
scheme exists to remove. **Unless the air reading is taken in a fixed arrangement,
clear of surfaces and of other sensors, and returned to that arrangement every
time, the anchor is not accurate enough to be worth having.**

The water anchor is probably safer, since a submerged sensor is surrounded by water
rather than by its surroundings, but we have not tested that either.

We also cannot say how long a wetted sensor reads high, or by how much. Our sessions
differed in placement as well as in elapsed time, so the two cannot be separated
from the data we have. See [errata.md](errata.md).

## The range indicator appears to switch on uncompensated conductance

The range indicator described in [behavior.md](behavior.md) does not divide
cleanly by reported conductivity. Ranges overlap, and in one case a single sensor
reported range 6 at 4,870 µS/cm and range 7 at the lower value of 4,761.

The two readings were taken at different temperatures, 21.3 °C and 23.5 °C.

Conductivity measurements are conventionally corrected to a reference temperature
of 25 °C. If the range indicator switches on the uncorrected measurement while the
transmitted value is corrected, then the same underlying measurement will be
reported as a higher conductivity when the soil is colder. The apparent switching
point would move with temperature even though the real one had not.

Converting both readings back to uncorrected conductance using a coefficient of 2
percent per degree gives 4,509 and 4,618, which are in the correct order. A second
sensor behaves the same way.

The published register map for the commodity module discussed in
[hardware.md](hardware.md) documents a conductivity temperature coefficient with a
default of exactly 2 percent per degree Celsius (Seeed Technology, 2020). We
arrived at that figure independently before finding the documentation.

**An inversion disappearing under a model is stronger evidence than a curve
fitting**, and we regard this as the better supported of our inferences. It rests
on two sensors and four readings, which is not many.

We were not able to determine the rule governing where the thresholds fall. They
are uneven when expressed as reported conductivity, and we do not have enough
readings either side of each boundary to say whether they are regular once
temperature is accounted for.

## The range indicator is not derived from the reported conductivity

At the 10,000 µS/cm ceiling all four sensors report the same clamped value, to
within 0.01 percent. The range indicator nonetheless moved from 8 to 12 to 13
while that value stayed fixed.

**This means the indicator cannot be computed from the conductivity the sensor
transmits.** It must reflect an internal measurement that continues to rise after
the transmitted figure has been capped.

Taken with the temperature result above, the picture is of a raw internal
conductance measurement that drives the range switching, and a separately
processed output that is temperature-corrected and then limited to the product's
specified range. The two diverge at both ends: at low temperature, where the
correction inflates the reported value, and at the ceiling, where the reported
value stops.

## The conductivity ceiling is a product limit

All four sensors stop at 10,000 µS/cm, while the data field carries values up to
roughly 41,000. The commodity module's published specification is 0 to 10,000
µS/cm.

**This suggests the limit is set by the sensing element or the firmware rather
than by the transmission format**, and that the unused headroom in the field is
not an oversight.

## Differences between units are probably physical

Each sensor has its own moisture conversion and its own conductivity calibration,
and the rank order among the four was stable all day.

If the underlying measurement is a physical property of the surrounding material,
as the permittivity result suggests, then differences between units are most
likely differences in electrode geometry and cell constant rather than in
firmware. Small variations in blade spacing or plating would produce exactly this
pattern.

**We think this is why the differences are stable and reproducible** rather than
drifting, but we have not measured any physical dimension to check it.

## A conductivity correction for moisture is not warranted in our soil

Our measurements found no detectable effect below about 300 µS/cm, and our soil
reads between 5 and 230.

We would not go further than that. The measurements were made in water, and the
published literature reports the effect running the other way in soil, with
capacitance sensors reading high rather than low in saline conditions (Skierucha
& Wilczek, 2012). Water and soil are not equivalent here: a submerged sensor is
already at the top of its permittivity range, whereas in partly wet soil the same
ions add to apparent permittivity. **We do not know which direction applies in our
beds**, and we withdrew an earlier claim that we did. See [errata.md](errata.md).

What survives is the magnitude. Whatever the sign, we could not measure it where
our soil operates, and it is smaller than the error introduced by how firmly the
sensor is pushed into the ground.

If a correction is ever wanted, the published approach uses the measured
conductivity as an indicator of dielectric loss and corrects the water content
from both together, reporting residuals of 3 to 5 percent. It should be fitted in
soil rather than in water.

## An observation we cannot explain

At the conductivity ceiling, reported moisture rose again. Sensors reading 74 to
81 percent at 5,300 µS/cm read 92 to 98 percent at 10,002 µS/cm, all still fully
submerged.

The relationship between conductivity and reported moisture therefore appears to
be non-monotonic. We do not know whether this is a real effect or a consequence of
the conductivity measurement being clamped, and we have not investigated further.
