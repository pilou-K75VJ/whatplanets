# zodiac-wanderer
Clock of visible planets, where to find them in the sky.

The angle on the clock corresponds to the **ecliptic longitude** viewed from Earth.

## Coordinates
The coordinates comes from [NASA JPL Horizons](https://ssd.jpl.nasa.gov/?horizons),
which provides custom ephemerides.
One way of sending requests to the service is by email.

- [`request_generator.py`](request_generator.py):
    - uses the config file [`ecliptic_coordinates/horizons_configuration.json`](ecliptic_coordinates/horizons_configuration.json)
    - opens web browser tabs with the email requests ready to be sent.
    - creates one directory per body, in [`ecliptic_coordinates`](./ecliptic_coordinates)

- You have to manually save the responses as `*.txt` files in the directories created

- [`data_parser.py`](data_parser.py) creates one `*.csv` file for each `*.txt` data file saved 
