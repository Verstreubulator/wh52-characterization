#!/usr/bin/env python3
"""Parse Fine Offset / Ecowitt WH52 payloads into fields.

The production rtl_433 decoder reports moisture, temperature, conductivity and
battery voltage. It does not report the raw moisture measurement or the
conductivity range indicator, which are the fields this repository is about.

Capture the payloads with a flex decoder on a stock rtl_433:

    rtl_433 -f 915M -X 'n=wh52raw,m=FSK_PCM,s=58,l=58,r=5000,preamble=aa2dd4'

then feed the hex payloads to this script, one per line:

    rtl_433 ... -F json | python wh52_parse.py

It also reads from MQTT if rtl_433 is publishing there:

    python wh52_parse.py --mqtt <broker> --user <u> --password <p>

Frames failing either check byte are discarded. Byte 11 is NOT used as a
validity check; see errata.md for why that is a mistake.

Released under the GPL, version 2 or later, to match rtl_433.
"""

import argparse
import json
import sys


def crc8(data, poly=0x31, init=0x00):
    crc = init
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ poly) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc


def parse(payload_hex):
    """Return a dict of fields, or None if the frame is not a valid WH52 frame."""
    h = payload_hex.strip().lower()
    if h.startswith("0x"):
        h = h[2:]
    if len(h) < 48 or not h.startswith("a2"):
        return None
    try:
        b = bytes.fromhex(h[:48])
    except ValueError:
        return None

    if crc8(b[:22]) != b[22]:
        return None
    if (sum(b[:23]) & 0xFF) != b[23]:
        return None

    ec_raw = ((b[8] & 0x0F) << 16) | (b[9] << 8) | b[10]
    return {
        "id": h[2:8],
        "temperature_C": round((((b[4] & 0x1F) << 8) | b[5]) * 0.1 - 40.0, 1),
        "moisture_pct": b[6],
        "moisture_raw": ((b[8] & 0xF0) << 4) | b[7],
        "conductivity_uS_cm": round(ec_raw / 25.6, 1),
        "ec_raw": ec_raw,
        "ec_range": b[11] >> 4,
        "battery_mV": b[20] * 20,
        "boost": b[4] >> 5,
        "unknown_b12_b19": b[12:20].hex(),
        "unknown_b21": b[21],
    }


def payloads_from_line(line):
    """Yield hex payloads from a raw hex line or from rtl_433 JSON output."""
    line = line.strip()
    if not line:
        return
    if line.startswith("{"):
        try:
            j = json.loads(line)
        except ValueError:
            return
        for row in j.get("rows", []):
            if row.get("data"):
                yield row["data"]
        if j.get("codes"):
            for c in j["codes"]:
                yield c.split("}")[-1]
    else:
        yield line


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mqtt", help="broker host; omit to read stdin")
    ap.add_argument("--port", type=int, default=1883)
    ap.add_argument("--user")
    ap.add_argument("--password")
    ap.add_argument("--topic", default="rtl_433/+/devices/wh52raw/#")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")
    a = ap.parse_args()

    def emit(f):
        if not f:
            return
        if a.json:
            print(json.dumps(f), flush=True)
        else:
            print(
                f"{f['id']}  moisture {f['moisture_pct']:3d}%  raw {f['moisture_raw']:5d}  "
                f"{f['temperature_C']:6.1f}C  EC {f['conductivity_uS_cm']:9.1f} uS/cm  "
                f"range {f['ec_range']:2d}  batt {f['battery_mV']} mV",
                flush=True,
            )

    if a.mqtt:
        import paho.mqtt.client as mqtt

        def on_message(client, userdata, msg):
            for p in payloads_from_line(msg.payload.decode("utf-8", "ignore")):
                emit(parse(p))

        try:
            c = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        except Exception:
            c = mqtt.Client()
        if a.user:
            c.username_pw_set(a.user, a.password)
        c.on_message = on_message
        c.connect(a.mqtt, a.port, 30)
        c.subscribe(a.topic)
        c.loop_forever()
    else:
        for line in sys.stdin:
            for p in payloads_from_line(line):
                emit(parse(p))


if __name__ == "__main__":
    main()
