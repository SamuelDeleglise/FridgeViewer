import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import plotly.graph_objs as go
from plotly import tools

import pandas as pd
import numpy as np
from datetime import timedelta, date


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=[external_stylesheets])
#########################################################
# Settings
# It requires that time series are same
CHANNELS = ['CH1 T', 'CH2 T', 'CH5 T', 'CH6 T']
PRESSURES = []
LEVELS = ['He3']

PATH_DATA = r'LOGS\DummyFridge\data'
# Date range
MIN_DATE_ALLOWED = date(2018, 8, 5)
MAX_DATE_ALLOWED = date.today()
INITIAL_MONTH = date.today()
END_DATE  = date.today()

#########################################################
# Time range 
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)

# Acquisition of data
def get_file(path):
    """ The original format of data is 'date,time,value',
        This function returns a pandas format with frames 'Date', 'Time', 'Value',
        Their types are 'object', 'datetime64[ns]', 'float64' accordingly.
    """
    df = pd.read_csv(path, sep=r",", names=['Date','Time','Value'], engine='python')
    df.Time = pd.to_datetime(df.Date +' '+ df.Time, format=' %d-%m-%y %H:%M:%S')
    # delete the 'Date', 'Time' has the information 
    df = df.drop('Date', 1)
    return df

# By defaut, it gets the data of today
def get_data(start_date=date.today(), end_date=date.today(), channels = CHANNELS):
    
    df_full = pd.DataFrame()
    for single_date in daterange(start_date, end_date + timedelta(days=1)):

        path = PATH_DATA + '\\' + single_date.strftime("%Y")+ '\\' + single_date.strftime("%y-%m-%d") + '\\'

        # for different channels, their data are saved in an object
        df_channel = pd.DataFrame()
        for i, chan in enumerate(channels):
            file_name = chan + ' ' + single_date.strftime("%y-%m-%d") + r'.log'

            # get the data from a file

            df = get_file(path + file_name)

            # delete the 'Date', 'Time' has the information 
            df = df.rename(columns={'Value': chan})
            if df_channel.empty:
                df_channel = df
            else: df_channel = pd.merge(df_channel, df, how='outer', on='Time')
        
        if df_full.empty:
            df_full = df_channel
        else: df_full = pd.concat([df_full, df_channel], axis=0)
    
    return df_full

path_data = os.path.dirname(os.path.abspath(__file__))

test_data = get_data(date(2019, 4, 13), date(2019, 4, 14))


TIMES1 = np.linspace(0,15, 200)
DATA1 = np.cos(TIMES1)
TIMES2 = np.linspace(0,15, 200)
DATA2 = np.sin(TIMES2)
#########################################################
# Update graph

def update_graph(graph_id,
                 graph_title,
                 channels_name,
                 run_log_json,
                 display_mode,
                 channels_selected,
                 truncation,
                 yaxis_title):
    """
    :param graph_id: ID for Dash callbacks
    :param graph_title: Displayed on layout
    :param channels_name: a lsit of channel names
    :param run_log_json: the json file containing the data
    :param display_mode: 'separate' or 'overlap'
    :param channels_selected: channels selected
    :param truncation: value between 0 and 1, at interval of 0.05
    :return: dcc Graph object containing the updated figures
    """

    if run_log_json:  
        # hidden log data exists
        layout = go.Layout(
        title=graph_title,
        margin=go.Margin(l=50, r=50, b=50, t=50),
        yaxis={'title': yaxis_title}
        )

        run_log_df = pd.read_json(run_log_json, orient='split')
        time = run_log_df['Time']

        # Select the channels if needed 
        # Get a list of displayed traces 
        trace = []
        for num, channel in enumerate(channels_name, start=1):
            if channel in channels_selected:
                trace.append(go.Scatter(x=time, y=run_log_df[channel], mode='lines', name=channel))

        num_trace = len(trace)       

        # if CHANNELS[0] in channels:
        #     data_1 = run_log_df[data_1_index]
        #     trace_1 = go.Scatter(x=time, y=data_1, mode='lines', name=CHANNELS[0])

        # if CHANNELS[1] in channels:
        #     data_2 = run_log_df[data_2_index]
        #     trace_2 = go.Scatter(x=time, y=data_2, mode='lines', name=CHANNELS[1])

        # if CHANNELS[2] in channels:
        #     data_3 = run_log_df[data_3_index]
        #     trace_3 = go.Scatter(x=time, y=data_3, mode='lines', name=CHANNELS[2])

        # if CHANNELS[3] in channels:
        #     data_4 = run_log_df[data_4_index]
        #     trace_4 = go.Scatter(x=time, y=data_4, mode='lines', name=CHANNELS[3])

        # 
        if display_mode == 'separate':
            figure = tools.make_subplots(rows=num_trace, cols=1, print_grid=False, shared_yaxes=True)
            
            for num, trace_item in enumerate(trace, start=1):
                figure.append_trace(trace_item, num, 1)

            figure['layout'].update(title=layout.title, margin=layout.margin,) # scene={'domain': {'x': (0., 0.5), 'y': (0.5,1)}}

        elif display_mode == 'overlap':
            figure = go.Figure(
                data=trace,
                layout=layout
            )
        else:
            figure = None

        return dcc.Graph(figure=figure, id=graph_id)
    return dcc.Graph(id=graph_id)

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


    # Head
    html.Div([
        html.H2('Select the signal channel'),
        # head style
    ], style={'margin-left': '10px','margin-top': '10px'}
    ),
    
    # Body
    dbc.Row(className="Row", children=[
        dbc.Col([
            dbc.Row([    
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
            
            # Real time control
            dcc.Interval(id="interval-log-update",
                n_intervals=0
            ),

            dbc.Row([     
                dcc.Graph(id='indicator-graphic',)
               # temperature graph style
            ], style = {'left':'0px', 'right':'0px'}
            ),

            dbc.Row([
                dcc.RangeSlider(
                    marks={i: 'Label {}'.format(i) for i in range(-5, 7)},
                    min=-5,
                    max=6,
                    value=[-3, 4]
                )
            ]),
            

            # Hidden Div Storing JSON-serialized dataframe of run log
            html.Div(id='run-log-storage', style={'display': 'none'}),
 
            # temperature col style
            ], className='graph col', style={ 'width':'70%', 'height':'100%', 'float': 'left', 'padding': 5, 'margin': 5, 'display': 'inline-block'}
        ),

        dbc.Col([

            dbc.Row([
                html.P("Scale:", style={'font-weight': 'bold', 'margin-bottom': '10px'}),

                dcc.DatePickerRange(id='date_range',
                    min_date_allowed=MIN_DATE_ALLOWED,
                    max_date_allowed=MAX_DATE_ALLOWED,
                    initial_visible_month=INITIAL_MONTH,
                    end_date=END_DATE,
                    style={'width': '100%'}
                )
            # date range style
            ],style={'width': '100%', 'margin-bottom': '20px' }
            ),
            
            
            dbc.Row([
                html.P("Update Speed:", style={'font-weight': 'bold', 'margin-bottom': '10px'}),

                html.Div(id='div-interval-control', children=[
                    dcc.Dropdown(id='dropdown-interval-control',
                        options=[
                            {'label': 'No Updates', 'value': 'no'},
                            {'label': 'Slow Updates', 'value': 'slow'},
                            {'label': 'Regular Updates', 'value': 'regular'},
                            {'label': 'Fast Updates', 'value': 'fast'}
                        ],
                        value='regular',
                        className='ten columns',
                        clearable=False,
                        searchable=False
                    ),
                ]),
            ],style={'width': '100%', 'margin-bottom': '20px' }
            ),

            dbc.Row([
                html.P("Plot Display mode:", style={'font-weight': 'bold', 'margin-bottom': '10px'}),

                dcc.RadioItems(
                    options=[
                        {'label': ' Overlapping', 'value': 'overlap'},
                        {'label': ' Separate', 'value': 'separate'},
                    ],
                    value='overlap',
                    id='display_mode'
                ),
            ], style={'width': '100%', 'margin-bottom': '20px' }
            )
          # selection block style
        ], className='selected col', style={'width': '25%', 'height':'100%', 'float': 'right', 'padding': 20, 'margin': 5, 'borderRadius': 5, 'border': 'thin lightgrey solid'}
        ),
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

# Callback the update speed
@app.callback(Output('interval-log-update', 'interval'),
              [Input('dropdown-interval-control', 'value')])
def update_interval_log_update(interval_rate):
    if interval_rate == 'fast':
        return 500

    elif interval_rate == 'regular':
        return 1000

    elif interval_rate == 'slow':
        return 5 * 1000

    # Refreshes every 24 hours
    elif interval_rate == 'no':
        return 24 * 60 * 60 * 1000

# Just get a hidden data
@app.callback(Output('run-log-storage', 'children'),
                  [Input('interval-log-update', 'n_intervals'), 
                  Input('date_range', 'start_date'),
                  Input('date_range', 'end_date')])
def get_run_log(n_intervals, start_date, end_date):
        
    try:
        run_log_df = get_data(start_date, end_date)
        json = run_log_df.to_json(orient='split')
    except FileNotFoundError as error:
        print(error)
        print("Please verify if the data is placed in the correct directory.")
        return None

    return json




@app.callback(
    Output('indicator-graphic', 'figure'),
    [Input('channels_dropdown', 'value'),
     Input('date_range', 'end_date')],
     [State('date_range', 'start_date')])
def update_graph(channels, end_date, start_date):
    print('updating')
    data = []
    if 'temp1' in channels:
        data = go.Scatter(
            x=test_data.Time,
            y=test_data.Value,
            mode='lines')
    return {
        'data': data}

if __name__ == '__main__':
    app.run_server(debug=True, host='localhost')