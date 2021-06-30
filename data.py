import argparse
import datetime
import json
import os
from math import pi

import numpy as np
import pandas as pd
import requests

from utils import equatorial_to_ecliptic


class Horizons:
    def __init__(self, data_dir, verbose=False):
        self.verbose = verbose

        self.data_dir = data_dir
        with open(os.path.join(self.data_dir, 'config.json'), 'r') as f_config:
            self.config = json.load(f_config)

        self.children = None
        self.children_index = None

        # Compute time cover
        time_cover = self.config['time_cover']
        time_range = self.config['time_range']
        if time_cover == 'all':
            self._make_children(time_range)
        elif time_cover == 'today':
            start = datetime.date.today().year - time_range // 2
            end = start + time_range - 1
            self.config['time_cover'] = '{}-{}'.format(start, end)

        if self.verbose:
            print('Data dir : {}'.format(self.data_dir))
            print('time cover : {}'.format(self.config['time_cover']))

        self.bodies = list(self.config['bodies'].keys())

    def _make_children(self, time_range):
        """
        Prepare hierarchical data structure
        """
        self.children = list()
        self.children_index = dict()
        for start in np.arange(1850, 2250, time_range):
            end = start + time_range - 1
            new_config = self.config.copy()
            new_config['time_cover'] = '{}-{}'.format(start, end)

            new_data_dir = os.path.join(self.data_dir, new_config['time_cover'])
            os.makedirs(new_data_dir, exist_ok=True)
            with open(os.path.join(new_data_dir, 'config.json'), 'w') as f_config:
                json.dump(new_config, f_config, indent=2)
                f_config.write("\n")
            self.children.append(Horizons(new_data_dir, verbose=self.verbose))

    def get_data(self, body):
        """
        Request to Nasa Horizons service
        """
        assert body in self.bodies, "Requested body not in config"

        # Wrapper for hierarchical data
        if self.children is not None:
            for c in self.children:
                c.get_data(body=body)
            return

        start, stop = self.config['time_cover'].split('-')

        # Constructing HTTP GET request
        url = "https://ssd.jpl.nasa.gov/horizons_batch.cgi"
        url += '?'
        for k, v in self.config['base'].items():
            if v is None:
                if k == "START_TIME":
                    v = '{}-01-01'.format(int(start))
                elif k == "STOP_TIME":
                    v = '{}-03-01'.format(int(stop) + 1)
                else:
                    v = self.config['bodies'][body][k]

            url += "&{}='{}'".format(k, v)

        if self.verbose:
            print('\nRequest :\n{}\n'.format(url))

        # Interrogating Nasa Horizons Service
        response = requests.get(url).text

        txt_path = os.path.join(self.data_dir, '{}.tmp.txt'.format(body))
        with open(txt_path, 'w') as f_txt:
            f_txt.write(response)

        if self.verbose:
            print('Created {} (size {} chars).'.format(txt_path, len(response)))

    def parse_data(self, body):
        """
        Transform raw response to formatted JSON
        """
        assert body in self.bodies, "Requested body not in config"

        # Wrapper for hierarchical data
        if self.children is not None:
            self.children_index[body] = list()
            for c in self.children:
                if c.parse_data(body=body):
                    self.children_index[body].append(c.config['time_cover'])
            return

        def path(ext):
            return os.path.join(self.data_dir, '{}.{}'.format(body, ext))

        # Transform to CSV
        with open(path('tmp.txt'), 'r') as f_txt:
            for line in f_txt:
                if line[:5] == '$$SOE':
                    break
            else:
                print('**\n** Not created: {}\n**'.format(path('csv')))
                return False

            with open(path('tmp.csv'), 'w') as f_csv:
                f_csv.write("timestamp,daylight,moon,ecliptic_longitude,ecliptic_latitude,\n")
                for n, line in enumerate(f_txt):
                    if line[:5] == '$$EOE':
                        break
                    f_csv.write(line)

        if self.verbose:
            print('Created {} (size {} lines).'.format(path('tmp.csv'), n))

        # Clean data
        date_format = '%Y%m%d'
        if self.config['bodies'][body]['STEP_SIZE'][-1] != 'd':
            date_format += '%H%M'
        df = pd.read_csv(path('tmp.csv'))[['timestamp', 'ecliptic_longitude']]
        df.ecliptic_longitude = df.ecliptic_longitude.astype('float').mul(pi / 180.).round(self.config['rounding'])
        df.timestamp = pd.to_datetime(df.timestamp.str.strip(), format='%Y-%b-%d %H:%M').dt.strftime(date_format)
        df = df.set_index('timestamp').ecliptic_longitude

        # Save as JSON
        df.to_json(path('json'))

        print('* Created {} (size {} lines).'.format(path('json'), len(df)))
        os.remove(path('tmp.txt'))
        os.remove(path('tmp.csv'))

        return True

    def main(self, bodies=None):
        if bodies is None:
            bodies = self.bodies
        elif isinstance(bodies, str):
            bodies = [bodies]

        for body in bodies:
            self.get_data(body)
            self.parse_data(body)
            if 'high_frequency' in self.data_dir:
                self._main_dt_max(body)

        if self.children is not None:
            with open(os.path.join(self.data_dir, 'index.json'), 'w') as f_index:
                json.dump(self.children_index, f_index, indent=2)
                f_index.write("\n")

    def _dt_max(self, body, err=pi / 180.):
        """
        How much temporal resolution do we need?
        https://math.stackexchange.com/questions/1021799/bound-remainder-of-taylor-series-with-lipschitz-property-of-derivative
        """
        json_path = os.path.join(self.data_dir, '{}.json'.format(body))
        df = pd.read_json(json_path, typ='series', convert_axes=False, convert_dates=False)
        df = pd.DataFrame(data={'timestamp': pd.to_datetime(df.index, format='%Y%m%d%H%M'),
                                'ecliptic_longitude': df.reset_index(drop=True)})
        dt = (df.timestamp.iloc[1] - df.timestamp.iloc[0]).seconds

        # Compute 1st and 2nd derivatives
        dl = df.ecliptic_longitude.diff()
        dl = dl.where(dl.abs() < pi)
        dl = dl.div(dt)
        dl2 = dl.diff().div(dt)

        # Compute Lipschitz constants
        a_max = dl2.abs().quantile(0.999)
        v_max = dl.abs().quantile(0.999)

        # Compute minimum dj (time resolution) for bounded error (< 1°)
        dj_max_p = (err / v_max) / (3600. * 24.)
        dj_max_v = (2. * err / v_max) / (3600. * 24.)
        dj_max_a = ((2. * err / a_max) ** 0.5) / (3600. * 24.)

        print("{}: {:.1f}d / {:.1f}d / {:.1f}d".format(body, dj_max_p, dj_max_v, dj_max_a))

    def _main_dt_max(self, bodies=None, err=pi / 180.):
        if bodies is None:
            bodies = self.bodies
        elif isinstance(bodies, str):
            bodies = [bodies]

        for body in bodies:
            try:
                self._dt_max(body, err=err)
            except FileNotFoundError:
                print('Did not find file for {}'.format(body))


class Stars:
    """
    Parses the .dat star database retrieved from http://tdc-www.harvard.edu/catalogs/bsc5.html
    Extracts coordinates and magnitude, converts to ecliptic coordinates in a JSON
    """

    def __init__(self, data_dir, verbose=False):
        self.verbose = verbose

        self.data_dir = data_dir
        if self.verbose:
            print('Data dir : {}'.format(self.data_dir))
        with open(os.path.join(self.data_dir, 'config.json'), 'r') as f_config:
            self.config = json.load(f_config)

    def get_data(self):
        if self.verbose:
            print('URL : {}'.format(self.config['url']))

        os.system("wget {}".format(self.config['url']))
        os.system("gzip -d bsc5.dat.gz")
        os.system("rm -f bsc5.dat.gz")
        os.system("mv bsc5.dat {}".format(self.data_dir))

    def parse_data(self):
        def path(ext):
            return os.path.join(self.data_dir, 'bsc5.{}'.format(ext))

        with open(path('dat'), 'r') as f_dat:
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

        if self.config['format'] == 'csv':
            df.to_csv(path('csv'), index=False)
        elif self.config['format'] == 'json':
            df.to_json(path('json'), orient='split', index=False)
        else:
            raise NotImplementedError

        print('* Created {} (size {} lines).'.format(path(self.config['format']), len(df)))
        os.remove(path('dat'))

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

    if args.stars is not None:
        S = Stars(args.stars, verbose=args.verbose)
        S.main()

    if args.planets is None and args.stars is None:
        parser.print_help()
