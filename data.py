import argparse
import datetime
import json
import os
from math import pi

import pandas as pd
import numpy as np
import requests

from utils import equatorial_to_ecliptic


class Horizons:
    def __init__(self, data_dir, verbose=False):
        self.verbose = verbose

        self.data_dir = data_dir
        with open(os.path.join(self.data_dir, 'config.json'), 'r') as f_config:
            self.config = json.load(f_config)

        self.children = None
        time_cover = self.config['time_cover']
        if time_cover['cover'] == 'all':
            self._make_children(time_cover)
        elif time_cover['cover'] == 'today':
            start = datetime.date.today().year - time_cover['range'] // 2
            end = start + time_cover['range'] - 1
            self.config['time_cover']['cover'] = '{}-{}'.format(start, end)
        if self.verbose:
            print('Data dir : {}'.format(self.data_dir))
            print('time cover : {}'.format(self.config['time_cover']['cover']))

        self.bodies = list(self.config['bodies'].keys())

    def _make_children(self, time_cover):
        self.children = list()
        for start in np.arange(1850, 2250, time_cover['range']):
            end = start + time_cover['range'] - 1
            new_config = self.config.copy()
            new_config['time_cover']['cover'] = '{}-{}'.format(start, end)

            new_data_dir = os.path.join(self.data_dir, '{}-{}'.format(start, end))
            os.makedirs(new_data_dir, exist_ok=True)
            with open(os.path.join(new_data_dir, 'config.json'), 'w') as f_config:
                json.dump(new_config, f_config, indent=2)
                f_config.write("\n")
            self.children.append(Horizons(new_data_dir, verbose=self.verbose))

    def get_data(self, body):
        assert body in self.bodies, "Requested body not in config"

        start, stop = self.config['time_cover']['cover'].split('-')

        url = "https://ssd.jpl.nasa.gov/horizons_batch.cgi"
        url += '?'
        for k, v in self.config['base'].items():
            if v is None:
                if k == "START_TIME":
                    v = '{}-01-01'.format(start)
                elif k == "STOP_TIME":
                    v = '{}-12-31'.format(stop)
                else:
                    v = self.config['bodies'][body][k]

            url += "&{}='{}'".format(k, v)
        if self.verbose:
            print('\nRequest :\n{}\n'.format(url))

        txt_path = os.path.join(self.data_dir, '{}.txt'.format(body))
        with open(txt_path, 'w') as f_txt:
            response = requests.get(url).text
            f_txt.write(response)
        if self.verbose:
            print('Created {} (size {} chars).'.format(txt_path, len(response)))

    def parse_data(self, body):
        assert body in self.bodies, "Requested body not in config"

        txt_path = os.path.join(self.data_dir, '{}.txt'.format(body))
        csv_path = os.path.join(self.data_dir, '{}.csv'.format(body))
        with open(txt_path, 'r') as f_txt:
            for line in f_txt:
                if line[:5] == '$$SOE':
                    break
            else:
                print('**\n** Not created: {}\n**'.format(csv_path))
                return

            with open(csv_path, 'w') as f_csv:
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

        for k, v in self.config['rounding'].items():
          df[k] = df[k].round(v)

        df.to_csv(csv_path, index=False)
        print('* Created {} (size {} lines).'.format(csv_path, len(df)))
        os.remove(txt_path)

    def main(self, bodies=None):

        if self.children is not None:
            for c in self.children:
                c.main(bodies=bodies)
            return

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
            try:
                self._dt_max(body, err=err)
            except FileNotFoundError:
                print('Did not find file for {}'.format(body))


class Stars:
    """
    Parses the .dat star database retrieved from http://tdc-www.harvard.edu/catalogs/bsc5.html
    Extracts coordinates and magnitude, converts to ecliptic coordinates in a .csv
    """
    def __init__(self, data_dir, verbose=False):
        self.verbose = verbose

        self.data_dir = data_dir
        if self.verbose:
            print('Data dir : {}'.format(self.data_dir))
        with open(os.path.join(self.data_dir, 'config.json'), 'r') as f_config:
            self.config = json.load(f_config)
        self.dat_path = os.path.join(self.data_dir, 'bsc5.dat')
        self.csv_path = os.path.join(self.data_dir, 'bsc5.csv')

    def get_data(self):
        if self.verbose:
            print('URL : {}'.format(self.config['url']))
        os.system("wget {}".format(self.config['url']))
        os.system("gzip -d bsc5.dat.gz")
        os.system("rm -f bsc5.dat.gz")
        os.system("mv bsc5.dat {}".format(self.data_dir))

    def parse_data(self):
        with open(self.dat_path, 'r') as f_dat:
            data = {key: list() for key in ['RA', 'Dec', 'magnitude']}
            for line in f_dat:
                try:
                    data['RA'].append((float(line[75:77])
                                       + float(line[77:79]) / 60.
                                       + float(line[79:83]) / 3600.)
                                      * pi / 12.)
                    data['Dec'].append((1. if line[83] == '+' else -1.)
                                       * (float(line[84:86]) + float(line[86:88]) / 60. + float(line[88:90]) / 3600.)
                                       * pi / 180)
                    data['magnitude'].append(float(line[102:107]))
                except ValueError:
                    if self.verbose:
                        print('Error on line :\n{}'.format(line))
                    continue
        df = pd.DataFrame(data).sort_values('magnitude').reset_index(drop=True)
        df['ecliptic_longitude'], df['ecliptic_latitude'] = equatorial_to_ecliptic(df['RA'], df['Dec'])
        for k, v in self.config['rounding'].items():
          df[k] = df[k].round(v)

        df = df.drop(['RA', 'Dec'], axis='columns')
        df.to_csv(self.csv_path, index=False)
        print('* Created {} (size {} lines).'.format(self.csv_path, len(df)))
        os.remove(self.dat_path)

    def main(self):
        self.get_data()
        self.parse_data()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--planets', type=str, default=None,
                        help='Directory to put planets data in. Must contain config.json')
    parser.add_argument('--stars', type=str, default=None,
                        help='Directory to put stars data in. Must contain config.json')
    parser.add_argument('--verbose', action='store_true')
    args = parser.parse_args()

    if args.planets is not None:
        H = Horizons(args.planets, verbose=args.verbose)
        H.main()
        # H._dt_max_all()

    if args.stars is not None:
        S = Stars(args.stars, verbose=args.verbose)
        S.main()

    if args.planets is None and args.stars is None:
        parser.print_help()
