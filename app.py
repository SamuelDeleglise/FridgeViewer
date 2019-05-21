import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import pandas as pd
import plotly.graph_objs as go
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=[external_stylesheets])

#########################################################
# Acuquisition of data
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

#########################################################
# Layout of page

app.layout = html.Div([
    
    # Banner display
    html.Div([
        # Title
        html.H2('FridgeViewer',
            id='title',
            style={
                    'position': 'relative',
                    'top': '5px',
                    'left': '15px',
                    'font-family': 'Dosis',
                    'display': 'inline',
                    'font-size': '4.0rem',
                    'color': '#4D637F'
            }
        ),
        # Logo
        html.Img(src="https://tel.archives-ouvertes.fr/LKB-THESE/public/Logo_LKB.png",
            style={ 'top': '5px',
                    'height': '90px',
                    'float': 'right',
                    'position': 'relative',
                    'right': '15px'
            },
        )
    ],className="banner", style={'position': 'relative', 'right': '15px'}
    ),
    
    # Channel selection
    html.Div(className='tem_channel',children=[
        # Head
        html.Div([
            html.H2('Select the signal channel'),
           # head style
        ], style={'margin-left': '10px','margin-top': '10px'}
        ),
        # Channel selection dropdown
        dcc.Dropdown(id='channels_dropdown',
            options=[{'label': i, 'value': i} for i in CHANNELS],
            # defaut selections
            value=CHANNELS,
            multi=True,
        )
    # channel selection style
    ], style = {'left':'15px', 'right':'15px'}
    ),
    
    # Body
    dbc.Row(className="Row", children=[
        dbc.Col([        
            dcc.Graph(id='indicator-graphic',)
              # temp block style
            ], className='graph col', style={ 'height':'700px', 'float': 'left', 'display': 'inline-block'}
        ),
        dbc.Col([
            html.Div([
                dcc.DatePickerRange(id='date_range')
            # date range style
            ],style={'width': '100%', 'display': 'inline-block'}
            ),
          # selection block style
        ], className='selection col', style={'width': '25%', 'height':'700px', 'float': 'right', 'padding': 20, 'margin': 5, 'borderRadius': 5, 'border': 'thin lightgrey solid'}
        )
    ]),
        
        
    # Markdown Description
    html.Div(className='text',children=[
        html.Div(children=dcc.Markdown(),
                style={'width': '80%','margin': '30px auto'}
        )
    ])
])

#########################################################
# Callback and update

@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('channels_dropdown', 'value'),
     Input('date_range', 'end_date')],
     [State('date_range', 'start_date')])
def update_graph(channels, end_date, start_date):
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
    app.run_server(debug=True, host='localhost')