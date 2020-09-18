import pandas as pd 
import numpy as np 
from itertools import islice
import matplotlib.pyplot as plt


data = pd.read_csv('GBPUSD_30M.csv', parse_dates=[0])
data.columns = map(str.lower, data.columns)
data.columns = data.columns.str.replace(' ', '_')
data['range'] = (data['close'] - data['open']) * 10000
data['body'] = np.where(data['range'] > 0, 'green', 'red')


def trend_bars():
    repeats = 1
    body = data['body'][0]
    trend = [{'body':body , 'repeats':repeats}]
    trend_index = 0
    for index, row in islice(data.iterrows(), 1, None):
        if row['body'] == trend[trend_index]['body']:
            repeats = repeats + 1
            trend[trend_index]['repeats'] = repeats
        else:
            repeats = 1
            trend.append({'body':row['body'], 'repeats':repeats})
            trend_index = trend_index + 1
    return trend

trend_bars = pd.DataFrame(trend_bars())

print(trend_bars['repeats'].value_counts(normalize=True))

# plt.plot(data['local_time'], data['range'])
# plt.show()