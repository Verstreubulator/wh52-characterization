# vgabor99's 868 MHz measurements, October 11, 2026

**Every measurement in this folder was made by vgabor99, not by us.** They ran
the test, wrote the method and recorded the files, and gave permission for them to
be included here ([merbanan/rtl_433_tests#519, comment of October 17,
2026](https://github.com/merbanan/rtl_433_tests/pull/519#issuecomment-6237666358)). If you use any of it,
please credit vgabor99. The analysis built on it in this repository is ours, and
so are any mistakes in that analysis.

The original post, with the method in vgabor99's own words, is their comment on
[merbanan/rtl_433_tests#519](https://github.com/merbanan/rtl_433_tests/pull/519#issuecomment-6112095570)
of October 11, 2026, with a postscript
[nine minutes later](https://github.com/merbanan/rtl_433_tests/pull/519#issuecomment-6112181254).

## The files

The three files are exactly as attached to that comment. `SHA256SUMS` lets you
confirm that, and `tools/verify_claims.py` checks it on every run.

| File | What it covers |
|---|---|
| `wh52_in_air_no51.json` | Each sensor held in open air, away from any object, for about three minutes |
| `wh52_low_range_no51.json` | Dry in the rig, then distilled water, then small salt steps about every four minutes |
| `wh52_high_range_no51.json` | Larger salt steps about every three minutes, up to the conductivity ceiling |

They are `rtl_433 -F json` output. Each transmission appears as a line from the
production `Fineoffset-WH52` decoder and, alongside it, a `wh52raw` line from the
flex decoder in [../../decoder.md](../../decoder.md) carrying the whole payload.
Times are UTC, as vgabor99's receiver recorded them. The recording command, from
their comment:

```
rtl_433 -f 868.35M -g auto -Y autolevel -s 1024k -X 'n=wh52raw,m=FSK_PCM,s=58,l=58,r=5000,preamble=aa2dd4' -M time:iso:tz -M level -M protocol -C si -F json
```

## The method, in summary

Our summary of the comment; the comment itself is the authority.

Five European 868 MHz WH52 units sat together in a cardboard rig over a plastic
container, 4 cm apart, with the blades, in vgabor99's words, "almost fully
submerged" once the water was in. Three are older units (`007713`, `007da9`,
`00846a`), "most likely a single batch", and two are newer (`0077b2`, `0080d9`),
"most likely a different batch"; both descriptions are vgabor99's.

The sensors were washed and dried first. The sequence was dry in the rig from
11:31, distilled water at 11:37, salt dialled in from 11:42, then a step about
every four minutes from 11:48. The high range began at 14:22 with larger and less
even steps every three minutes until the conductivity reading stopped rising.
Afterwards each unit was held in open air, clear of everything including the
person holding it, for about three minutes. vgabor99 removed other sensors and
noise from the files.

There was no reference conductivity meter, so, as in our own work, the
conductivity values are the sensors' own readings.

## What to watch for

- **Count transmissions, not lines.** Every transmission appears at least twice,
  once per decoder, and some bursts are reported more than once. Validate the
  `wh52raw` payload on both check bytes and deduplicate on device, time and
  payload: 1,394 valid payloads, 972 distinct transmissions.
- **The blades were not fully submerged**, so the water readings are not
  comparable with ours, which were taken fully submerged.
- **The two newer units report a re-encoded moisture value.** See
  [../../behavior.md](../../behavior.md).
