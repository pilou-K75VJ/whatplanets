# zodiac-wanderer
Clock of visible planets, where to find them in the sky.

The angle on the clock corresponds to the **ecliptic longitude** viewed from Earth.

## Data
The data comes from [NASA JPL Horizons](https://ssd.jpl.nasa.gov/?horizons),
which provides custom ephemerides.
One way of sending requests the the service is by email.

- [`request_generator.py`](request_generator.py):
    - uses the [`horizons_configuration.json`](ecliptic_data/horizons_configuration.json) file
    - opens web browser tabs with the email requests ready to be sent.
    - creates one directory per body

- You have to manually save the responses as `*.txt` files in the directories created

- [`data_parser.py`](data_parser.py) creates one `*.csv` file for each `*.txt` file, parsing the data received. 
