import os

import pandas as pd
from numpy import pi


class DataParser:
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


if __name__ == '__main__':
    data_parser = DataParser('./ecliptic_data/')
    data_parser.parse_all()
