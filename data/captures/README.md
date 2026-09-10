# Raw Signal Captures

Forty-two raw IQ captures of WH52 transmissions, recorded on September 9, 2026 at
915 MHz. Forty-one of them contain a decodable frame; `INVENTORY.csv` lists those
with their decoded fields and the full payload in hexadecimal.

These exist for one reason. The conductivity value is a 20-bit number assembled
from three bytes, and its top four bits are zero below 2,560 µS/cm. Ordinary soil
never comes close, so that part of the arithmetic is never exercised in normal use
and an error in it would be invisible. The same is true of the higher gain ranges.
These captures reach conditions the sensors will not otherwise see.

## Format

Unsigned 8-bit complex baseband, 1.024 Msps, centered on 915 MHz. This is the
format rtl_433 writes with `-S all` and reads with `-r`.

```
rtl_433 -c 0 -r g55271_915M_1000k.cu8 \
        -X 'n=wh52raw,m=FSK_PCM,s=58,l=58,r=5000,preamble=aa2dd4'
```

The `-c 0` matters if you have a configuration file that publishes to MQTT.
Replaying captures without it will republish stale readings to a live broker.

## What is covered

| Condition | Files |
|---|---|
| Dry air, after rinsing | 8 |
| Tap water with salt, 2,191 to 2,333 µS/cm | 7 |
| 3,405 to 3,739 µS/cm | 4 |
| 4,940 to 5,132 µS/cm | 10 |
| At the 10,000 µS/cm ceiling | 4 |
| Soil, from sensors in service | 8 |

Across the set the moisture reading spans 0 to 98 percent, the raw moisture
measurement 586 to 1,603, temperature 19.7 to 37.5 °C, and conductivity 4.7 to
10,008 µS/cm. Eight distinct sensors appear.

**Every carry value the hardware can produce is present.** The four high bits of
the conductivity count take the values 0, 1, 2 and 3 here. A value of 4 would need
a count of 262,144, which is 10,240 µS/cm, and the sensor clamps at 10,000. The
highest count in this set is 256,197. There is no fifth case to capture.

## The file that is not in the inventory

`g57185_915M_1000k.cu8` contains a WH52 transmission that fails both check bytes,
so it has no inventory row. It is kept on purpose.

```
a20070f4028a0048200080166948937e7cccf7e6a213561e
```

The flex decoder recovers 194 bits rather than 192, and most of the frame looks
perfectly ordinary: 0 percent moisture, raw 584, 25.0 °C, 5.0 µS/cm, range
indicator 1. Every one of those is a plausible reading for the sensor it came
from. The corruption is only visible in the tail, where byte 20 gives a battery
voltage of 3,240 mV from a single AA cell.

Neither check byte passes. The CRC is `0x56` against a computed `0xb9`, and the
checksum `0x1e` against `0x82`. This is what a bad frame looks like when nothing
about the numbers warns you, and it is the argument for verifying both.

## Columns in INVENTORY.csv

| Column | Meaning |
|---|---|
| file | The capture |
| probe, device_id | Which sensor, and its 24-bit identifier |
| moisture_pct, m_raw | As reported, and the 12-bit raw measurement |
| temp_C, ec_uS_cm | As reported |
| ec_range | The conductivity range indicator, `b[11] >> 4` |
| carry_nibble | The top four bits of the conductivity count, `b[8] & 0x0F` |
| payload | All 24 bytes, hexadecimal |

## Conditions and their limits

Conductivity was set with ordinary table salt in tap water and was not
independently measured; the values in the inventory are the sensors' own readings.
The dry-air frames were taken from sensors that had been rinsed and towel dried
shortly before, and they read about 20 to 50 counts higher than the same sensors
did in air the night before. They should be treated as recently-wet rather than as
a clean dry reference. Both points are discussed in
[../../behavior.md](../../behavior.md).

The sensors here were out of the ground during construction work, which is why
four of them could be moved through these conditions at all.
