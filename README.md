# Starlink Orbit Forecaster

Live page: https://rakancoder67.github.io/starlink-orbit-forecaster/

A small machine-learning model corrects the standard orbit forecast (SGP4) of Starlink satellites during geomagnetic storms. The page runs the real model inside the browser: pick a storm and a satellite and see the standard forecast, the corrected forecast and the later orbit files they are compared with. No server, no account and no network request after the page has loaded.

## The result in three numbers
Median position error of forecasts that cover a storm (seven storms, May 2024 to January 2025; every storm tested on a model that had not seen it):

| Forecast | Standard (SGP4) | With the correction | Smaller by |
|---|---|---|---|
| 1-5 days ahead | 30.4 km | 5.4 km | 82 % |
| 5-10 days ahead | 62.4 km | 5.1 km | 92 % |
| 10-29 days ahead | 418 km | 4.9 km | 99 % |

"Typical" means the median: half of the forecasts are better than the number shown. With the correction, 14.2 % of the 1-5 day forecasts ended up worse than the standard forecast. The reference ("where the satellite really was") comes from later orbit files, which carry about 2.4 km of their own uncertainty.

## What is on the page
- the three numbers above;
- a live example: two storms that came after the training of the model (9-10 November 2024 and 1-3 January 2025), four Starlink satellites each, forecast made on your device;
- how it works in three steps;
- a table with the result of each storm;
- details folded away: limits, checks, data and credits.

## How it works
1. SGP4 turns the newest public orbit file (TLE) of a satellite into a forecast.
2. A model of decision trees (3 x 780 trees), trained on 2024 data, adds a correction. It looks only at the satellite's own recent orbit history.
3. Later orbit files show where the satellite really was; the corrected forecast stays much closer.

## Files
- `index.html`: the whole page (the trained model, the forecaster in JavaScript, the satellite.js library and the example satellites are inside this one file).
- `README.md`: this text.

## Data and credits
- Orbit files (TLEs): Space-Track (https://www.space-track.org), collected in the dataset SpaceTrack-TimeSeries (Guo et al., 2025; https://doi.org/10.6084/m9.figshare.29067764.v1; https://arxiv.org/abs/2506.13034). The TLE lines in the examples were re-created from stored orbital elements and rounded to the TLE format; they are not the original lines.
- Storm dates, Dst and Kp: NASA/SPDF OMNI2 hourly record (https://omniweb.gsfc.nasa.gov).
- SGP4: satellite.js 5.0.0 (MIT license, Shashwat Kandadai and contributors; https://github.com/shashwatak/satellite-js), with one change: the export of an internal initialization function.
