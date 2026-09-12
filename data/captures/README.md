# Raw Signal Captures

Seventy-four raw IQ captures of WH52 transmissions, recorded on September 9 and 10,
2026 at 915 MHz. **All seventy-four** contain at least one frame that passes both
check bytes. `INVENTORY.csv` lists 77 readings, 69 of them distinct payloads, with
the decoded fields and the full payload in hexadecimal.

## How the inventory was built, and why it is built that way

Every row was found by a demodulator and then **validated by arithmetic that does
not depend on the demodulator**. A WH52 frame carries a CRC-8 and an eight-bit
checksum, sixteen bits of redundancy, so a wrong payload satisfying both by chance
is about one in 65,536.

Candidates were pooled from two independent demodulators: rtl_433's flex decoder,
and a separate implementation written for the purpose. Every candidate either tool
produced was then checked against both bytes. The point of the pooling is that a
fault in either tool can only cause a **miss**, never a false entry.

That is not a theoretical concern. An earlier inventory was built from rtl_433
alone, and it was missing three real frames that the second demodulator found;
rtl_433 slips bits in the tail of a weak burst. The second tool found nothing the
first did not, on 74 of the 77 readings, and the three it added are marked in the
errata. Completeness is the thing neither tool can guarantee: both detect bursts by
a signal-strength threshold, so a transmission close to the noise floor is invisible
to both.

These exist for two reasons. The conductivity value is a 20-bit number assembled
from three bytes, and its top four bits are zero below 2,560 µS/cm. Ordinary soil
never comes close, so that part of the arithmetic is never exercised in normal use
and an error in it would be invisible. Beyond that, a raw capture is the only form
of evidence that lets someone check a decode without owning the hardware.

## Format

Unsigned 8-bit complex baseband, 1.000 Msps, centered on 915 MHz. This is what
rtl_433 writes with `-S all` and reads back with `-r`; the rate is in the filename,
which is where `-r` takes it from. An earlier version of this file said 1.024 Msps,
which is wrong: at that rate the bit period would not come out at the WH52's 58
microseconds.

```
rtl_433 -c 0 -r g55271_915M_1000k.cu8 \
        -X 'n=wh52raw,m=FSK_PCM,s=58,l=58,r=5000,preamble=aa2dd4'
```

The `-c 0` matters if you have a configuration file that publishes to MQTT.
Replaying captures without it will republish stale readings to a live broker.

## A WH52 sends each reading twice

Of the 77 readings, **39 appear twice within their own capture and 38 appear once**.
The single ones are mostly explained by file length: 28 of the 74 captures are
131,072 bytes, which is 65.5 milliseconds, and two copies about 43 milliseconds
apart do not reliably both fit.

`INVENTORY.csv` lists a repeated pair once. Where a file yields two *different*
payloads it gets two rows; three captures caught two sensors transmitting inside the
same window.

**The interval is about 43 milliseconds, and we cannot pin the last digit.** Two
measurements disagree slightly: rtl_433's decode timestamps give 43.2 to 43.4
milliseconds over 25 pairs, and independent burst detection gives 43.0 to 44.0 over
39 pairs with about 0.3 milliseconds of its own jitter. Both agree it is a fixed
firmware delay rather than anything adaptive. Neither copy carries a flag
distinguishing it from the other, so a receiver sees the same reading arrive twice
and should expect that.

Count carefully: 77 readings, 69 distinct payloads, because a sensor reporting an
unchanged value twice in a row transmits the identical 24 bytes.

## What is covered

| Condition | Readings |
|---|---|
| Dry air | 29 |
| Soil, from sensors in service | 23 |
| Tap water with salt, 2,191 to 2,333 µS/cm | 7 |
| 3,405 to 3,739 µS/cm | 4 |
| 4,940 to 5,132 µS/cm | 10 |
| At the 10,000 µS/cm ceiling | 4 |

Across the set the moisture reading spans 0 to 98 percent, the raw moisture
measurement 565 to 1,603, temperature 19.3 to 37.5 °C, and conductivity 4.6 to
10,008 µS/cm. All eight of our sensors appear.

**Every carry value the hardware can produce is present.** The four high bits of
the conductivity count take the values 0, 1, 2 and 3 here. A value of 4 would need
a count of 262,144, which is 10,240 µS/cm, and the sensor clamps at 10,000. The
highest count in this set is 256,198. There is no fifth case to capture.

## Reading the dry-air captures

There are three groups and they are not equivalent. Eight were taken a few hours
after the sensors were rinsed. Twelve were taken a day later, indoors. The rest
were taken fifteen minutes after that, once the sensors had been carried somewhere
else.

The last two groups differ by up to 21 counts on the same sensor with nothing
changed but location. **Do not treat any of these as a clean dry-air reference.**
The `desk_spare` frames come from a sensor that has never been wetted or placed in
soil, which is the closest thing here to a control, and even it moved 5 counts
between groups. This is discussed in [../../behavior.md](../../behavior.md).

## The frame we published as corrupt was not

An earlier version of this file presented `g57185_915M_1000k.cu8` as a worked
example of a corrupt transmission, given away by a battery voltage of 3,240 mV from
an AA cell. That was our decoder, not the sensor. The second demodulator recovers

```
a20070f4028a0048200080166948937e7cce7bf35109ab0f
```

which passes both check bytes and gives 1,620 mV. The two decodes agree byte for
byte until the tail. The frame is now in the inventory, along with two others found
the same way.

The lesson we drew from it was right and the example was wrong. Verify both check
bytes: our own mis-decode produced a payload whose moisture, temperature and
conductivity all read plausibly, and only the battery byte looked absurd.

## Columns in INVENTORY.csv

| Column | Meaning |
|---|---|
| file | The capture the frame came from |
| probe, device_id | Which sensor, and its 24-bit identifier |
| moisture_pct, m_raw | As reported, and the 12-bit raw measurement |
| temp_C, ec_uS_cm | As reported |
| ec_range | The conductivity range indicator, `b[11] >> 4` |
| carry_nibble | The top four bits of the conductivity count, `b[8] & 0x0F` |
| battery_mV | `b[20] * 20`, the decode contributed by vgabor99 |
| payload | All 24 bytes, hexadecimal |

Every row was regenerated from the capture files themselves and rechecked against
the payload: CRC, checksum and all derived fields.

## Conditions and their limits

Conductivity was set with ordinary table salt in tap water and was not
independently measured; the values in the inventory are the sensors' own readings.

The sensors here were out of the ground during construction work, which is why four
of them could be moved through these conditions at all.
