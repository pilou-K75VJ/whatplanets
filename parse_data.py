import os

import pandas as pd


def txt2csv(txtpath):
    path, ext = os.path.splitext(txtpath)
    if ext != '.txt':
        raise ValueError('Requires a .txt file but got {}'.format(txtpath))
    csvpath = path + '.csv'
    with open(txtpath, 'r') as txtfile, open(csvpath, 'w') as csvfile:
        for line in txtfile:
            if line[:5] == '$$SOE':
                break
        csvfile.write("timestamp,daylight,moon,ecliptic_longitude,ecliptic_latitude,\n")
        for line in txtfile:
            if line[:5] == '$$EOE':
                break
            csvfile.write(line)
    return csvpath


def parse_horizons(body=None):
    if body is None:
        body = str()

    data = dict()
    files = os.listdir('horizons/')
    for filename in files:
        name, ext = os.path.splitext(filename)
        if body not in name or ext != '.txt':
            continue

        filepath = txt2csv(os.path.join('horizons/', filename))

        df = pd.read_csv(filepath)[['timestamp', 'EcLon']]
        data[name] = pd.Series(
            name=name, data=df.EcLon.to_numpy(), dtype='float',
            index=pd.to_datetime(df.timestamp, format=' %Y-%b-%d %H:%M')
        )

    return pd.DataFrame(data)
