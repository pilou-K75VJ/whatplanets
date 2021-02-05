import json
import os
import shutil
import webbrowser

import pandas as pd
from numpy import pi

BASE_CONFIG = {
    "COMMAND": None,
    "CENTER": "500@399",
    "MAKE_EPHEM": "YES",
    "TABLE_TYPE": "OBSERVER",
    "START_TIME": None,
    "STOP_TIME": None,
    "STEP_SIZE": None,
    "CAL_FORMAT": "CAL",
    "TIME_DIGITS": "MINUTES",
    "ANG_FORMAT": "DEG",
    "OUT_UNITS": "KM-S",
    "RANGE_UNITS": "AU",
    "APPARENT": "AIRLESS",
    "SUPPRESS_RANGE_RATE": "NO",
    "SKIP_DAYLT": "NO",
    "EXTRA_PREC": "NO",
    "R_T_S_ONLY": "NO",
    "REF_SYSTEM": "J2000",
    "CSV_FORMAT": "YES",
    "OBJ_DATA": "NO",
    "QUANTITIES": "31",
}


def horizons_requests(root_dir):
    global BASE_CONFIG
    with open(os.path.join(root_dir, 'horizons_configuration.json'), 'r') as config_file:
        config = json.load(config_file)

    for body in config['bodies'].keys():
        body_dir = os.path.join(root_dir, body)

        if os.path.exists(body_dir):
            shutil.rmtree(body_dir)
        os.makedirs(body_dir)
        with open(os.path.join(body_dir, 'batch-file.txt'), 'w') as batch_file:

            batch_file.write('!$$SOF\n')
            for k, v in BASE_CONFIG.items():
                if v is None:
                    if 'TIME' in k:
                        v = config['time_range'][k]
                    else:
                        v = config['bodies'][body][k]
                batch_file.write("{}= '{}'\n".format(k, v))
            batch_file.write('!$$EOF\n')

        email_url = "mailto:horizons@ssd.jpl.nasa.gov"
        email_url += "?subject=JOB {}".format(body)
        with open(os.path.join(body_dir, 'batch-file.txt'), 'r') as batch_file:
            email_url += "&body={}".format(''.join(batch_file.readlines()))
        webbrowser.open(email_url.replace(' ', '%20').replace('\n', '%0A'))
        print('Created {}. Email ready to be sent.'.format(batch_file.name))
    return


def parse_data(root_dir):
    files = os.listdir(root_dir)
    for body in files:
        if not os.path.isdir(os.path.join(root_dir, body)):
            continue
        # Extract CSV data
        txt_path = os.path.join(root_dir, body, 'data.txt')
        csv_path = os.path.join(root_dir, body, 'data.csv')
        with open(txt_path, 'r') as txt_file, open(csv_path, 'w') as csv_file:

            for line in txt_file:
                if line[:5] == '$$SOE':
                    break

            csv_file.write("timestamp,daylight,moon,ecliptic_longitude,ecliptic_latitude,\n")

            for line in txt_file:
                if line[:5] == '$$EOE':
                    break
                csv_file.write(line)

        # Clean data
        df = pd.read_csv(csv_path)[['timestamp', 'ecliptic_longitude', 'ecliptic_latitude']]

        df[['ecliptic_longitude', 'ecliptic_latitude']] = df[
            ['ecliptic_longitude', 'ecliptic_latitude']].astype('float').mul(pi/180.)
        df.timestamp = pd.to_datetime(df.timestamp.str.strip(), format='%Y-%b-%d %H:%M')

        df.to_csv(csv_path, index=False)
        print('Created {}.'.format(csv_path))
    return
