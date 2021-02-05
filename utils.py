import pandas as pd


def interpolate(dataframe, time, columns):
    t1 = dataframe.loc[dataframe.timestamp <= time].iloc[-1]
    t2 = dataframe.loc[dataframe.timestamp >= time].iloc[0]

    if t1.timestamp == t2.timestamp:
        return t1[columns]

    weight = (time - t1.timestamp) / (t2.timestamp - t1.timestamp)
    return (1 - weight) * t1[columns] + weight * t2[columns]
