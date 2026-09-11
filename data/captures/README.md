# Raw Signal Captures

Seventy-four raw IQ captures of WH52 transmissions, recorded on September 9 and 10,
2026 at 915 MHz. Seventy-two contain at least one frame that passes both check
bytes; `INVENTORY.csv` lists every such frame with its decoded fields and the full
payload in hexadecimal.

These exist for two reasons. The conductivity value is a 20-bit number assembled
from three bytes, and its top four bits are zero below 2,560 µS/cm. Ordinary soil
never comes close, so that part of the arithmetic is never exercised in normal use
and an error in it would be invisible. Beyond that, a raw capture is the only form
of evidence that lets someone check a decode without owning the hardware.

## Format

Unsigned 8-bit complex baseband, 1.024 Msps, centered on 915 MHz. This is the
format rtl_433 writes with `-S all` and reads with `-r`.

```
rtl_433 -c 0 -r g55271_915M_1000k.cu8 \
        -X 'n=wh52raw,m=FSK_PCM,s=58,l=58,r=5000,preamble=aa2dd4'
```

The `-c 0` matters if you have a configuration file that publishes to MQTT.
Replaying captures without it will republish stale readings to a live broker.

## Every capture holds the same frame twice

A WH52 sends each reading twice, 43 milliseconds apart, and a capture that catches
one copy almost always catches both. Decoding a file therefore yields two identical
payloads, and `INVENTORY.csv` lists such a pair once. Where a file yields two
*different* payloads it gets two rows; one capture caught two different sensors
transmitting inside the same window.

This is worth knowing before counting anything. These files produce 160 valid
frames but only 74 distinct readings, and 67 distinct payloads, since a sensor
reporting an unchanged value twice in a row transmits the identical 24 bytes.

## What is covered

| Condition | Readings |
|---|---|
| Dry air | 27 |
| Soil, from sensors in service | 22 |
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
highest count in this set is 256,197. There is no fifth case to capture.

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

## The two files with no valid frame

`g57185_915M_1000k.cu8` and `g122181_915M_1000k.cu8` contain WH52 transmissions
that fail both check bytes. They have no inventory rows and are kept on purpose.

The instructive one is `g57185`:

```
a20070f4028a0048200080166948937e7cccf7e6a213561e
```

Most of it looks perfectly ordinary: 0 percent moisture, raw 584, 25.0 °C, 5.0
µS/cm, range indicator 1. Every one of those is a plausible reading for the sensor
it came from. The corruption shows only in the tail, where byte 20 gives a battery
voltage of 3,240 mV from a single AA cell.

Neither check byte passes. The CRC is `0x56` against a computed `0xb9`, and the
checksum `0x1e` against `0x82`. This is what a bad frame looks like when nothing
about the numbers warns you, and it is the argument for verifying both.

Two further frames elsewhere in the set pass the checksum but fail the CRC. Their
files are listed, because each also contains a good frame; only the bad copies are
absent from the inventory.

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
