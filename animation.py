import json
import os

import matplotlib.pyplot as plt
import numpy as np
from utils import interpolate
import pandas as pd

if __name__ == '__main__':

    with open('planets_config.json', 'r') as f:
        config = json.load(f)
    bodies = config.keys()
    data = {body: pd.read_csv(os.path.join('ecliptic_coordinates', body, 'data.csv'), parse_dates=['timestamp'])
            for body in bodies}

    ts = pd.date_range(start='2021-01-01', end='2021-12-31', freq='1d')
    for i, time in enumerate(ts):
        ax = plt.subplot(polar=True, label=str(time.timestamp()))
        ax.set_facecolor('xkcd:very dark blue')
        ax.set_thetagrids([29, 53, 90, 118, 138, 174, 218, 241, 248, 267, 300, 328, 352], labels=[])
        ax.set_rgrids([])

        for body in bodies:
            ax.plot(
                interpolate(data[body], time, ['ecliptic_longitude']), 0., 'o',
                color='xkcd:' + config[body]['color'], markersize=config[body]['size'], alpha=0.9
            )

        ax.text(0, 2, '{:02d} {}'.format(time.day, time.month_name()))
        ax.set_rmin(-10)
        ax.set_rmax(1)

        plt.savefig(os.path.join('images', '{:05d}.png'.format(i)))
        # plt.show()
