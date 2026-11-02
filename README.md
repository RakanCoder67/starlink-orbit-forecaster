# Starlink Orbit Forecaster

Live page: https://rakancoder67.github.io/starlink-orbit-forecaster/

A test of a machine-learning correction to the standard orbit forecast (SGP4) of Starlink satellites during geomagnetic storms: 14 storms from May 2024 to July 2026, a simple rule without machine learning as the baseline, a forward test with rules written down before the data were opened, and every limit stated. The page runs the real model inside the browser (no server, no account, no network request after the page has loaded) and works offline.

Version 6.0, built 2 Nov 2026, 16:01 (Saudi time).

## Result in one table
Typical (median) position error of forecasts that cover a storm, 1-5 days ahead, in km:

| Storms | Standard SGP4 | Simple rule (no ML) | Corrected (ML) | Corrected / simple rule |
|---|---|---|---|---|
| May 2024 - Jan 2025 (7 storms) | 30.4 | 11.7 | 5.4 | 0.46 |
| April - November 2025 (4 storms) | 25.9 | 12.3 | 6.9 | 0.56 |
| January - July 2026 (3 storms) | 64.5 | 21.6 | 14.4 | 0.67 |

## Read this first
- Most of the gain comes from a simple rule (B*=0 plus a correction of the speed along the track): at 1-5 days it delivers 75 % of the total gain in the 2024-25 storms.
- The model sees no space weather. All 17 inputs come from the satellite's own recent orbit files. This is a robustness test of a Starlink-specific correction during storms, not a model of how storms heat the atmosphere.
- The advantage of the learned part shrank in 2026: corrected / simple-rule error 0.46 in 2024-25, 0.56 in the 2025 storms, 0.67 in the 2026 storms, 0.95 in July 2026.
- Of the pre-set checks of the forward test, the no-harm check (FT3) and the shuffled-inputs control (FT6) failed for the 2026 storms, in one storm and one lead band; the uncertainty-range checks FU2 and FU3 failed.
- With the correction, 14 % of the 1-5 day forecasts in 2024-25 are worse than the standard forecast (21 % in 2025-26). The reference ("where the satellite really was") comes from later orbit files and carries about 2.4 km of its own noise.
- Starlink only; 1-29 days ahead; at least 10 orbit files.

## Files
- `index.html`: the whole page (trained model, forecaster in JavaScript, satellite.js and the example satellites are inside this one file).
- `detail.html`: the full detailed view (ground track, true-scale view, storm replays with Dst and Kp, quiet-week test against SpaceX positions), also one file. The file names are lower case; GitHub Pages is case-sensitive.
- `live.html`: Live forecasts. Pick a Starlink satellite, enter an exact UTC time and get the predicted position with the positional error of standard SGP4 corrected; shows the current NOAA space-weather status. It reads `live_tles.json` (made by `get_live_data.py`) when that file is next to the page, or a file the visitor loads.
- `get_live_data.py`: downloads recent orbit files from Space-Track (your own free login, nothing stored) and writes `live_tles.json`.
- `404.html`: shown for addresses that do not exist.
- `LICENSE`: MIT licence.
- `build_info.json`: version, size and fingerprints of the files.
- `offline/`: the same pages with instructions for a computer without internet.

## How it works
1. SGP4 turns the newest public orbit file (TLE) of a satellite into a forecast.
2. Decision trees (3 x 780 trees, gradient boosting), trained on 2024 data, add a correction from 17 inputs taken from the satellite's own orbit history.
3. Later orbit files show where the satellite really was; the page compares the two forecasts with them.

## Data and credits
- Orbit files (TLEs): Space-Track (https://www.space-track.org), collected for April 2024 - March 2025 in the dataset SpaceTrack-TimeSeries (Guo et al., 2025; https://doi.org/10.6084/m9.figshare.29067764.v1; https://arxiv.org/abs/2506.13034). Orbit files of 1 April 2025 to 14 September 2026 were downloaded from Space-Track directly and are not re-published. The TLE lines in the examples were re-created from stored orbital elements and rounded to the TLE format; they are not the original lines.
- Storm dates, Dst and Kp: NASA/SPDF OMNI2 hourly record (https://omniweb.gsfc.nasa.gov).
- SGP4 in the page: satellite.js 5.0.0 (MIT license, Shashwat Kandadai and contributors; https://github.com/shashwatak/satellite-js), with one change: the export of an internal initialization function.

## Licence
MIT, see `LICENSE`. Copyright (c) 2026 Rakan Alghamdi.
