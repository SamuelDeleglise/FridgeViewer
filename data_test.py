import pandas as pd
from pandas.compat import StringIO
import os

import plotly.plotly as py
import plotly.graph_objs as go

temp=u"""13-04-19,00:00:23,7.526100E-8
 13-04-19,00:01:23,7.526400E-8
 13-04-19,00:02:23,7.528200E-8"""
 
#after testing replace StringIO(temp) to filename
df = pd.read_csv(StringIO(temp), sep="\,", names=['Date','Time','Value'], engine='python')
df.Time = pd.to_datetime(df.Date +' '+ df.Time, format='%d-%m-%y %H:%M:%S')


def get_data(path):
    """ The original format of data is 'date,time,value',
        This function returns a pandas format with frames 'Date', 'Time', 'Value',
        Their types are 'object', 'datetime64[ns]', 'float64' accordingly.
    """
    df = pd.read_csv(path, sep="\,", names=['Date','Time','Value'], engine='python')
    df.Time = pd.to_datetime(df.Date +' '+ df.Time, format='%d-%m-%y %H:%M:%S')
    return df

def select_path(channel, date, time):
    path = ''
    return path


path_data = os.path.dirname(os.path.abspath(__file__))

a = get_data(r'LOGS\DummyFridge\data\2019\19-04-13\CH1 T 19-04-13.log')
b= get_data(r'LOGS\DummyFridge\data\2019\19-04-13\CH2 T 19-04-13.log')

c = pd.concat([test_data, test_data2], ignore_index=True)

d = pd.merge(a,b, how='outer', on='Time')

c 