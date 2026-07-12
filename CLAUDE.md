# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A Raspberry Pi 4 aircraft tracker: it reads live ADS-B data from a local dump1090-fa instance and scrolls details of matching nearby aircraft on a 32x32 Adafruit RGB LED matrix. There is no build system, package manifest, linter, or test suite — just two Python scripts deployed to the Pi (`/home/flightradar/`) and run via systemd.

Development typically happens on this machine, but the code only fully runs on the Pi: `rgbtext.py` imports `rgbmatrix` (the hzeller rpi-rgb-led-matrix Python binding), which requires the LED matrix hardware.

## Commands

```bash
# Run the tracker loop (on the Pi; expects dump1090-fa on localhost:8080)
python3 fetch_aircraft_data.py

# Test the LED display directly (on the Pi)
python3 rgbtext.py --top="Top Line Text" --center="Center Line Text" --bottom="Bottom Line Text"

# Service management on the Pi
sudo systemctl restart fetch_aircraft_data.service
journalctl -u fr24feed -f
```

## Architecture

`fetch_aircraft_data.py` is the long-running entry point (installed as the `fetch_aircraft_data` systemd service, see `fetch_aircraft_data.service`). Its loop:

1. Polls `http://localhost:8080/data/aircraft.json` (dump1090-fa/SkyAware output).
2. Filters aircraft in `search_flight()`: currently by category (`A4`/`A5` = large/heavy), descending (`geom_rate < -0.1`), and below 15,000 ft. The `exact_terms`/`prefix_terms` callsign lists exist but are commented out of the filter condition.
3. Enriches matches from two sources:
   - Local SkyAware DB files (`/usr/share/skyaware/html/db`, hex-prefix JSON shards) via `lookup_hex_info()`.
   - The adsbdb.com API for flight route and aircraft owner details, wrapped in an in-memory `LRUCache` with 24h TTL. adsbdb answers 404 for unknown airframes/callsigns (common for brand-new registrations and military traffic); those misses are cached as `{}` so the API isn't re-queried every loop.
4. Displays each match by spawning `rgbtext.py` as a subprocess for ~6 seconds, then terminating it (`cleanup_subprocess` handles termination; the display script itself scrolls forever until killed). Display falls back gracefully: unknown airframe → local DB info, unknown route → callsign, nothing known → `Unknown aircraft <hex>`.

`rgbtext.py` is a standalone CLI that scrolls three text lines across the matrix. All LED panel options (rows, brightness, GPIO mapping, etc.) are argparse flags with defaults tuned for this hardware (32x32, `adafruit-hat`, brightness 20). It loads the font from the absolute path `/home/flightradar/rpi-rgb-led-matrix/fonts/7x13.bdf` (the rpi-rgb-led-matrix checkout on the Pi).

Hardcoded config at the top of `fetch_aircraft_data.py`: `api_url` and `db_folder`. Hex `4b15a2` (Swiss A350 HB-IFA) is special-cased in both lookup functions.

## Supporting files

- `mockdata/aircraft.json` — sample dump1090 API response for testing off-Pi; `mockdata/icao_ranges.json` — hex-range-to-country mapping.
- `:etc:fr24feed.ini`, `wpa_supplicant.conf` — reference copies of Pi config files (the fr24key/WiFi values are placeholders/local only).
- `update_aircraft_db.sh` + `update_aircraft_db.service` — oneshot systemd unit that refreshes the SkyAware DB from the FlightAware dump1090 repo (`~/dump1090` on the Pi) at boot.
- `fr24_knowledge_base/` — vendor PDFs.
- `README.md` — full hardware list and step-by-step Pi installation (fr24feed, piaware/dump1090-fa, RGB matrix driver, service setup).
