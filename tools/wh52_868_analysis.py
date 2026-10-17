#!/usr/bin/env python3
"""Summarise vgabor99's 868 MHz WH52 measurements from their three original files.

The data and the method are vgabor99's: five 868 MHz units, a distilled-water salt
series and open-air endpoints, posted on merbanan/rtl_433_tests#519 on 2026-10-11 and
kept unchanged in data/vgabor99-868-20261011/. This script prints the figures that
behavior.md and decoder.md draw from them; tools/verify_claims.py checks the ones the
documents quote.

Run it from the repository root:

    python tools/wh52_868_analysis.py data/vgabor99-868-20261011

Frames are validated on the CRC-8 (polynomial 0x31, initial 0, bytes 0 to 21) and the
sum byte only, never on bytes 11, 14 or 21; see errata.md for why. "Distinct" means
unique (device, time, payload), because rtl_433 reports the same burst more than once.
All times in the files are UTC, as vgabor99's receiver recorded them.

Copyright (C) 2026 Andreas Braunlich
Licensed under the GNU General Public License, version 2 or later.
"""
import collections, datetime as DT, json, os, statistics as S, sys

FILES = ['wh52_in_air_no51.json', 'wh52_low_range_no51.json', 'wh52_high_range_no51.json']
OLD, NEW = ('007713', '007da9', '00846a'), ('0077b2', '0080d9')


def crc8(data):
    c = 0
    for b in data:
        c ^= b
        for _ in range(8):
            c = ((c << 1) ^ 0x31) & 0xFF if c & 0x80 else (c << 1) & 0xFF
    return c


def lsq(x, y):
    mx, my = S.mean(x), S.mean(y)
    s = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sum((a - mx) ** 2 for a in x)
    return s, my - s * mx


def load(folder):
    rows, stats, paired, agree = [], {}, 0, 0
    for fn in FILES:
        lines = [json.loads(l) for l in open(os.path.join(folder, fn), encoding='utf-8') if l.strip()]
        st = collections.Counter()
        prev = None
        for j in lines:
            m = j.get('model')
            if m == 'Fineoffset-WH52':
                st['native'] += 1
            elif m == 'wh52raw':
                st['raw'] += 1
                h = j['rows'][0]['data']
                b = bytes.fromhex(h[:48]) if len(h) >= 48 else b''
                if not (len(b) == 24 and b[0] == 0xA2 and crc8(b[:22]) == b[22] and sum(b[:23]) & 0xFF == b[23]):
                    st['raw_fail'] += 1
                    prev = j
                    continue
                st['raw_ok'] += 1
                ec_raw = ((b[8] & 0x0F) << 16) | (b[9] << 8) | b[10]
                r = dict(file=fn, time=j['time'], t=DT.datetime.fromisoformat(j['time'].replace('Z', '+00:00')),
                         id=b[1:4].hex(), temp=round((((b[4] & 0x1F) << 8) | b[5]) * 0.1 - 40, 1), pct=b[6],
                         mraw=((b[8] & 0xF0) << 4) | b[7], ec_raw=ec_raw, ec=ec_raw / 25.6, rng=b[11] >> 4,
                         b11lo=b[11] & 0xF, b12_19=b[12:20].hex(), b14=b[14], b18=b[18], b20=b[20], b21=b[21],
                         payload=h[:48])
                rows.append(r)
                if prev and prev.get('model') == 'Fineoffset-WH52' and prev['time'] == j['time']:
                    paired += 1
                    agree += (prev['id'] == r['id'] and prev['moisture'] == r['pct']
                              and abs(prev['conductivity_uS_cm'] - r['ec']) < 0.01
                              and abs(prev['temperature_C'] - r['temp']) < 0.06 and prev['battery_mV'] == r['b20'] * 20)
            else:
                st['other'] += 1
            prev = j
        stats[fn] = dict(st)
    seen, d = set(), []
    for r in rows:
        k = (r['id'], r['time'], r['payload'])
        if k not in seen:
            seen.add(k)
            d.append(r)
    return rows, d, stats, paired, agree


def main(folder):
    rows, d, stats, paired, agree = load(folder)
    ids = sorted({r['id'] for r in d})
    print('== 1. Integrity')
    for fn, st in stats.items():
        print(f'  {fn}: {st}')
    print(f'  valid rows {len(rows)}; distinct transmissions {len(d)}; native/raw pairs {paired}, agreeing {agree}')

    print('\n== 2. Per-unit constants (whole session)')
    for i in ids:
        u = [r for r in d if r['id'] == i]
        print(f'  {i} n={len(u)} b12-19 {sorted({r["b12_19"] for r in u})} b14 {sorted({hex(r["b14"]) for r in u})}'
              f' b18 {sorted({hex(r["b18"]) for r in u})} b21 {sorted({hex(r["b21"]) for r in u})}'
              f' b11-low {sorted({r["b11lo"] for r in u})} b20 {min(r["b20"] for r in u)}-{max(r["b20"] for r in u)}'
              f' temp {min(r["temp"] for r in u)}-{max(r["temp"] for r in u)} C')

    print('\n== 3. ec_range (b11 >> 4) spans, all files')
    for g in sorted({r['rng'] for r in d}):
        u = [r for r in d if r['rng'] == g]
        print(f'  range {g:2d} n={len(u):3d} EC {min(r["ec"] for r in u):9.2f} - {max(r["ec"] for r in u):9.2f}'
              f' ec_raw {min(r["ec_raw"] for r in u)} - {max(r["ec_raw"] for r in u)} units {len({r["id"] for r in u})}')
    print('  transitions (consecutive frames of one unit, within one file):')
    for fn in FILES[1:]:
        for i in ids:
            u = sorted([r for r in d if r['id'] == i and r['file'] == fn], key=lambda r: r['t'])
            for a, b in zip(u, u[1:]):
                if a['rng'] != b['rng']:
                    print(f'    {i} {b["time"][11:19]}Z {a["rng"]:2d}->{b["rng"]:2d}  EC {a["ec"]:9.2f} -> {b["ec"]:9.2f}'
                          f'  ec_raw {a["ec_raw"]} -> {b["ec_raw"]}')
    for i in ids:
        u = sorted([r for r in d if r['id'] == i], key=lambda r: r['t'])
        r1 = max(r['ec'] for r in u if r['rng'] == 1)
        r2 = min(r['ec'] for r in u if r['rng'] == 2)
        print(f'  {i}: highest EC in range 1 = {r1:.2f}; lowest EC in range 2 = {r2:.2f}')

    print('\n== 4. EC step size (cluster distinct values, gap > 3 uS/cm)')
    for g in (1, 2):
        v = sorted({r['ec'] for r in d if r['rng'] == g})
        cl = [[v[0]]]
        for x in v[1:]:
            (cl[-1].append(x) if x - cl[-1][-1] <= 3 else cl.append([x]))
        cen = [S.mean(c) for c in cl]
        sp = [b - a for a, b in zip(cen, cen[1:])]
        print(f'  range {g}: {len(v)} distinct values in {len(cl)} clusters, {cen[0]:.2f} .. {cen[-1]:.2f};'
              f' spacing min {min(sp):.2f} max {max(sp):.2f}; widest cluster {max(max(c) - min(c) for c in cl):.2f}')
    r1 = sorted({r['ec'] for r in d if r['rng'] == 1})
    # fit a lattice on range 1
    ns = [round((x - 5.3) / 10.13) for x in r1]
    s, a = lsq(ns, r1)
    print(f'  range-1 lattice: step {s:.3f} uS/cm = {s * 25.6:.1f} counts, first step at {a:.2f}')
    for g in sorted({r['rng'] for r in d}):
        v = sorted({r['ec'] for r in d if r['rng'] == g and r['ec'] < 9999})
        gaps = sorted(b - x for x, b in zip(v, v[1:]) if b - x > 3)
        if gaps:
            print(f'    range {g:2d}: smallest gaps between distinct values {[round(x, 2) for x in gaps[:3]]}')

    print('\n== 5. moisture_raw')
    for i in ids:
        air = [r['mraw'] for r in d if r['id'] == i and r['file'] == FILES[0]]
        rig = [r['mraw'] for r in d if r['id'] == i and r['file'] == FILES[1] and r['time'][11:19] < '11:37:00']
        print(f'  {i} air(held) {min(air)}-{max(air)} n={len(air)}; dry in rig {min(rig)}-{max(rig)} n={len(rig)}')
    for i in NEW:
        u = [r for r in d if r['id'] == i]
        bad = [r for r in u if r['mraw'] != 192 + round(14.52 * r['pct'])]
        print(f'  {i}: mraw == 192 + round(14.52*pct) on {len(u) - len(bad)} of {len(u)}; pct seen {sorted({r["pct"] for r in u})}')
    for i in OLD:
        u = [r for r in d if r['id'] == i and 0 < r['pct'] < 100]
        s, z = lsq([r['pct'] + 0.5 for r in u], [r['mraw'] for r in u])
        per = collections.defaultdict(set)
        for r in u:
            per[r['pct']].add(r['mraw'])
        p100 = min(r['mraw'] for r in d if r['id'] == i and r['pct'] == 100)
        print(f'  {i}: firmware line (raw on pct+0.5, {len(u)} frames, pct {min(per)}-{max(per)}): {s:.2f} counts/%,'
              f' 0 % at {z:.0f}, 100 % at {z + 100 * s:.0f}; lowest raw reported as 100 % = {p100};'
              f' mean distinct raw values per percent {S.mean(len(x) for x in per.values()):.1f}')
    t_settle = DT.datetime(2026, 10, 11, 11, 56, tzinfo=DT.timezone.utc)
    for i in OLD:
        w = sorted([r for r in d if r['id'] == i and r['file'] == FILES[1] and r['pct'] > 50 and r['t'] < t_settle], key=lambda r: r['t'])
        print(f'  {i} distilled water, before 11:56Z: first {w[0]["mraw"]} ({w[0]["time"][11:16]}Z) last {w[-1]["mraw"]}'
              f' ({w[-1]["time"][11:16]}Z), EC {min(r["ec"] for r in w):.1f}-{max(r["ec"] for r in w):.1f}')
        u = [r for r in d if r['id'] == i and r['file'] == FILES[1] and r['t'] >= t_settle and 10 <= r['ec'] <= 360 and r['pct'] > 50]
        s, z = lsq([r['ec'] for r in u], [r['mraw'] for r in u])
        cl = {}
        for r in sorted(u, key=lambda r: r['t']):
            cl.setdefault(round(r['ec'] / 10.13), []).append(r['mraw'])
        within = [v[-1] - v[0] for v in cl.values() if len(v) >= 3]
        steps = [S.mean(cl[k2]) - S.mean(cl[k1]) for k1, k2 in zip(sorted(cl), sorted(cl)[1:])]
        h = [r for r in d if r['id'] == i and r['file'] == FILES[2] and 400 <= r['ec'] <= 3000]
        sh, _ = lsq([r['ec'] for r in h], [r['mraw'] for r in h])
        print(f'  {i} low-EC slope (after 11:56Z, EC {min(r["ec"] for r in u):.0f}-{max(r["ec"] for r in u):.0f}, n={len(u)}):'
              f' {s:.3f} counts per uS/cm; mean change within a plateau {S.mean(within):+.2f}, between plateaus {S.mean(steps):+.2f};'
              f' 400-3000 uS/cm slope {sh:.3f} (n={len(h)})')
    print('  median moisture_raw by EC band (submerged, pct > 50):')
    bands = [(0, 10), (10, 120), (120, 260), (260, 320), (320, 700), (700, 2000), (2000, 4000), (4000, 5500), (5500, 7000), (7000, 9990), (9990, 20000)]
    print('    band         ' + ' '.join(f'{i:>8}' for i in ids))
    for lo, hi in bands:
        cells = []
        for i in ids:
            u = [r['mraw'] for r in d if r['id'] == i and r['pct'] > 50 and lo <= r['ec'] < hi]
            cells.append(f'{S.median(u):8.0f}' if u else '       -')
        print(f'    {lo:5d}-{hi:<6d} ' + ' '.join(cells))

    print('\n== 6. Inter-unit EC, same solution (low file; grid 30 s; every unit stable and > 150 uS/cm)')
    f = [r for r in d if r['file'] == FILES[1]]
    by = {i: sorted([r for r in f if r['id'] == i], key=lambda r: r['t']) for i in ids}
    t, t1 = min(r['t'] for r in f), max(r['t'] for r in f)
    spread, ratio = [], {i: [] for i in ids}
    while t <= t1:
        vals = {}
        for i in ids:
            p = [r for r in by[i] if r['t'] <= t]
            if len(p) < 2 or (t - p[-1]['t']).total_seconds() > 80 or p[-1]['ec'] != p[-2]['ec']:
                vals = None
                break
            vals[i] = p[-1]['ec']
        if vals and all(v > 150 for v in vals.values()):
            spread.append(max(vals.values()) / min(vals.values()))
            med = S.median(vals.values())
            for i in ids:
                ratio[i].append(vals[i] / med)
        t += DT.timedelta(seconds=30)
    print(f'  {len(spread)} grid points; highest/lowest unit: median {S.median(spread):.3f}, range {min(spread):.3f}-{max(spread):.3f}')
    for i in ids:
        print(f'    {i} vs 5-unit median: {S.median(ratio[i]):.3f}')


if __name__ == '__main__':
    main(sys.argv[1])
