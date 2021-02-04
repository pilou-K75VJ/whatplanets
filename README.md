# zodiac-wanderer
Clock of visible planets, where to find them in the sky.

The angle on the clock corresponds to the **ecliptic longitude** viewed from Earth.

## Data
The data comes from [NASA JPL Horizons](https://ssd.jpl.nasa.gov/?horizons),
which provides custom ephemerides.

As documented in the link above, one way of sending requests the the service is by email.
It is done this way here:
- Send an email to [horizons@ssd.jpl.nasa.gov](mailto:horizons@ssd.jpl.nasa.gov)
- Subject header "JOB"
- Body of the email similar to the content of this [example file](batch-file.txt)

To make your own **ecliptic longitude ephemerides** request, modify the following fields:

- `START_TIME`
- `STOP_TIME`
- `STEP_SIZE` with the corresponding unit
- `QUANTITIES= '31'` asks for ecliptic longitude
- `COMMAND` to choose the target. 

    |Target|COMMAND|
    |---:|---|
    |Sun|'10'|
    |Mercury|'199'|
    |Venus|'299'|
    |Moon|'301'|
    |Mars|'499'|
    |Jupiter|'599'|
    |Saturn|'699'|
