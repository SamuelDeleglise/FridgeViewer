import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas as pd
import plotly.graph_objs as go
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#app = dash.Dash(__name__)

######################################################
# Receive the data
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
    # Banner display
    html.Div([
        # Title
        html.H2('FridgeViewer',
            id='title',
            style={
                    'position': 'relative',
                    'top': '0px',
                    'left': '0px',
                    'font-family': 'Dosis',
                    'display': 'inline',
                    'font-size': '6.0rem',
                    'color': '#4D637F'
            }
        ),
        # Logo
        html.Img(src="https://tel.archives-ouvertes.fr/LKB-THESE/public/Logo_LKB.png",
            style={ 'top': '0px',
                    'height': '90px',
                    'float': 'right',
                    'position': 'relative',
                    'right': '0px'
            },
        )
    ],className="banner", style={'position': 'relative', 'right': '15px'}
    ),
    
    # Channel selection
    html.Div([
        html.Div([
            html.P('Select the signal channel'),
        ], style={'margin-left': '10px'}
        ),
        # Channel selection dropdown
        dcc.Dropdown(id='channel',
            options=[
                {'label': 'Tem RnO2', 'value': 'tem_rno2'},
                {'label': 'Tem 1Kpot', 'value': 'tem_kpot'},
                {'label': 'Tem Helium 3', 'value': 'temp_he'}
            ],
            # defaut selections
            value=['tem_rno2', 'tem_kpot','temp_he'],
            multi=True,
        )
    ],className='tem_channel' 
    ),

    # Tabs and Figure
    html.Div([
        # Tabs
        dcc.Tabs(id="tabs", 
            value='tab-1', 
            children=[
                dcc.Tab(label='Tab one', value='tab-1'),
                dcc.Tab(label='Tab two', value='tab-2'),
            ],style={'width': '250px'}
            ),
        # Tabs content
        html.Div(
            # Checklist of temperature 
            html.Div([
            dcc.Checklist(
                id='channels',
                options=[{'label': i, 'value': i} for i in CHANNELS],
                values=[]
            )],style={'width': '48%'}
            ),
            # Date Picker
            html.Div([
            dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=dt(1995, 8, 5),
                max_date_allowed=dt(2017, 9, 19),
                initial_visible_month=dt(2017, 8, 5),
                end_date=dt(2017, 8, 25)
            ),
            # Print picked date
            html.Div(id='output-container-date-picker-range')
            ],style={'display': 'inline-block'})
            ),
        # Real-time Graph 
        html.Div([
        dcc.Graph(id='indicator-graphic')
        ],style={'width': '100%', 'height':'600px', 'float': 'right', 'display': 'inline-block'}
        ),
    ]),
], className='container'
)

@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('channels', 'values'),
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