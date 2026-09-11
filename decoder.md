# Reading the Raw Fields

Every number in this document comes from fields that no released software
reports. The production decoder in rtl_433 emits moisture, temperature,
conductivity and battery voltage, which is what most people want, but it does not
emit the raw moisture measurement or the conductivity range indicator. This
section explains how to read them.

## Attribution

The frame layout was worked out in July 2026 and contributed to rtl_433 as pull
request 3602, with sample captures as rtl_433_tests pull request 508.

The battery decode is not ours. Our original submission placed battery voltage at
byte 15, which was wrong; the correlation held only because all four of our
sensors happened to be at nearly the same voltage. It was corrected by vgabor99,
who located it at byte 20 and also renamed the conductivity field, in pull request
3668. That work stands on its own and should be credited separately from ours.

The analysis and measurements in this repository were carried out with Claude
(Anthropic), which did the capture scripting, the curve fitting, and much of the
reasoning in [interpretation.md](interpretation.md). Several of the errors listed
in [errata.md](errata.md) are its as well, and it caught and corrected most of
them.

## The frame

Transmission is FSK with pulse-coded modulation, 58 microsecond bit width, with
the preamble `aa aa aa 2d d4`. The payload is 24 bytes. This is the same
modulation and preamble as the WH51, but the family byte differs, so the WH51
decoder correctly ignores these frames.

| Byte | Contents | Status |
|---|---|---|
| 0 | Family identifier, always `0xA2` | Known |
| 1 to 3 | Device identifier, 24 bits | Known |
| 4 | Bits 7 to 5: transmission boost counter. Bits 4 to 0: temperature, high bits | Known |
| 5 | Temperature, low byte | Known |
| 6 | Moisture percentage, 0 to 100 | Known |
| 7 | Raw moisture measurement, low byte | Known |
| 8 | High nibble: raw moisture, high bits. Low nibble: conductivity, bits 16 to 19 | Known |
| 9 | Conductivity, bits 15 to 8 | Known |
| 10 | Conductivity, bits 7 to 0 | Known |
| 11 | High nibble: conductivity range indicator. Low nibble: always 6 | Behavior known, rule not |
| 12, 13 | Constant per unit, differs between units | **Unknown** |
| 14 | `0x93` on all eight of our units | **Unknown**, but not per-unit |
| 15 to 17 | Constant per unit, differs between units | **Unknown** |
| 18 | `0x7b` on seven units, `0x8c` on one | **Unknown**, appears per-unit |
| 19 | Constant per unit, differs between units | **Unknown** |
| 20 | Battery voltage | Known (vgabor99) |
| 21 | `0x08` on units with identifiers beginning `0x005`, `0x09` on those beginning `0x007` | Probably a batch or revision marker |
| 22 | CRC-8, polynomial `0x31`, initial value `0x00`, over bytes 0 to 21 | Known |
| 23 | Sum of bytes 0 to 22, modulo 256 | Known |

Roughly a third of the frame remains undecoded. Bytes 12 through 19 are constant
for a given sensor and differ between sensors, which suggests factory calibration
data or a serial number, but we have not been able to demonstrate what they mean.
They are listed here in the hope that someone else can.

## Conversions

```
temperature_C  = (((b4 & 0x1F) << 8) | b5) * 0.1 - 40.0
moisture_pct   = b6
moisture_raw   = ((b8 & 0xF0) << 4) | b7                     12 bits
ec_raw         = ((b8 & 0x0F) << 16) | (b9 << 8) | b10       20 bits
conductivity   = ec_raw / 25.6                               microsiemens per cm
battery_mV     = b20 * 20
ec_range       = b11 >> 4
```

The 25.6 divisor was fitted empirically in July against readings from the
manufacturer's gateway. Note that every reading used to establish it was taken in
ordinary soil, which means it has only ever been checked with the range indicator
at 1. Ranges 2 through 13 use the same divisor with nothing verifying it.

Byte 8 carries two unrelated fields at once. Its high nibble belongs to the raw
moisture value and its low nibble to the conductivity value. This looks like an
error when read cold, and it is not.

## Checking a frame

Both check bytes should be verified. We recorded one frame in 671 that passed the
sum check while decoding to a temperature of 89 °C and a range indicator that
could not be valid. The CRC would have rejected it.

A second bad frame is kept in [data/captures/](data/captures/) as a worked
example. It fails both check bytes, and unlike the first one, nothing in its
moisture, temperature or conductivity values looks wrong. Only the battery voltage
gives it away, at 3,240 mV from an AA cell.

**Do not use byte 11 as a validity check.** It was constant across every frame we
had at the time, and using it as a filter seemed harmless. It is not: the moment
the sensor changed range, that filter discarded exactly the frames that
demonstrated the behavior. This cost us about twenty minutes of confusion and is
described in [errata.md](errata.md).

## Capturing frames yourself

No patched binary or forked decoder is needed. A flex decoder specification
recovers the whole payload from a stock rtl_433:

```
rtl_433 -f 915M -X 'n=wh52raw,m=FSK_PCM,s=58,l=58,r=5000,preamble=aa2dd4'
```

This runs alongside the normal decoders and does not interfere with them. It
matches WH51 frames as well, which are shorter and can be ignored.

The parser in [tools/wh52_parse.py](tools/wh52_parse.py) turns the resulting hex
payload into the fields above. It reads from standard input or from an MQTT topic.

If you would rather check the decode than reproduce the conditions, the raw radio
recordings in [data/captures/](data/captures/) can be replayed straight into
rtl_433 with `-r`, and every one of them is listed with its expected decode.

If you are running rtl_433 as a Home Assistant add-on, the same specification can
be added to `rtl_433.conf.template` as a `decoder` line. It is additive and does
not affect existing decoding.

## Reproducing the conductivity conditions

For anyone wanting to exercise the parts of the decode that soil never reaches, ordinary table salt in
tap water is sufficient. No reference meter is needed, because the sensor's own reading is what you are
testing against.

Rough dosing, measured on about 350 ml: a shaker tap adds around **245 µS/cm**, and an eighth of a
teaspoon around **3,300 µS/cm**. Conductivity stops being proportional to concentration above roughly
10 g/l, so the higher steps overshoot those figures.

Useful targets:

| To reach | Aim for | Why |
|---|---|---|
| carry bits 1 | 2,600 – 5,100 µS/cm | first time the top bits are non-zero |
| carry bits 2 | 5,150 – 7,600 | second carry |
| carry bits 3, and the clamp | add a rounded quarter teaspoon | the ceiling, and the highest carry possible |

Allow three minutes after stirring — for the salt to dissolve and for the temperature to settle, since
dissolving shifts it. The sensor transmits every ten seconds while a reading is changing and every
seventy once it has settled, so the return to the slow interval is a reliable stopping signal.

Two practical warnings. **Rinse and dry the blades thoroughly afterwards**; a rinsed but still-damp
sensor read 46–76 µS/cm as the film concentrated. And if you are pulling raw captures from a rolling
buffer, **identify and fetch in one operation** — see [errata.md](errata.md).

## The proper fix

This is a workaround. The correct solution is for the raw moisture value and the
range indicator to be emitted by the production decoder, so that nobody needs a
flex decoder to read them. That change belongs in `fineoffset_wh52.c` upstream and
is the next thing we intend to do. Once it lands, this section becomes historical.
