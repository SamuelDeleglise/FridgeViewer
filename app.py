import os
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

import pandas as pd
import plotly.graph_objs as go
from plotly import tools
import numpy as np
from datetime import timedelta, date, time, datetime

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=[external_stylesheets])
server = app.server
app.config.suppress_callback_exceptions = True

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
TODAY_DATE  = date.today()
TEST_MODE = True


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
def get_data_simple(start_date=date.today(), end_date=date.today(), channels = CHANNELS):
    
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

def get_data(start_date=date.today(), end_date=date.today(), channels = CHANNELS):
    
    df_full = pd.DataFrame()
    for single_date in daterange(start_date, end_date + timedelta(days=1)):
        
        path = PATH_DATA + '\\' + single_date.strftime("%Y")+ '\\' + single_date.strftime("%y-%m-%d") + '\\'
        # for different channels, their data are saved in an object
        df_channel = pd.DataFrame()
        for chan in channels:
            file_name = chan + ' ' + single_date.strftime("%y-%m-%d") + r'.log'

            # get the data from a file
            df = get_file(path + file_name)

            # delete the 'Date', 'Time' has the information 
            df = df.rename(columns={'Value': chan})
            df = df.rename(columns={'Time': 'Time_'+chan})
            if df_channel.empty:
                df_channel = df
            else: df_channel = pd.concat([df_channel, df], axis=1)
        
        if df_full.empty:
            df_full = df_channel
        else: df_full = pd.concat([df_full, df_channel], axis=0)
    return df_full


# test mode data
path_data = os.path.dirname(os.path.abspath(__file__))
test_data = get_data(date(2019, 4, 13), date(2019, 4, 14))
test_data2 = get_data(date(2019, 4, 13), date(2019, 4, 14))

#########################################################
if 'DYNO' in os.environ:
    app_name = os.environ['FridgeViewer']
else:
    app_name = 'dash-timeseriesplot'

#########################################################
# Layout of page

app.layout = html.Div([
    
    # Banner display
    html.Div([
        # Title
        html.H1('FridgeViewer',
            id='title',
            style={
                    'position': 'relative',
                    'top': '5px',
                    'left': '15px',
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
               #dcc.Graph(id='temperature-graph')
            
               # temperature graph style
            ], id='graph_firework', style = {'left':'0px', 'right':'0px'}
            ),
            
            # # Hidden Div Storing JSON-serialized dataframe of run log
            # html.Div(id='run-log-storage', style={'display': 'none'}),
 
            # temperature col style
            ], className='graph col', style={'width': '80%','float': 'left', 'padding': 5, 'margin': 0, 'display': 'inline-block'}
        ),

        dbc.Col([

            dbc.Row([
                html.P("Scale:", style={'font-weight': 'bold', 'margin-bottom': '10px'}),

                dcc.DatePickerRange(id='date_range',

                        end_date = date(2019, 4, 14),
                        start_date = date(2019, 4, 13),
                        style={'width': '100%'},

                        # min_date_allowed=MIN_DATE_ALLOWED,
                        # max_date_allowed=MAX_DATE_ALLOWED,
                        # initial_visible_month=INITIAL_MONTH,
                        # end_date=TODAY_DATE,
                        # start_date= TODAY_DATE,
                        # style={'width': '100%'}
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
            ], className='side bar', style={'width': '100%', 'margin-bottom': '20px' }
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
            ],  className='side bar', style={'width': '100%', 'margin-bottom': '20px' }
            ),
                
            dbc.Row(id="div-num-display",
                    className='side bar'
            )
          # selection block style
        ], className='selected col', style={'width': '15%', 'height':'100%', 'float': 'right', 'padding': 15, 'margin': 5, 'borderRadius': 5, 'border': 'thin lightgrey solid'}
        ),
    ]),
        
        
    # Markdown Description
    html.Div(className='text',children=[
        html.Div(children=dcc.Markdown(),
                style={'width': '80%','margin': '30px auto'}
        )
    ]),
], className="container")


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

# # Just get a hidden data
# @app.callback(Output('run-log-storage', 'children'),
#                   [Input('interval-log-update', 'n_intervals'), 
#                   Input('date_range', 'start_date'),
#                   Input('date_range', 'end_date')])
# def get_run_log(n_intervals, start_date, end_date):
#     try:
#         if TEST_MODE:
#             run_log_df = test_data
#             print('1')
#             print(run_log_df)
#             print(run_log_df['Time_CH1 T'])
#             print(run_log_df['Time_CH5 T'])
         
#         else: 
#             run_log_df = get_data(start_date, end_date, CHANNELS)
        
#         json_data = run_log_df.to_json(orient='split')
#         # print('This is json', json_data)
#     except FileNotFoundError as error:
       
#         print(error)
#         print("Please verify if the data is placed in the correct directory.")
#         return None
#     return json_data

# @app.callback(Output('div-num-display', 'children'),
#               [Input('run-log-storage', 'children')])
# def update_num_display_and_time(run_log_json):
#     if run_log_json:
        
#         run_log_df = pd.read_json(run_log_json, orient='split')

#         return html.Div([html.P("Number of data points:", style={'font-weight': 'bold', 'margin-bottom': '10px'}),
#                 html.H2(f"{run_log_df.shape[0]}", style={'margin-top': '3px'})])
#     else:
#         print('There is no cache data')


@app.callback(Output('graph_firework', 'children'),
            [Input('date_range', 'start_date'),
            Input('date_range', 'end_date'),   # Input('run-log-storage', 'children')
            Input('channels_dropdown', 'value'),
            Input('display_mode','value')])
def update_graph(start_date, end_date, selected_dropdown_value, display_mode_value):
    try:
        if TEST_MODE:
            df = test_data    
        else: 
            df = get_data(start_date, end_date, CHANNELS)

    except FileNotFoundError as error:
        print(error)
        print("Please verify if the data is placed in the correct directory.")

    # create vide trace
    trace = []
    for channel in selected_dropdown_value:
        key_time = 'Time_'+channel
        key = channel

        df[key_time] = pd.to_datetime(df[key_time])

        trace.append(go.Scatter(x=df[key_time], y=df[key],mode='lines',
        opacity=0.7,name=channel, textposition='bottom center'))

    data = trace
    if display_mode_value == 'overlap':
        figure = {'data': data,
        'layout': go.Layout(colorway=["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400'], # '#FFF400', '#FF0056'
        height=600,title=f" The temperature monitor",
        xaxis={"title":"Date",
                   'rangeselector': {'buttons': list([{'count': 1, 'label': 'last 1 hour', 'step': 'hour', 'stepmode': 'backward'},
                                                      {'count': 6, 'label': 'last 6 hour', 'step': 'hour', 'stepmode': 'backward'},
                                                      {'step': 'all'}])},
                   'rangeslider': {'visible': True}, 'type': 'date'},yaxis={"title":"Temperature"})}
        
        return  dcc.Graph(figure=figure, id='temperature-graph') 

    elif display_mode_value == 'separate':
        print('separate')
        graph_group = []
        color = ["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400']
        for tra, chan, col in zip(trace, selected_dropdown_value, color):
            print(type(tra))
            t = [tra]
            figure = {'data': t,
                     'layout': go.Layout(colorway=[col],
                     height=400,title=f" The temperature of {0}".format(chan),
                     xaxis={"title":"Date",
                    'rangeselector': {'buttons': list([{'count': 1, 'label': 'last 1 hour', 'step': 'hour', 'stepmode': 'backward'},
                                                      {'count': 6, 'label': 'last 6 hour', 'step': 'hour', 'stepmode': 'backward'},
                                                      {'step': 'all'}])},
                   'rangeslider': {'visible': False}, 'type': 'date'},yaxis={"title":"Temperature"})}
            graph_group.append(dcc.Graph(figure=figure, id='temperature_{0}'.format(chan)))
        

        return graph_group
    else:
        print('The creation of graph figure fails')
    

if __name__ == '__main__':
    app.run_server(debug=True, host='localhost')