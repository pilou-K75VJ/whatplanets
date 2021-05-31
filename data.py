import json
import os
from math import pi

import pandas as pd
import requests

from utils import equatorial_to_ecliptic


class Horizons:
    def __init__(self, data_dir, config='data_config.json'):
        self.data_dir = data_dir
        with open(os.path.join(self.data_dir, config), 'r') as f_config:
            self.config = json.load(f_config)
        self.bodies = list(self.config['bodies'].keys())

    def get_data(self, body):
        assert body in self.bodies, "Requested body not in config"
        url = "https://ssd.jpl.nasa.gov/horizons_batch.cgi"
        url += '?'
        for k, v in self.config['base'].items():
            if v is None:
                if 'TIME' in k:
                    v = self.config['time_range'][k]
                else:
                    v = self.config['bodies'][body][k]

            url += "&{}='{}'\n".format(k, v)

        txt_path = os.path.join(self.data_dir, '{}.txt'.format(body))
        with open(txt_path, 'w') as f_txt:
            response = requests.get(url).text
            f_txt.write(response)
        print('Created {} (size {}).'.format(txt_path, len(response)))

    def parse_data(self, body):
        txt_path = os.path.join(self.data_dir, '{}.txt'.format(body))
        csv_path = os.path.join(self.data_dir, '{}.csv'.format(body))
        with open(txt_path, 'r') as f_txt, open(csv_path, 'w') as f_csv:

            for line in f_txt:
                if line[:5] == '$$SOE':
                    break
                pass

            f_csv.write("timestamp,daylight,moon,ecliptic_longitude,ecliptic_latitude,\n")
            for line in f_txt:
                if line[:5] == '$$EOE':
                    break
                f_csv.write(line)

        # Clean data
        df = pd.read_csv(csv_path)[['timestamp', 'ecliptic_longitude', 'ecliptic_latitude']]

        df.timestamp = pd.to_datetime(df.timestamp.str.strip(), format='%Y-%b-%d %H:%M')
        df[['ecliptic_longitude', 'ecliptic_latitude']] = df[
            ['ecliptic_longitude', 'ecliptic_latitude']].astype('float').mul(pi / 180.)
        df.to_csv(csv_path, index=False)
        print('\tCreated {} (size {}).'.format(csv_path, len(df)))
        os.remove(txt_path)

    def main(self, bodies=None):
        if bodies is None:
            bodies = self.bodies
        elif isinstance(bodies, str):
            bodies = [bodies]

        for body in bodies:
            self.get_data(body)
            self.parse_data(body)

    def _dt_max(self, body, err=pi / 180.):
        """
        How much temporal resolution do we need?
        https://math.stackexchange.com/questions/1021799/bound-remainder-of-taylor-series-with-lipschitz-property-of-derivative
        """
        csv_path = os.path.join(self.data_dir, '{}.csv'.format(body))
        df = pd.read_csv(csv_path, parse_dates=['timestamp'])
        dt = (df.timestamp.iloc[1] - df.timestamp.iloc[0]).seconds

        dl = df.ecliptic_longitude.diff()
        dl = dl.where(dl.abs() < pi)
        dl = dl.div(dt)

        dl2 = dl.diff().div(dt)

        a_max = dl2.abs().quantile(0.999)
        v_max = dl.abs().quantile(0.999)

        dj_max_p = (err / v_max) / (3600. * 24.)
        dj_max_v = (2. * err / v_max) / (3600. * 24.)
        dj_max_a = ((2. * err / a_max) ** 0.5) / (3600. * 24.)

        print("{}: {:.1f}d / {:.1f}d / {:.1f}d".format(body, dj_max_p, dj_max_v, dj_max_a))

    def _dt_max_all(self, err=pi / 180.):
        for body in self.bodies:
            self._dt_max(body, err=err)


class Stars:
    """
    Parses the .dat star database retrieved from http://tdc-www.harvard.edu/catalogs/bsc5.html
    Extracts coordinates and magnitude, converts to ecliptic coordinates in a .csv
    """
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.dat_path = os.path.join(self.data_dir, 'bsc5.dat')
        self.csv_path = os.path.join(self.data_dir, 'bsc5.csv')

    def get_data(self):
        os.system("wget http://tdc-www.harvard.edu/catalogs/bsc5.dat.gz")
        os.system("gzip -d bsc5.dat.gz")
        os.system("rm -f bsc5.dat.gz")
        os.system("mv bsc5.dat {}".format(self.data_dir))

    def parse_data(self):
        with open(self.dat_path, 'r') as f_dat:
            data = {key: list() for key in ['RA', 'Dec', 'mag']}
            for line in f_dat:
                try:
                    data['RA'].append((float(line[75:77])
                                       + float(line[77:79]) / 60.
                                       + float(line[79:83]) / 3600.)
                                      * pi / 12.)
                    data['Dec'].append((1. if line[83] == '+' else -1.)
                                       * (float(line[84:86]) + float(line[86:88]) / 60. + float(line[88:90]) / 3600.)
                                       * pi / 180)
                    data['mag'].append(float(line[102:107]))
                except ValueError:
                    print('Error on line :\n{}'.format(line))
                    continue
        df = pd.DataFrame(data).sort_values('mag').reset_index(drop=True)
        df['ecliptic_longitude'], df['ecliptic_latitude'] = equatorial_to_ecliptic(df['RA'], df['Dec'])
        df.to_csv(self.csv_path, index=False)
        print('\tCreated {} (size {}).'.format(self.csv_path, len(df)))
        os.remove(self.dat_path)

    def main(self):
        self.get_data()
        self.parse_data()


if __name__ == '__main__':
    H = Horizons('data', config='data_config.json')
    H.main()

    S = Stars('data')
    S.main()
