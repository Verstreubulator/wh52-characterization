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
import hashlib
import json
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
counts = [((bytes.fromhex(r["payload"])[8] & 0x0F) << 16)
          | (bytes.fromhex(r["payload"])[9] << 8)
          | bytes.fromhex(r["payload"])[10] for r in captures]
check("highest conductivity count is 256,198", max(counts) == 256198, f"{max(counts):,}")
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
check("byte 14 is 0x93 on every one of our units",
      {b for v in per_unit[14].values() for b in v} == {0x93})
tally = Counter(sorted(v)[0] for v in per_unit[18].values())
check("byte 18 is 0x7b on seven units and 0x8c on one",
      dict(tally) == {0x7B: 7, 0x8C: 1}, str({hex(k): v for k, v in tally.items()}))
batch = {(d[:3], sorted(v)[0]) for d, v in per_unit[21].items()}
check("in our sample, byte 21 happens to follow the identifier prefix",
      batch == {("005", 0x08), ("007", 0x09)}, "vgabor99's 0x0077b2 breaks it; see below")

print("\nRange-indicator transitions, and what the counts depend on")
# The patch comment quotes "100 of the 101 range changes". That figure excludes one
# frame, and the exclusion has to be stated or the number cannot be reproduced.
def transitions(frames):
    by_probe = defaultdict(list)
    for r in frames:
        by_probe[r["probe"]].append(r)
    total = same = 0
    exceptions = []
    for fs in by_probe.values():
        fs.sort(key=lambda r: r["time"])
        for a, b in zip(fs, fs[1:]):
            ra, rb = int(a["byte11"], 16) >> 4, int(b["byte11"], 16) >> 4
            if ra == rb:
                continue
            total += 1
            if (rb - ra) * (float(b["ec_uS_cm"]) - float(a["ec_uS_cm"])) > 0:
                same += 1
            else:
                exceptions.append((a["probe"], a["time"], ra, b["time"], rb))
    return total, same, exceptions


odd = [r for r in series if int(r["byte11"], 16) & 0x0F != 6]
check("exactly one series frame fails the byte 11 low-nibble sanity check", len(odd) == 1,
      f"{odd[0]['probe']} {odd[0]['time']}, byte11 {odd[0]['byte11']}, {odd[0]['temp_C']} C"
      if len(odd) == 1 else f"{len(odd)} frames")
check("and it is not a physical reading", len(odd) == 1 and float(odd[0]["temp_C"]) > 80,
      f"{odd[0]['temp_C']} C on an indoor probe" if len(odd) == 1 else "")

clean = [r for r in series if int(r["byte11"], 16) & 0x0F == 6]
tot_c, same_c, exc_c = transitions(clean)
check("excluding it: 100 of 101 transitions move with the reported value",
      (same_c, tot_c) == (100, 101), f"{same_c} of {tot_c}")
tot_a, same_a, _ = transitions(series)
check("including it: 102 of 103, which is why the exclusion must be stated",
      (same_a, tot_a) == (102, 103), f"{same_a} of {tot_a}")
check("the single exception is the fall from 13 to 12 at the ceiling",
      len(exc_c) == 1 and (exc_c[0][2], exc_c[0][4]) == (13, 12),
      f"{exc_c[0]}" if len(exc_c) == 1 else f"{len(exc_c)} exceptions")
check("byte 11 low nibble is 0x6 in every CRC-checked capture",
      all(bytes.fromhex(r["payload"])[11] & 0x0F == 6 for r in captures),
      f"{len(captures)} readings")

print("\nThe moisture frames are part of the conductivity series, not an addition to it")
mois_rows = load("moisture-frames-20260909.csv")
mois_distinct = {(r["time"], r["probe"], r["m_raw"], r["ec_uS_cm"]) for r in mois_rows}
check("moisture-frames holds 338 rows but 327 distinct transmissions",
      (len(mois_rows), len(mois_distinct)) == (338, 327),
      f"{len(mois_rows)} rows, {len(mois_distinct)} distinct")
check("every one of them also appears in the conductivity series",
      mois_distinct <= {(r["time"], r["probe"], r["m_raw"], r["ec_uS_cm"]) for r in series_rows},
      "so the two counts must never be added together")

print("\nThe conductivity ceiling is approximate")
top = sorted({float(r["ec_uS_cm"]) for r in series if float(r["ec_uS_cm"]) >= 10000})
check("readings at the ceiling sit above 10,000 rather than exactly on it",
      bool(top) and 10000 < top[0] and top[-1] < 10010, f"{top[0]} to {top[-1]} uS/cm")

print("\nvgabor99's 868 MHz measurements (behavior.md, decoder.md)")
# All of this data is vgabor99's, kept unchanged in data/vgabor99-868-20261011/.
V_DIR = os.path.join("data", "vgabor99-868-20261011")
V_FILES = ["wh52_in_air_no51.json", "wh52_low_range_no51.json", "wh52_high_range_no51.json"]
V_OLD, V_NEW = ("007713", "007da9", "00846a"), ("0077b2", "0080d9")
sums = dict(line.split()[::-1] for line in open(os.path.join(V_DIR, "SHA256SUMS"), encoding="utf-8")
            if line.strip())
check("the three files are unchanged from vgabor99's post",
      all(hashlib.sha256(open(os.path.join(V_DIR, f), "rb").read()).hexdigest() == sums[f]
          for f in V_FILES))
v_rows, v_native = [], 0
for name in V_FILES:
    for line in open(os.path.join(V_DIR, name), encoding="utf-8"):
        if not line.strip():
            continue
        j = json.loads(line)
        if j.get("model") == "Fineoffset-WH52":
            v_native += 1
        if j.get("model") != "wh52raw":
            continue
        hexed = j["rows"][0]["data"]
        raw = bytes.fromhex(hexed[:48]) if len(hexed) >= 48 else b""  # short bursts fail below
        if not (len(raw) == 24 and raw[0] == 0xA2 and crc8(raw[:22]) == raw[22]
                and sum(raw[:23]) & 0xFF == raw[23]):
            continue
        v_rows.append({
            "file": name, "time": j["time"], "id": raw[1:4].hex(), "payload": raw.hex(),
            "pct": raw[6], "m_raw": ((raw[8] & 0xF0) << 4) | raw[7],
            "ec": (((raw[8] & 0x0F) << 16) | (raw[9] << 8) | raw[10]) / 25.6,
            "range": raw[11] >> 4, "low": raw[11] & 0x0F, "raw": raw})
v_seen, vg = set(), []
for r in v_rows:
    if (r["id"], r["time"], r["payload"]) not in v_seen:
        v_seen.add((r["id"], r["time"], r["payload"]))
        vg.append(r)
check("1,394 valid payloads, one per native decode, 972 distinct transmissions",
      (len(v_rows), v_native, len(vg)) == (1394, 1394, 972),
      f"{len(v_rows)} valid, {v_native} native, {len(vg)} distinct")
check("byte 11 low nibble is 6 on every one of them", all(r["low"] == 6 for r in vg))
units = sorted({r["id"] for r in vg})
check("ranges 1 to 11 occur on all five units, 12 on four and 13 on two",
      all(len({r["id"] for r in vg if r["range"] == g}) == 5 for g in range(1, 12))
      and len({r["id"] for r in vg if r["range"] == 12}) == 4
      and {r["id"] for r in vg if r["range"] == 13} == set(V_NEW)
      and sorted({r["range"] for r in vg}) == list(range(1, 14)))
top1 = {u: max(r["ec"] for r in vg if r["id"] == u and r["range"] == 1) for u in units}
low2 = {u: min(r["ec"] for r in vg if r["id"] == u and r["range"] == 2) for u in units}
check("three units leave range 1 at 309.9 and enter range 2 at 310.0",
      all(round(top1[u], 1) == 309.9 and round(low2[u], 1) == 310.0
          for u in ("007713", "0080d9", "00846a")))
check("0077b2 reads 350.0 in range 1 and then 340.0 in range 2",
      (round(top1["0077b2"], 1), round(low2["0077b2"], 1)) == (350.0, 340.0))
check("007da9 is last seen in range 1 at 350.0 and first in range 2 at 400.8",
      (round(top1["007da9"], 1), round(low2["007da9"], 1)) == (350.0, 400.8))
v_total = v_same = 0
for name in V_FILES[1:]:
    for u in units:
        fs = sorted((r for r in vg if r["id"] == u and r["file"] == name), key=lambda r: r["time"])
        for a, b in zip(fs, fs[1:]):
            if a["range"] != b["range"]:
                v_total += 1
                v_same += (b["range"] - a["range"]) * (b["ec"] - a["ec"]) > 0
check("the range moves with the reported value in 53 of 57 changes",
      (v_same, v_total) == (53, 57), f"{v_same} of {v_total}")


def lattice(values):
    """Step of the best evenly spaced grid through the values, and the clusters on it."""
    values = sorted(values)
    clusters = [[values[0]]]
    for x in values[1:]:
        (clusters[-1].append(x) if x - clusters[-1][-1] <= 3 else clusters.append([x]))
    centres = [sum(c) / len(c) for c in clusters]
    gaps = [b - a for a, b in zip(centres, centres[1:]) if b - a < 15]
    n = [round((x - 5.3) / 10.13) for x in values]
    _, step = straight_line(list(zip(n, values)))
    return step, len(clusters), min(gaps), max(gaps), max(max(c) - min(c) for c in clusters)


step, n_cl, g_lo, g_hi, wide = lattice({r["ec"] for r in vg if r["range"] == 1})
check("868: range 1 holds 35 steps of 10.14 uS/cm, none missing, 9.75 to 10.45 apart",
      n_cl == 35 and abs(step - 10.14) < 0.005 and wide < 1
      and (round(g_lo, 2), round(g_hi, 2)) == (9.75, 10.45),
      f"{n_cl} steps of {step:.3f}, adjacent gaps {g_lo:.2f} to {g_hi:.2f}")
step, n_cl, g_lo, g_hi, wide = lattice({float(r["ec_uS_cm"]) for r in series
                                        if int(r["byte11"], 16) >> 4 == 1
                                        and float(r["temp_C"]) < 80})
check("915: our range 1 sits on the same grid, 10.12 uS/cm, 25 steps 9.90 to 10.45 apart",
      n_cl == 25 and abs(step - 10.12) < 0.005
      and (round(g_lo, 2), round(g_hi, 2)) == (9.90, 10.45),
      f"{n_cl} steps of {step:.3f}, adjacent gaps {g_lo:.2f} to {g_hi:.2f}")
consts = {u: {r["raw"][12:20].hex() + r["raw"][21:22].hex() for r in vg if r["id"] == u}
          for u in units}
check("bytes 12 to 19 and 21 are constant within each of the five units",
      all(len(v) == 1 for v in consts.values()))
b = {u: next(iter({r["raw"] for r in vg if r["id"] == u})) for u in units}
check("older batch: byte 14 0x93, byte 21 0x09; newer batch: 0x13 and 0x0F",
      all((b[u][14], b[u][21]) == (0x93, 0x09) for u in V_OLD)
      and all((b[u][14], b[u][21]) == (0x13, 0x0F) for u in V_NEW))
check("the two newer units share bytes 12 and 13, 0x6c 0xc0",
      all(b[u][12:14] == bytes([0x6C, 0xC0]) for u in V_NEW))
check("byte 18: 0x7c on 007713, 0x8c on 007da9 and both newer units, 0x7b on 00846a",
      [b[u][18] for u in ("007713", "007da9", "00846a", "0077b2", "0080d9")]
      == [0x7C, 0x8C, 0x7B, 0x8C, 0x8C])
check("0x0077b2 lies between two older-batch identifiers", 0x007713 < 0x0077B2 < 0x007DA9)
for u in V_NEW:
    fs = [r for r in vg if r["id"] == u]
    hits = sum(r["m_raw"] == 192 + round(14.52 * r["pct"]) for r in fs)
    check(f"{u}: raw moisture is 192 + 14.52 x percent on {hits} of {len(fs)}",
          hits == len(fs), f"percentages seen {sorted({r['pct'] for r in fs})}")
check("and the newer units report nothing between 1 and 94 percent",
      all(r["pct"] == 0 or r["pct"] >= 95 for r in vg if r["id"] in V_NEW))
held = {u: sorted({r["m_raw"] for r in vg if r["id"] == u and r["file"] == V_FILES[0]}) for u in V_OLD}
check("older units held in open air: 581, 605 to 611, 586 to 587",
      [(h[0], h[-1]) for h in held.values()] == [(581, 581), (605, 611), (586, 587)], str(held))
for u, (n, slope, zero, hundred) in {"007713": (46, 9.41, 617, 1558),
                                     "007da9": (71, 10.02, 643, 1645),
                                     "00846a": (82, 10.01, 623, 1625)}.items():
    pts = sorted({(r["m_raw"], r["pct"]) for r in vg if r["id"] == u and 0 < r["pct"] < 100})
    a, bb = straight_line(pts)
    check(f"{u}: firmware line, our method, {n} points: {slope} counts/%, zero {zero}",
          len(pts) == n and abs(1 / bb - slope) < 0.005 and abs(-a / bb - zero) < 0.5
          and abs((100 - a) / bb - hundred) < 0.5,
          f"got {len(pts)} {1/bb:.2f} {-a/bb:.0f} {(100-a)/bb:.0f}")
for u, slope in {"007713": -0.183, "007da9": -0.180, "00846a": -0.159}.items():
    fs = [r for r in vg if r["id"] == u and r["file"] == V_FILES[1]
          and r["time"] >= "2026-10-11T11:56" and 10 <= r["ec"] <= 360 and r["pct"] > 50]
    a, bb = straight_line([(r["ec"], r["m_raw"]) for r in fs])
    check(f"{u}: in water at 16 to 350 uS/cm, raw moisture falls {slope} counts per uS/cm",
          abs(bb - slope) < 0.0005, f"{bb:.4f} over {len(fs)} transmissions")


def band(u, lo, hi):
    vals = sorted(r["m_raw"] for r in vg if r["id"] == u and r["pct"] > 50 and lo <= r["ec"] < hi)
    mid = len(vals) // 2
    return vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2


check("older units: raw moisture is lowest at 4,000 to 5,500 and rises from there to the ceiling",
      all(band(u, 4000, 5500) < band(u, 5500, 7000) < band(u, 7000, 9990) < band(u, 9990, 20000)
          for u in V_OLD),
      str({u: [band(u, *x) for x in ((4000, 5500), (5500, 7000), (7000, 9990), (9990, 20000))]
           for u in V_OLD}))

v_table = {1: (4.9, 350.0), 2: (310.0, 1049.8), 3: (1090, 1799), 4: (1850, 2700), 5: (2670, 3546),
           6: (3541, 4860), 7: (4310, 5355), 8: (5473, 6609), 9: (6522, 7969), 10: (7671, 9099),
           11: (8760, 10010), 12: (10001, 10007), 13: (10001, 10005)}
v_bad = []
for g, (lo, hi) in v_table.items():
    ec = [r["ec"] for r in vg if r["range"] == g]
    nd = 1 if g <= 2 else 0
    if (round(min(ec), nd), round(max(ec), nd)) != (lo, hi):
        v_bad.append((g, round(min(ec), 1), round(max(ec), 1)))
check("868 range table in behavior.md", not v_bad, str(v_bad))
v_gaps = []
for g in range(2, 11):
    vals = sorted({r["ec"] for r in vg if r["range"] == g})
    v_gaps.append(min(b - a for a, b in zip(vals, vals[1:]) if b - a > 3))
check("ranges 2 to 10: the smallest gap between values is 8.9 to 10.1 uS/cm",
      all(8.9 <= x <= 10.1 for x in v_gaps), str([round(x, 2) for x in v_gaps]))
for u in V_OLD:
    per = defaultdict(set)
    for r in vg:
        if r["id"] == u and 0 < r["pct"] < 100:
            per[r["pct"]].add(r["m_raw"])
    mean = sum(len(x) for x in per.values()) / len(per)
    check(f"{u}: several raw values per reported percent ({mean:.1f})", mean >= 2)
for u in V_OLD:
    rig = [r["m_raw"] for r in vg if r["id"] == u and r["file"] == V_FILES[1]
           and r["time"] < "2026-10-11T11:37"]
    check(f"{u}: dry in the rig within 2 counts of held in open air",
          max(abs(x - y) for x in rig for y in held[u]) <= 6
          and abs(sorted(rig)[len(rig) // 2] - sorted(held[u])[len(held[u]) // 2]) <= 2,
          f"rig {sorted(set(rig))}, held {held[u]}")
for u, (first, last) in {"007713": (1631, 1594), "00846a": (1629, 1590)}.items():
    w = sorted((r for r in vg if r["id"] == u and r["file"] == V_FILES[1] and r["pct"] > 50
                and r["time"] < "2026-10-11T11:56"), key=lambda r: r["time"])
    check(f"{u}: in distilled water before salt took effect, {first} falling to {last}",
          (w[0]["m_raw"], w[-1]["m_raw"]) == (first, last)
          and max(r["ec"] for r in w) < 16.1,
          f"{w[0]['time'][11:16]} to {w[-1]['time'][11:16]} UTC, EC up to {max(r['ec'] for r in w):.1f}")
for u, slope in {"007713": -0.075, "007da9": -0.090, "00846a": -0.083}.items():
    fs = [r for r in vg if r["id"] == u and r["file"] == V_FILES[2] and 400 <= r["ec"] <= 3000]
    a, bb = straight_line([(r["ec"], r["m_raw"]) for r in fs])
    check(f"{u}: at 400 to 3,000 uS/cm the slope is {slope}", abs(bb - slope) < 0.0005,
          f"{bb:.4f} over {len(fs)} transmissions")
# Five units in one solution: a 30-second grid over the low run, keeping only moments when
# every unit has reported within 80 s, repeated its previous value, and reads above 150.
from datetime import datetime, timedelta
low = [r for r in vg if r["file"] == V_FILES[1]]
when = lambda r: datetime.fromisoformat(r["time"].replace("Z", "+00:00"))
by_unit = {u: sorted((r for r in low if r["id"] == u), key=when) for u in units}
t0, t1 = min(map(when, low)), max(map(when, low))
spread = []
while t0 <= t1:
    vals = []
    for u in units:
        past = [r for r in by_unit[u] if when(r) <= t0]
        if len(past) < 2 or (t0 - when(past[-1])).total_seconds() > 80 or past[-1]["ec"] != past[-2]["ec"]:
            break
        vals.append(past[-1]["ec"])
    if len(vals) == 5 and min(vals) > 150:
        spread.append(max(vals) / min(vals))
    t0 += timedelta(seconds=30)
spread.sort()
check("five units in one solution: highest over lowest 1.112 to 1.212, median 1.155, 36 moments",
      len(spread) == 36 and round(spread[0], 3) == 1.112 and round(spread[-1], 3) == 1.212
      and round((spread[17] + spread[18]) / 2, 3) == 1.155,
      f"{len(spread)} moments, {spread[0]:.3f} to {spread[-1]:.3f}")

# Each wh52raw line follows the production decoder's line for the same burst.
pairs = agree = 0
for name in V_FILES:
    prev = None
    for line in open(os.path.join(V_DIR, name), encoding="utf-8"):
        if not line.strip():
            continue
        j = json.loads(line)
        if j.get("model") == "wh52raw" and prev and prev.get("model") == "Fineoffset-WH52" \
                and prev["time"] == j["time"]:
            hexed = j["rows"][0]["data"]
            raw = bytes.fromhex(hexed[:48]) if len(hexed) >= 48 else b""
            if len(raw) == 24 and crc8(raw[:22]) == raw[22] and sum(raw[:23]) & 0xFF == raw[23]:
                pairs += 1
                agree += (prev["id"] == raw[1:4].hex() and prev["moisture"] == raw[6]
                          and abs(prev["conductivity_uS_cm"]
                                  - (((raw[8] & 0x0F) << 16) | (raw[9] << 8) | raw[10]) / 25.6) < 0.01
                          and abs(prev["temperature_C"]
                                  - ((((raw[4] & 0x1F) << 8) | raw[5]) * 0.1 - 40)) < 0.06
                          and prev["battery_mV"] == raw[20] * 20)
        prev = j
check("every valid payload decodes to what the production decoder reported",
      pairs == agree == 1394, f"{agree} of {pairs}")
for u, sign in {"007713": -1, "00846a": +1}.items():
    fs = sorted((r for r in vg if r["id"] == u and r["file"] == V_FILES[1] and r["pct"] > 50
                 and r["time"] >= "2026-10-11T11:56" and 10 <= r["ec"] <= 360), key=lambda r: r["time"])
    steps = defaultdict(list)
    for r in fs:
        steps[round(r["ec"] / 10.13)].append(r["m_raw"])
    within = [v[-1] - v[0] for v in steps.values() if len(v) >= 3]
    mean = sum(within) / len(within)
    check(f"{u}: within one conductivity step the reading {'falls' if sign < 0 else 'does not fall'}",
          mean * sign > 0, f"mean {mean:+.2f} counts")
v_med = {"007713": (1324, 1357, 1423, 1481), "007da9": (1367, 1392, 1473, 1537),
         "00846a": (1326, 1357, 1446, 1498)}
got = {u: tuple(int(band(u, *x) + 0.5) for x in ((4000, 5500), (5500, 7000), (7000, 9990), (9990, 20000)))
       for u in V_OLD}
check("high-conductivity medians table", got == v_med, str(got))
first15 = {u: min(r["time"][11:16] for r in low if r["id"] == u and r["ec"] >= 15) for u in units}
check("early on the cup was not mixed: units first read 15 between 11:45 and 11:57 UTC",
      min(first15.values()) == "11:45" and max(first15.values()) == "11:57", str(first15))

gap = [r for r in series if 5400 < float(r["ec_uS_cm"]) < 9990 and float(r["temp_C"]) < 80]
check("our series has one reading between 5,400 uS/cm and the ceiling", len(gap) == 1,
      ", ".join(f"{r['probe']} {r['ec_uS_cm']}" for r in gap))
check("our sweep soil, 5 to 137 uS/cm, spans about fourteen 10.14 uS/cm levels",
      round((137 - 5) / 10.14) + 1 == 14)

check("in air the two newer units read exactly 192",
      all({r["m_raw"] for r in vg if r["id"] == u and r["file"] == V_FILES[0]} == {192} for u in V_NEW))

ours_top1 = {}
for r in series:
    if int(r["byte11"], 16) >> 4 == 1 and float(r["temp_C"]) < 80 and r["probe"].startswith("back_lawn"):
        ours_top1[r["probe"]] = max(ours_top1.get(r["probe"], 0), float(r["ec_uS_cm"]))
check("three of our four units read above 350 in range 1",
      sum(v > 350 for v in ours_top1.values()) == 3, str(ours_top1))

# Range changes at the ceiling, and the order in which ranges 1 to 11 first appear
v_moves = []
for name in V_FILES[1:]:
    for u in units:
        fs = sorted((r for r in vg if r["id"] == u and r["file"] == name), key=lambda r: r["time"])
        v_moves += [(u, a, b) for a, b in zip(fs, fs[1:]) if a["range"] != b["range"]]
rises = [(u, a["range"], b["range"]) for u, a, b in v_moves
         if a["ec"] >= 10000 and b["ec"] >= 10000 and b["range"] > a["range"] and b["ec"] < a["ec"]]
check("at the ceiling three units rose a range while the value fell slightly: 11 to 12 once, 12 to 13 twice",
      sorted(x[1:] for x in rises) == [(11, 12), (12, 13), (12, 13)] and len({x[0] for x in rises}) == 3,
      str(rises))
check("007da9 fell back once from 12 to 11",
      [(a["range"], b["range"]) for u, a, b in v_moves if u == "007da9" and b["range"] < a["range"]]
      == [(12, 11)])
order_ok = True
for u in units:
    first = {g: min(r["time"] for r in vg if r["id"] == u and r["range"] == g) for g in range(1, 12)}
    order_ok &= all(first[g] < first[g + 1] for g in range(1, 11))
check("every unit first reached ranges 1 to 11 in order", order_ok)
temps = [float(f"{(((b['raw'][4] & 0x1F) << 8) | b['raw'][5]) * 0.1 - 40:.1f}")
         for u, a, b in v_moves if (a["range"], b["range"]) == (1, 2)]
check("their 1 to 2 changes came within 1 degree C of each other",
      temps and max(temps) - min(temps) <= 1.0, f"{min(temps)} to {max(temps)} C")
close = []
for g in (11, 12):
    vals = sorted({r["ec"] for r in vg if r["range"] == g})
    close.append(min(b - a for a, b in zip(vals, vals[1:]) if b - a > 1))
check("ranges 11 and 12 have readings closer than 8.9 uS/cm", all(x < 8.9 for x in close),
      str([round(x, 2) for x in close]))
med77 = [band("0077b2", lo, hi) for lo, hi in ((120, 260), (260, 320), (320, 700), (700, 2000))]
check("0077b2's reading rises with salt above about 260, from 95 to 100 percent",
      med77 == sorted(med77) and med77[0] < med77[-1]
      and med77[0] == 192 + round(14.52 * 95) and med77[-1] == 192 + round(14.52 * 100), str(med77))
fits = {}
for u in V_OLD:
    pts = sorted({(r["m_raw"], r["pct"]) for r in vg if r["id"] == u and 0 < r["pct"] < 100})
    fits[u] = 1 / straight_line(pts)[1]
    check(f"{u}: its fitted frames lie between 70 and 99 percent",
          70 <= min(p for _, p in pts) and max(p for _, p in pts) <= 99)
check("007713 has the lowest slope of the seven units fitted", fits["007713"] < 9.86
      and fits["007713"] == min(fits.values()))
per_pct = []
for u in V_OLD:
    per = defaultdict(set)
    for r in vg:
        if r["id"] == u and 0 < r["pct"] < 100:
            per[r["pct"]].add(r["m_raw"])
    per_pct.append(sum(len(x) for x in per.values()) / len(per))
check("the older units average two to four raw values per percent",
      all(2 <= x <= 4 for x in per_pct), str([round(x, 1) for x in per_pct]))
w = sorted((r for r in vg if r["id"] == "00846a" and r["file"] == V_FILES[1] and r["pct"] > 50
            and r["time"] < "2026-10-11T11:56"), key=lambda r: r["time"])
mins = (when(w[-1]) - when(w[0])).total_seconds() / 60
check("00846a's fall in distilled water took about 17 minutes", 16 <= mins <= 18, f"{mins:.1f} min")
lo_s = {"007713": -0.183, "007da9": -0.180, "00846a": -0.159}
hi_s = {"007713": -0.075, "007da9": -0.090, "00846a": -0.083}
ratios = [lo_s[u] / hi_s[u] for u in V_OLD]
check("about twice as steep at low conductivity", all(1.8 <= x <= 2.5 for x in ratios),
      str([round(x, 2) for x in ratios]))
pts16 = [abs(lo_s[u]) * (320 - 16) / fits[u] for u in V_OLD]
check("5 to 6 percentage points between 16 and 320 uS/cm",
      all(4.5 <= x < 6.5 for x in pts16), str([round(x, 1) for x in pts16]))
pts5 = [abs(lo_s[u]) * (137 - 5) / fits[u] for u in V_OLD]
check("about 2 to 3 percentage points across 5 to 137 uS/cm",
      all(2 <= x <= 3 for x in pts5), str([round(x, 1) for x in pts5]))

print("\nDocument text (phrases that must not reappear)")
DOCS = {name: open(name, encoding="utf-8").read()
        for name in ("README.md", "behavior.md", "interpretation.md", "decoder.md",
                     "hardware.md", "errata.md", "sources.md",
                     "data/README.md", "data/captures/README.md")}
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
# A phrase may legitimately appear in a sentence that withdraws it. Those sentences
# are exempt; a bare restatement anywhere else is not. errata.md is exempt as a file,
# but its contents no longer switch the check off for every other file, which is what
# the earlier version did: three phrases, including the withdrawn temperature
# coefficient and the withdrawn permittivity range, were never being enforced at all.
CORRECTION_MARKERS = ("An earlier version", "earlier version of this file",
                      "which is wrong", "was wrong", "we withdrew", "had to withdraw")


def asserted_in(text, phrase):
    return [line for line in text.splitlines()
            if phrase in line and not any(m in line for m in CORRECTION_MARKERS)]


for phrase, why in BANNED:
    where = [n for n, t in DOCS.items()
             if n != "errata.md" and asserted_in(t, phrase)]
    check(f'withdrawn wording absent: "{phrase}"', not where,
          f"found in {where} ({why})" if where else why)

print()
if FAILED:
    print(f"{len(FAILED)} claim(s) do not reproduce:")
    for item in FAILED:
        print(f"  - {item}")
    sys.exit(1)
print("Every checked claim reproduces from the published data.")
