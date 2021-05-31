# zodiac-wanderer
Clock of visible planets, where to find them in the sky : Sun, Moon, Mercury, Venus, Mars, Jupiter, Saturn.

We see them around us in a single circle, since they are in the same plane as the Earth (the ecliptic plane).
The angle on the clock corresponds to the **ecliptic longitude** viewed from Earth.

## Coordinates
The coordinates come from [NASA JPL Horizons](https://ssd.jpl.nasa.gov/horizons_batch.cgi),
which provides custom ephemerides.

- [`data.py`](data.py):
    - uses the config file [`data/config.json`](data/data_config.json)
    - creates a parsed CSV file per body, in [`data`](data)
