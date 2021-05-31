import numpy as np


def interpolate(dataframe, time, columns):
    t1 = dataframe.loc[dataframe.timestamp <= time].iloc[-1]
    t2 = dataframe.loc[dataframe.timestamp >= time].iloc[0]

    if t1.timestamp == t2.timestamp:
        return t1[columns]

    weight = (time - t1.timestamp) / (t2.timestamp - t1.timestamp)
    return (1 - weight) * t1[columns] + weight * t2[columns]


def equatorial_to_ecliptic(ra, dec):
    """
    Copied from
    http://www.mathworks.com/matlabcentral/fileexchange/23285-conversion-between-equatorial-and-ecliptic-coordinates
    """

    if isinstance(ra, float) or isinstance(ra, int):
        return equatorial_to_ecliptic(np.array([ra]), np.array([dec]))

    tilt = 23.43655 * np.pi / 180.

    sin_lat = np.sin(dec) * np.cos(tilt) - np.cos(dec) * np.sin(tilt) * np.sin(ra)

    cos_lon_cos_lat = np.cos(dec) * np.cos(ra)
    sin_lon_cos_lat = np.sin(dec) * np.sin(tilt) + np.cos(dec) * np.cos(tilt) * np.sin(ra)
    cos_lat = np.sqrt(sin_lon_cos_lat ** 2 + cos_lon_cos_lat ** 2)

    longitude = np.arctan2(sin_lon_cos_lat, cos_lon_cos_lat)
    latitude = np.arctan2(sin_lat, cos_lat)

    r2 = np.sqrt(sin_lat ** 2 + cos_lat ** 2)
    if max(abs(r2 - 1.)) > 1e-9:
        raise ValueError('Latitude conversion radius is not uniformly 1')
    return longitude, latitude
