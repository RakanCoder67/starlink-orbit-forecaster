# Starlink Orbit Forecaster

Live demonstration: https://rakancoder67.github.io/starlink-orbit-forecaster/

Orbit forecasts for Starlink satellites from public TLE (two-line element) data, calculated with SGP4 and corrected by a frozen machine-learning model. Everything runs inside the page in the visitor's browser: no server, no account and no network request after the page has loaded.

## What the page contains
- Replay: eight Starlink satellites, forecasts compared with SpaceX's published ephemerides (25 Nov - 1 Dec 2024).
- Storm study: seven geomagnetic storms between May 2024 and January 2025, plain SGP4 against the corrected forecast.
- Run the real model: the frozen model embedded in the page (its SHA-256 fingerprint is checked when the page loads) forecasts 28 examples (4 per storm) or TLEs pasted by the visitor, and the result is compared with later TLEs of the same satellite.

## Files
- `index.html`: the complete page (code, data and the packed model in one file).

## Data and credits
- Orbit files (TLEs): published by Space-Track.org and collected in the dataset SpaceTrack-TimeSeries (Guo et al., 2025; DOI 10.6084/m9.figshare.29067764.v1; arXiv:2506.13034).
- Storm dates, Dst and Kp: NASA/SPDF OMNI2 hourly record.
- SGP4: satellite.js 5.0.0 (MIT licence, Shashwat Kandadai and contributors).
- Coastlines: Natural Earth 1:110m land (public domain).

## AI disclosure
The page, the browser forecaster and the scripts that generate its data and checks were written by Claude (Anthropic) on 31 October and 1 November 2026 for Rakan Alghamdi's Starlink orbit-prediction project.
