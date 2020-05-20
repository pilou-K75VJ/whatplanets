import pandas as pd
import os


def txt2csv(txtpath):
    path, ext = os.path.splitext(txtpath)
    if ext != '.txt':
        return None
    csvpath = path + '.csv'
    with open(txtpath, 'r') as txtfile, open(csvpath, 'w') as csvfile:
        for line in txtfile:
            if line[:5] == '$$SOE':
                break
        csvfile.write("timestamp,daylight,moon,EcLon,EcLat,\n")
        for line in txtfile:
            if line[:5] == '$$EOE':
                break
            csvfile.write(line)
    return csvpath


def parse_horizons(body=None):
    if body is None:
        body = str()

    data = dict()
    for filename in os.listdir('horizons/'):
        name, ext = os.path.splitext(filename)
        if body not in name:
            continue

        filepath = txt2csv(os.path.join('horizons/', filename))
        if filepath is None:
            continue

        df = pd.read_csv(filepath)[['timestamp', 'EcLon']]
        data[name] = pd.Series(
            name=name, data=df.EcLon.to_numpy(), dtype='float',
            index=pd.to_datetime(df.timestamp, format=' %Y-%b-%d %H:%M')
        )

    return pd.DataFrame(data)


horizons = parse_horizons()

print('ok')
