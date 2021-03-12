import os

import pandas as pd
from numpy import pi

from utils import equatorial_to_ecliptic


class HorizonsParser:
    """
    Parses the .txt coordinates tables retrieved from JPL Horizons service.
    Extracts timestamps and ecliptic coordinates to a .csv
    """
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.bodies = [b for b in os.listdir(self.root_dir) if os.path.isdir(os.path.join(self.root_dir, b))]

    def parse_data(self, body):
        # Extract CSV data
        txt_path = os.path.join(self.root_dir, body, 'data.txt')
        csv_path = os.path.join(self.root_dir, body, 'data.csv')
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

    def parse_all(self):
        for body in self.bodies:
            self.parse_data(body)


class YBSParser:
    """
    Parses the .dat star database retrieved from http://tdc-www.harvard.edu/catalogs/bsc5.html
    Extracts coordinates and magnitude, converts to ecliptic coordinates in a .csv
    """
    def __init__(self, dat_path):
        self.dat_path = dat_path
        self.csv_path = dat_path[:-4] + '.csv'

    def parse_data(self):
        with open(self.dat_path, 'r') as dat_file:
            data = {key: list() for key in ['RA', 'Dec', 'mag']}
            for line in dat_file:
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
        return df


if __name__ == '__main__':
    parser = HorizonsParser('./ecliptic_coordinates/')
    parser.parse_all()
