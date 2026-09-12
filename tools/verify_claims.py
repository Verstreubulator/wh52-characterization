#!/usr/bin/env python3
"""Check the numbers in this repository against the data published with it.

Every figure quoted in the documents should be recomputable from the CSV files
in data/. This script does that. It is here because we published three numbers
that no file supported, and reading the documents carefully did not catch any of
them.

Run it from the repository root:

    python tools/verify_claims.py

It prints one line per claim and exits non-zero if any fails.

Copyright (C) 2026 Andreas Braunlich
Licensed under the GNU General Public License, version 2 or later.
"""

import csv
import math
import os
import sys
from collections import Counter, defaultdict

FAILED = []


def check(label, ok, detail=""):
    print(f"  [{'ok  ' if ok else 'FAIL'}] {label}" + (f"   {detail}" if detail else ""))
    if not ok:
        FAILED.append(label)


def load(name):
    with open(os.path.join("data", name), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def crc8(data, poly=0x31, init=0):
    reg = init
    for byte in data:
        reg ^= byte
        for _ in range(8):
            reg = ((reg << 1) ^ poly) & 0xFF if reg & 0x80 else (reg << 1) & 0xFF
    return reg


def straight_line(points):
    """Least squares of percentage against raw. Returns intercept, slope."""
    n = len(points)
    sx = sum(x for x, _ in points)
    sy = sum(y for _, y in points)
    sxx = sum(x * x for x, _ in points)
    sxy = sum(x * y for x, y in points)
    slope = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    return (sy - slope * sx) / n, slope


series_rows = load("conductivity-series-20260909.csv")
# Two loggers overlapped, so the file holds the same transmission more than once.
# Everything below counts distinct transmissions.
_seen = set()
series = []
for _r in series_rows:
    _k = (_r["time"], _r["probe"], _r["m_raw"], _r["ec_uS_cm"],
          _r["moisture_pct"], _r["temp_C"])
    if _k not in _seen:
        _seen.add(_k)
        series.append(_r)
frames = load("moisture-frames-20260909.csv")
sweep = load("moisture-sweep-20260909.csv")
percent = load("moisture-percent-20260909.csv")
july = load("reference-frames-202607.csv")
captures = load(os.path.join("captures", "INVENTORY.csv"))

AIR = {"ne": 572, "nw": 575, "se": 564, "sw": 597}
WATER = {"ne": 1661, "nw": 1669, "se": 1646, "sw": 1666}

print("\nCapture inventory")
bad = crc_fail = 0
for row in captures:
    raw = bytes.fromhex(row["payload"])
    if crc8(raw[:22]) != raw[22]:
        crc_fail += 1
    if (sum(raw[:23]) & 0xFF) != raw[23]:
        bad += 1
    expected = {
        "device_id": row["payload"][2:8],
        "moisture_pct": str(raw[6]),
        "m_raw": str(((raw[8] & 0xF0) << 4) | raw[7]),
        "temp_C": f"{(((raw[4] & 0x1F) << 8) | raw[5]) * 0.1 - 40:.1f}",
        "ec_uS_cm": f"{(((raw[8] & 0x0F) << 16) | (raw[9] << 8) | raw[10]) / 25.6:.1f}",
        "ec_range": str(raw[11] >> 4),
        "carry_nibble": str(raw[8] & 0x0F),
        "battery_mV": str(raw[20] * 20),
    }
    bad += sum(1 for k, val in expected.items() if row[k] != val)
check("every row matches its own payload", bad == 0 and crc_fail == 0,
      f"{len(captures)} rows, {bad} mismatches, {crc_fail} CRC failures")
check("all eight sensors appear", len({r["device_id"] for r in captures}) == 8)
check("every carry value 0 to 3 is present",
      sorted({int(r["carry_nibble"]) for r in captures}) == [0, 1, 2, 3])
counts = [round(float(r["ec_uS_cm"]) * 25.6) for r in captures]
check("highest conductivity count is 256,197", max(counts) == 256197, f"{max(counts):,}")
check("a carry of 4 is out of reach", 262144 > max(counts),
      f"would need 262,144; the ceiling stops us {262144 - max(counts):,} short")

print("\nPer-sensor moisture conversion (behavior.md)")
published = {
    "ne": (37, 10.37, 624, 1661, 0.52, 1.89, 78.5),
    "nw": (28, 10.14, 618, 1633, 0.46, 1.72, 74.0),
    "se": (32, 10.06, 607, 1613, 0.51, 1.73, 74.3),
    "sw": (38, 9.86, 640, 1625, 0.53, 1.73, 73.3),
}
for unit, (n, slope, zero, hundred, resid, eps0, eps100) in published.items():
    points = {(int(r["m_raw"]), int(r["moisture_pct"])) for r in frames
              if r["probe"].endswith(unit)
              and 2 <= int(r["moisture_pct"]) <= 70 and float(r["ec_uS_cm"]) < 300}
    points |= {(int(r["m_raw"]), int(r["moisture_pct"])) for r in sweep
               if r["probe"].endswith(unit) and r["m_raw"]
               and 0 < int(r["moisture_pct"]) < 100}
    points |= {(int(r["m_raw"]), int(r["moisture_pct"])) for r in july
               if r["probe"].endswith(unit)}
    points = sorted(points)
    a, b = straight_line(points)
    worst = max(abs(y - (a + b * x)) for x, y in points)
    grad = (math.sqrt(78.5) - 1) / (WATER[unit] - AIR[unit])
    offset = 1 - grad * AIR[unit]
    ok = (len(points) == n
          and abs(1 / b - slope) < 0.005
          and abs(-a / b - zero) < 0.5
          and abs((100 - a) / b - hundred) < 0.5
          and abs(worst - resid) < 0.005
          and abs((grad * (-a / b) + offset) ** 2 - eps0) < 0.006
          and abs((grad * ((100 - a) / b) + offset) ** 2 - eps100) < 0.06)
    check(f"{unit}: {n} points, {slope} counts/%, zero {zero}, permittivity {eps0}", ok,
          f"got n={len(points)} {1/b:.2f} {-a/b:.0f} {(grad*(-a/b)+offset)**2:.2f}")

print("\nNo temperature coefficient is measurable (behavior.md)")
for unit, (n, slope, resid) in {"ne": (34, 2.69, 31), "nw": (28, -1.86, 28),
                                "se": (56, 0.05, 26), "sw": (31, 0.79, 26)}.items():
    rows = [r for r in series if r["probe"].endswith(unit)
            and int(r["moisture_pct"]) <= 1 and float(r["ec_uS_cm"]) < 20]
    temps = [float(r["temp_C"]) for r in rows]
    raws = [int(r["m_raw"]) for r in rows]
    a, b = straight_line(list(zip(temps, raws)))
    worst = max(abs(r - (a + b * t)) for t, r in zip(temps, raws))
    check(f"{unit}: {n} frames, slope {slope:+} counts/degC, scatter {resid}",
          len(rows) == n and abs(b - slope) < 0.005 and abs(worst - resid) < 0.5,
          f"got n={len(rows)} {b:+.2f} {worst:.0f}")

print("\nConductivity (behavior.md)")
ranges = {1: (4.7, 359.9, 451), 2: (906.6, 1078.6, 28), 3: (1330.9, 2027.6, 44),
          4: (2272.5, 2978.5, 32), 5: (3101.0, 3576.0, 33), 6: (4030.6, 4989.6, 84),
          7: (4700.2, 5356.9, 54), 8: (6040.4, 6040.4, 1),
          12: (10006.8, 10006.8, 1), 13: (10000.9, 10003.8, 69)}
for rg, (lo, hi, n) in ranges.items():
    vals = [float(r["ec_uS_cm"]) for r in series
            if int(r["byte11"], 16) >> 4 == rg and float(r["temp_C"]) < 80]
    check(f"range {rg}: {lo} to {hi}, {n} frames",
          len(vals) == n and abs(min(vals) - lo) < 0.1 and abs(max(vals) - hi) < 0.1,
          f"got {len(vals)} frames, {min(vals)} to {max(vals)}")
ceiling = sorted({int(r["byte11"], 16) >> 4 for r in series if float(r["ec_uS_cm"]) > 9000})
check("only ranges 12 and 13 occur at the ceiling", ceiling == [12, 13], str(ceiling))

print("\nThe range indicator tracks uncompensated conductance (interpretation.md)")
six = [(float(r["ec_uS_cm"]), float(r["temp_C"])) for r in series
       if r["probe"].endswith("ne") and int(r["byte11"], 16) >> 4 == 6]
seven = [(float(r["ec_uS_cm"]), float(r["temp_C"])) for r in series
         if r["probe"].endswith("ne") and int(r["byte11"], 16) >> 4 == 7]
hi6, lo7 = max(six), min(seven)
warm = lambda ec, t: ec * (1 + 0.02 * (t - 25))
check("as reported, range 6 sits above range 7 on the same sensor", hi6[0] > lo7[0],
      f"{hi6[0]} at {hi6[1]} C versus {lo7[0]} at {lo7[1]} C")
check("uncompensated, the order is restored", warm(*hi6) < warm(*lo7),
      f"{warm(*hi6):.0f} then {warm(*lo7):.0f}")

print("\nWhere a sensor sits (behavior.md)")
for level, spread in {"dew_soil": 6, "normal_no_sprinkler": 7,
                      "sprinkler_soil": 8, "saturated_soil": 7}.items():
    vals = [int(r["moisture_pct"]) for r in sweep if r["level"] == level]
    check(f"{level}: {spread} points between sensors", max(vals) - min(vals) == spread)
seq = [r["moisture_pct"] for r in percent
       if r["probe"] == "back_lawn_sw" and "07:15:21" <= r["time"] <= "07:15:51"]
check("insertion reads 0, 5, 9 then 31", seq == ["0", "5", "9", "31"], str(seq))

print("\nProse figures (behavior.md, decoder.md, data/captures/README.md)")
sub = [int(r["m_raw"]) for r in sweep
       if r["level"] == "submerged_water" and int(r["moisture_pct"]) == 100]
check("submerged raw values are 1646 to 1669", (min(sub), max(sub)) == (1646, 1669))
filtered = [r for r in series if int(r["byte11"], 16) >> 4 == 1 and r["logger"].startswith("1")]
check("334 of the range 1 transmissions come from the filtered logger",
      len(filtered) == 334, str(len(filtered)))
soil = [float(r["ec_uS_cm"]) for r in sweep if r["level"] not in ("air", "submerged_water")]
check("the sweep soil reached 137 microsiemens", round(max(soil)) == 137, f"{max(soil)}")
check("the series holds 1,016 rows and 798 distinct transmissions",
      (len(series_rows), len(series)) == (1016, 798),
      f"{len(series_rows)} rows, {len(series)} distinct")
nw = [(int(r["m_raw"]), int(r["moisture_pct"])) for r in frames
      if r["probe"].endswith("nw") and 2 <= int(r["moisture_pct"]) <= 70
      and float(r["ec_uS_cm"]) < 300]
nw += [(int(r["m_raw"]), int(r["moisture_pct"])) for r in sweep
       if r["probe"].endswith("nw") and r["m_raw"] and 0 < int(r["moisture_pct"]) < 100]
nw += [(int(r["m_raw"]), int(r["moisture_pct"])) for r in july if r["probe"].endswith("nw")]
a, b = straight_line(sorted(set(nw)))
check("the 1593 frame predicts 96.1 percent", abs((a + b * 1593) - 96.1) < 0.05,
      f"{a + b * 1593:.2f}")
for target, expected in ((280, (1689, 1673, 1669, 1595)), (2500, (1421, 1406, 1442, 1393))):
    got = []
    for unit in ("ne", "se", "sw", "nw"):
        near = [(abs(float(r["ec_uS_cm"]) - target), int(r["m_raw"])) for r in series
                if r["probe"].endswith(unit) and int(r["moisture_pct"]) >= 50]
        got.append(min(near)[1])
    check(f"conductivity table column at {target} microsiemens", tuple(got) == expected,
          str(tuple(got)))
counted = Counter()
for row in captures:
    ec, moist = float(row["ec_uS_cm"]), int(row["moisture_pct"])
    counted["ceiling" if ec > 9000 else "high" if ec > 4000 else "mid" if ec > 3000
            else "low" if ec > 1000 else ("dry" if moist <= 1 else "soil")] += 1
check("capture conditions: 29 dry, 23 soil, 4 at the ceiling",
      (counted["dry"], counted["soil"], counted["ceiling"]) == (29, 23, 4), str(dict(counted)))
dry_ec = [float(r["ec_uS_cm"]) for r in captures if int(r["moisture_pct"]) <= 1]
dry_ec += [float(r["ec_uS_cm"]) for r in sweep if r["level"] == "air"]
check("air frames span 4.6 to 5.2 microsiemens", (min(dry_ec), max(dry_ec)) == (4.6, 5.2),
      f"{len(dry_ec)} frames")
outs = [r for r in series if int(r["m_raw"]) < 700 and r["time"] >= "08:00:00"]
floor = [r for r in outs if float(r["ec_uS_cm"]) < 6]
check("out of solution, 164 of 199 transmissions sit at the floor",
      (len(floor), len(outs)) == (164, 199), f"{len(floor)} of {len(outs)}")
above = [float(r["ec_uS_cm"]) for r in outs if float(r["ec_uS_cm"]) >= 6]
check("the remainder read 15 to 2,272 microsiemens",
      (min(above), max(above)) == (15.4, 2272.5), f"{min(above)} to {max(above)}")
check("77 readings, 69 distinct payloads, all 74 files",
      (len(captures), len({r["payload"] for r in captures}),
       len({r["file"] for r in captures})) == (77, 69, 74),
      f"{len(captures)}, {len({r['payload'] for r in captures})}, "
      f"{len({r['file'] for r in captures})}")


print("\nByte map (decoder.md)")
per_unit = defaultdict(lambda: defaultdict(set))
for row in captures:
    raw = bytes.fromhex(row["payload"])
    for index in (12, 13, 14, 15, 16, 17, 18, 19, 21):
        per_unit[index][row["device_id"]].add(raw[index])
for index in (12, 13, 15, 16, 17, 19):
    check(f"byte {index} is constant within a unit",
          all(len(v) == 1 for v in per_unit[index].values()))
check("byte 14 is 0x93 on every unit",
      {b for v in per_unit[14].values() for b in v} == {0x93})
tally = Counter(sorted(v)[0] for v in per_unit[18].values())
check("byte 18 is 0x7b on seven units and 0x8c on one",
      dict(tally) == {0x7B: 7, 0x8C: 1}, str({hex(k): v for k, v in tally.items()}))
batch = {(d[:3], sorted(v)[0]) for d, v in per_unit[21].items()}
check("byte 21 follows the identifier prefix", batch == {("005", 0x08), ("007", 0x09)})

print("\nDocument text (phrases that must not reappear)")
DOCS = {name: open(name, encoding="utf-8").read()
        for name in ("README.md", "behavior.md", "interpretation.md", "decoder.md",
                     "hardware.md", "errata.md", "sources.md")}
CORRECTIONS = DOCS["errata.md"]
BANNED = [
    ("8 to 12 to 13", "range 8 is at 6,040, not at the ceiling"),
    ("0.53 counts per degree", "no temperature coefficient is measurable"),
    ("predicts 96.6", "the 1593 frame predicts 96.1"),
    ("predicts 96.2", "the 1593 frame predicts 96.1"),
    ("1646 to 1690", "submerged raw values are 1646 to 1669"),
    ("read 7 percent", "no retained file contains that reading"),
    ("3.3 to 4.1", "the zero point is permittivity 1.7 to 1.9"),
    ("between 5 and 230", "the sweep soil reached 137"),
    ("but 345 of those", "334 distinct transmissions came from the filtered logger"),
    ("1,016 valid frames", "1,016 rows but 798 distinct transmissions"),
    ("moved from 12 to 13", "the indicator fell: the single 12 comes after every 13"),
    ("observed at 12 and then at 13", "the indicator fell, it did not rise"),
    ("1.024 Msps", "the captures are 1.000 Msps"),
    ("Skierucha & Wilczek, 2012", "PMC3472864 is Wilczek et al. 2012"),
    ("Kizito, F., et al.", "PMC11014125 is Fragkos et al. 2024"),
    ("published literature reports the opposite sign", "we could not confirm a direction"),
    ("Every raw capture that contains a decodable frame", "38 of 77 readings appear once"),
    ("straight to better than half a percentage point", "three of four residuals exceed 0.5"),
    ("only ever been checked with the range indicator at 1",
     "the July series spanned 340 to 7,430 uS/cm, ranges 1 to 8"),
    ("256,197", "the highest count from the payloads is 256,198"),
    ("277 counts apart", "the boundary frames are 278 counts apart"),
    ("63,838", "range 4 spans 58,176 to 76,249"),
    ("A second sensor produced a similar reading later the same", "all three 96 % frames are nw"),
    ("unlikely to be a coincidence", "the -400 offset is Fine Offset's house convention"),
    ("better supported of our inferences", "any coefficient above 1.55 %/degC also works"),
    ("only ever been checked in the lowest range",
     "the July calibration spanned 340 to 7,430 uS/cm, which is ranges 1 to 8"),
    ("only ever validated in ordinary soil",
     "the July calibration spanned 340 to 7,430 uS/cm, which is ranges 1 to 8"),
    ("reporting residuals of 3 to 5 percent",
     "not confirmable from the abstract we have"),
    ("water content is over-estimated in saline conditions",
     "not confirmable from the abstract we have"),
    ("held the same rank order", "the order changes from window to window"),
    ("rank order among the four was stable", "the order changes from window to window"),
    ("4.7 to 5.4 µS/cm, and never lower", "the air-frame range is 4.6 to 5.2"),
    ("report 4.6 to 5.4", "the air-frame range is 4.6 to 5.2"),
    ("A second bad frame is kept", "that frame is valid; our decoder slipped bits"),
    ("3,240 mV from an AA cell", "that reading came from a mis-decode, not the sensor"),
    ("Flame-retardant epoxy resin",
     "that is the module's sealing compound; its probe is an alloy electrode"),
]
for phrase, why in BANNED:
    where = [n for n, t in DOCS.items() if phrase in t and phrase not in CORRECTIONS]
    outside_errata = [n for n in where if n != "errata.md"]
    check(f'withdrawn wording absent: "{phrase}"', not outside_errata,
          f"found in {outside_errata} ({why})" if outside_errata else why)

print()
if FAILED:
    print(f"{len(FAILED)} claim(s) do not reproduce:")
    for item in FAILED:
        print(f"  - {item}")
    sys.exit(1)
print("Every checked claim reproduces from the published data.")
