# -*- coding: utf-8 -*-
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

test_data = get_data(r'LOGS\DummyFridge\data\2019\19-04-13\CH1 P 19-04-13.log')
################################################################################
import dash
import dash_core_components as dcc
import dash_html_components as html
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': test_data.Time, 'y': test_data.Value, 'name': 'SF'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)