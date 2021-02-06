import os

import matplotlib.pyplot as plt
import pandas as pd
from numpy import pi

if __name__ == '__main__':

    data = pd.read_csv('ecliptic_coordinates/mars2/data.csv', parse_dates=['timestamp'])
    data['rounds'] = data.ecliptic_longitude.diff().lt(-pi).cumsum()

    for i, row in data.iterrows():
        print(row.timestamp)

        past = data.loc[data.timestamp <= row.timestamp]

        ax1 = plt.subplot(121, polar=False, label=str(row.timestamp.timestamp()) + '1')
        ax1.set_facecolor('xkcd:very dark blue')

        for r in past.rounds.unique():
            past_round = past.loc[past.rounds == r]
            ax1.plot(past_round.ecliptic_longitude.mul(180. / pi), past_round.ecliptic_latitude.mul(180. / pi),
                     color='xkcd:rusty red', alpha=0.6)

        ax1.plot(row.ecliptic_longitude * 180. / pi, row.ecliptic_latitude * 180. / pi,
                 'o', color='xkcd:rusty red', markersize=10)
        ax1.set_xlim(0., 360.)
        ax1.set_ylim(-10., 10.)

        ax2 = plt.subplot(122, polar=True, label=str(row.timestamp.timestamp()) + '2')
        ax2.set_facecolor('xkcd:very dark blue')
        ax2.set_thetagrids([29, 53, 90, 118, 138, 174, 218, 241, 248, 267, 300, 328, 352], labels=[])
        ax2.set_rgrids([])

        past_last = past.loc[past.timestamp > row.timestamp - pd.to_timedelta(5*780, unit='d')]
        ax2.plot(past_last.ecliptic_longitude, past_last.ecliptic_latitude.mul(180. / pi), color='xkcd:rusty red', alpha=0.6)
        ax2.plot(row.ecliptic_longitude, row.ecliptic_latitude * 180. / pi,
                 'o', color='xkcd:rusty red', markersize=10)

        ax2.text(1.5 * pi, 15, '{:02d} {} {}'.format(row.timestamp.day, row.timestamp.month_name(), row.timestamp.year))
        ax2.set_rmin(-10)
        ax2.set_rmax(10)

        plt.savefig(os.path.join('images_mars', '{:05d}.png'.format(i)))
        # plt.show()
