import os.path as osp
import os
import numpy as np
from datetime import date

channels_values = {}
channels_times = {}


FOLDER = '.'
for filename in os.listdir(FOLDER):
    if filename.endswith('.chan'):
        ch_name = filename.rstrip('.chan') 
        with open(FOLDER + '/' + filename, 'rb') as f:
            data = np.frombuffer(f.read(), dtype=float)
            timestamps = data[::2]
            values = data[1::2]
#%%
            last_date = date.fromtimestamp(timestamps[0])
            index_last = 0
            for index, timestamp in enumerate(list(timestamps) + [0]):
                new_date = date.fromtimestamp(timestamp)
                if new_date!=last_date:
                    if not osp.exists('data'):
                        os.mkdir('data')
                    dir_year = 'data/' + str(last_date.year)
                    if not osp.exists(dir_year):
                        os.mkdir(dir_year)
                    short_date = last_date.strftime("%Y-%m-%d")[2:]
                    dir_day = dir_year + '/' + short_date
                    if not osp.exists(dir_day):
                        os.mkdir(dir_day)
                    with open(dir_day + '/' + ch_name + ' ' + short_date + '.chan', 'wb') as f:
                        f.write(data[2*index_last:2*index])
                    index_last = index
                    last_date = new_date