import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas as pd
import plotly.graph_objs as go
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv(
    'https://gist.githubusercontent.com/chriddyp/'
    'cb5392c35661370d95f300086accea51/raw/'
    '8e0768211f6b747c0db42a9ce9a0937dafcbd8b2/'
    'indicators.csv')

available_indicators = df['Indicator Name'].unique()

CHANNELS = ['temp1', 'temp2']
TIMES1 = np.linspace(0,15, 200)
DATA1 = np.cos(TIMES1)
TIMES2 = np.linspace(0,15, 200)
DATA2 = np.sin(TIMES2)

app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Checklist(
                id='channels',
                    options=[{'label': i, 'value': i} for i in CHANNELS],
                    values=[])],
            style={'width': '48%', 'display': 'inline-block'}),
        html.Div([
            dcc.DatePickerRange(id='date_range'),
            html.Button('Submit', id='button')],
                
            style={'width': '48%', 'display': 'inline-block'}
            ),
        ]),
    html.Div([
            dcc.Graph(id='indicator-graphic')
            ],
            style={'width': '100%', 'height':'600px', 'float': 'right', 'display': 'inline-block'})
    ])
@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('channels', 'values'),
     Input('button', 'n_clicks'),
     Input('date_range', 'end_date')],
     [State('date_range', 'start_date')])
def update_graph(channels, n_clicks, end_date, start_date):
    print('updating')
    data = []
    if 'temp1' in channels:
        data.append(go.Scatter(
            x=TIMES1,
            y=DATA1,
            text='coucou',
            mode='lines'))
    if 'temp2' in channels:
        data.append(go.Scatter(
            x=TIMES2,
            y=DATA2,
            text='coucou',
            mode='lines'))
    return {
        'data': data}
if __name__ == '__main__':
    app.run_server(debug=True, host='10.214.1.36')