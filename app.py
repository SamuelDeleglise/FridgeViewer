# In[]:
# Import required libraries
import os

import pandas as pd
from flask import Flask
from flask_cors import CORS
import dash 
from dash import no_update
from dash.dependencies import Input, Output, State


# need to update the latest version
#############################################
import dash_core_components as dcc
import dash_html_components as html
from datetime import timedelta, date, time, datetime
import plotly.graph_objs as go
from plotly import tools
import numpy as np
import sys

from data import *

app = dash.Dash(__name__)

#https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css
#https://codepen.io/chriddyp/pen/bWLwgP.css
app.css.append_css({'external_url': 'https://rayonde.github.io/external_css/fridge.css'})  


server = app.server
CORS(server)
#######################################################
# from flask_caching import Cache
# cache = Cache(app.server, config={
#     # try 'filesystem' if you don't want to setup redis
#     'CACHE_TYPE': 'redis',
#     'CACHE_REDIS_URL': os.environ.get('REDIS_URL', '')
# })
# app.config.suppress_callback_exceptions = True

# # Time-based expiry is helpful if you want to update your data (clear your cache) every hour or every day.
# timeout = 60 * 60 # seconds
#######################################################


years_auto = ['2019']
experiments_auto = ['DummyFridge']
min_date = datetime(2019, 4, 13)
max_date = datetime.today()
initial_month = datetime(2019, 4, 13)
initial_end_date = datetime(2019, 4, 14)
initial_start_date = datetime(2019, 4, 13)
path_data_auto = r'LOGS\DummyFridge\data'
#path_lab = r'LOGS'
#path_lab = r'Z:\ManipMembranes'
path_lab = r'Z:\ManipMembranes'

color_list = ["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056']


def create_cache_div(name, info):
    return dcc.Store(id='{0}-log-storage'.format(name), storage_type='memory', data = info)


# Create app layout
app.layout = html.Div([ 
    
    # Live mode or not according to end_date
    # Real time control
    dcc.Interval(
        id='interval-log-update',
        interval=10*1000, # in milliseconds
        n_intervals=0
    ),
    dcc.Interval(
        id='interval-info-update',
        interval=1*1000*60*60*24, # in milliseconds
        n_intervals=0
    ),

    # Hidden Div Storing JSON-serialized dataframe of run log
    html.Div([
        html.Div(id='before-log-storage', style={'display': 'none'}),
        html.Div(id='today-log-storage', style={'display': 'none'}),
        
        dcc.Store(id='num-before-storage', storage_type='memory'),
        dcc.Store(id='num-today-storage', storage_type='memory'),
        
        dcc.Store(id='experiments-storage',storage_type='session'),
        dcc.Store(id='years-storage',storage_type='session'),
        dcc.Store(id='channels-storage',storage_type='session'),
    ], id = 'cache'
    ),
    
    html.Div(
        [
            html.H1(
                'Fridge Viewer',
                className='eight columns',
            ),
            html.Img(
                src="https://rayonde.github.io/external_image/Logo_LKB.png",
                
                style={ 'height': '70px',
                'float': 'right',
                'position': 'relative',
                },
            ),
        ], className='row' , style={'margin-top': 5, 'margin-bottom': 5,}
    ),
    
    html.Div(
        [
        html.Div([
            html.Div([
                html.P('Experiment:',style={}),
            ]  ,style={}
            ),
            html.Div([
                dcc.Dropdown( id ='experiment',
                #options=[{'label': i, 'value': i} for i in experiments_auto],
                multi=False,
                #value= experiments_auto[0],
                ),
            ], style={}
            ), 
        ], id='experiment-framework',className='six columns' 
        ),
    
        html.Div([
            html.Div([
                html.P('Year:'),
            ],style={}
            ), 
            html.Div([
                dcc.Dropdown(id='year',
                #options=[{'label': i, 'value': i} for i in years_auto],
                multi=False,
                #value= years_auto[-1],
                ),
            ],style={}
            ), 

        ], id='years-framework', className='six columns'
        )
    ],className='row' , style={'margin-top': 5, 'margin-bottom': 5,}
    ),

    html.Div([
        
        html.Div([
            html.P('Select the signal channel'),
            # head style
        ], style={'margin-left': '0px','margin-top': '0px'}
        ),

        html.Div([    
            # Channel selection dropdown
            dcc.Dropdown(id='channels_dropdown',
                    multi=True,
            )
            # channel selection style
        ]
        ),
    ],className='row' , style={'margin-top': 5, 'margin-bottom': 5,}
    ),

    html.Div([
        html.Div([
            html.Div([
                dcc.Graph(id='temperature-graph')
            ],style={}
            )
        ],id='graph_framework', className ='eight columns',style={'display': 'inline-block'}),

        html.Div([
            html.Div([

                html.Div([
                    html.P("Live Data:", style={'font-weight': 'bold', 'margin-bottom': '10px'}),
                    
                    html.Div(id="div-data-display")

                ],style={'width': '100%', 'margin-bottom': '20px' }
                ),

                html.Div([
                    html.Button('Autoscale', 
                                    id='autoscale', 
                                    n_clicks_timestamp=0,
                                    style= {'width': '100%'})
                ], style={'width': '100%', 'margin-bottom': '20px' }
                ),

                html.Div([
                    html.P("Scale:", style={'font-weight': 'bold', 'margin-bottom': '10px'}),

                    dcc.DatePickerRange(id='date_range',
                        end_date = initial_end_date,
                        start_date = initial_start_date,
                        min_date_allowed=min_date,
                        max_date_allowed=max_date,
                        initial_visible_month=initial_month,
                    ),
                ],id='range_framework',style={'width': '100%', 'margin-bottom': '20px'}
                ),
                


                html.Div([
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
                ),
                
                html.Div([
                    html.P("Update Speed:", style={'font-weight': 'bold', 'margin-bottom': '10px'}),

                    html.Div(id='div-interval-control', children=[
                        dcc.Dropdown(id='dropdown-interval-control',
                            options=[
                                {'label': 'No Updates', 'value': 'no'},
                                {'label': 'Slow Updates', 'value': 'slow'},
                                {'label': 'Regular Updates', 'value': 'regular'},
                                {'label': 'Fast Updates', 'value': 'fast'}
                            ],
                            value='no',
                            style= {'width': '100%'},
                            clearable=False,
                            searchable=False
                        )
                    ]),
                ], style={'width': '100%', 'margin-bottom': '20px' }
                ),

                html.Div([
                    html.P("Number of data points:", style={'font-weight': 'bold', 'margin-bottom': '10px'}),
                    
                    html.Div(id="div-num-display")

                ],style={'width': '100%', 'margin-bottom': '20px' }
                ),
                
            ],style={       'height':'100%', 
                            'padding': 15,  
                            'borderRadius': 5, 
                            'border': 'thin lightgrey solid'})
        ],id='select_framework', className ='four columns', style={
                            'height':'100%', 
                            'display': 'inline-block',
                            'float': 'right',}
        )
    ],className='row', style={'margin-top': 5, 'margin-bottom': 5,}
    ),
        
],id ='page', className='ten columns offset-by-one'
)


########################################################


# Get the experiment list automatically every 24h
@app.callback([Output('experiment', 'options'),
               Output('experiment', 'value'),
              Output('experiments-storage','data')],
              [Input('interval-info-update', 'n_intervals')],
              [State('experiments-storage','data')])
def update_experiments(n_intervals, data):
    if n_intervals is 0:
        a = {}
        try:
            experiment_update = get_folder_names(all_folder_paths(path_lab))
        except FileNotFoundError as error:
            print(error)
            print('Cannot get the experiment list')
            return no_update, no_update, no_update
        else:
            data = data or {}
            a['experiments'] = experiment_update
            return [{'label': i, 'value': i} for i in experiment_update], experiment_update[0], a
    return no_update, no_update, no_update

# Get year list automatically
@app.callback([Output('year', 'options'),
              Output('year', 'value'),
               Output('years-storage','data')],
              [Input('experiment', 'value')],
              [State('years-storage','data')])
def update_years(exp, data):

    if exp is not None: 
        years_update = get_folder_names(all_folder_paths(path_lab + '\\' + exp + r'\data'))
        data = data or {}
        data['years'] = years_update
        return [{'label': i, 'value': i} for i in years_update], years_update[-1], data
    else: 
        return no_update, no_update, no_update

# Get effective channels list
# @app.callback([Output('channels_dropdown', 'options'),
#                Output('channels_dropdown', 'value'),
#               Output('channels-storage','data')],
#               [Input('experiment', 'value'),
#               Input('year', 'value')],
#               [State('channels-storage','data')])
# def update_channels(exp, year, data):
#     data_path = []
#     data_path_chan = []
#     try:
#         path = path_lab + '\\' + exp + r'\data' + '\\' + year
#         dates = all_folder_paths(path)
#         data_path = all_file_paths(dates[0], '.log')
#         data_path_chan = all_file_paths(dates[0], '.chan')

#         data_path = data_path + data_path_chan
#         channels_update = get_channels(data_path)
        
#         data = data or {}
#         data['channels'] = channels_update
#         return [{'label': i, 'value': i} for i in channels_update], channels_update[0], data

#     except FileNotFoundError as error:
#         print(error)
#         print('Cannot get the channel list')
#         return no_update, no_update, no_update

@app.callback([Output('channels_dropdown', 'options'),
               Output('channels_dropdown', 'value'),
              Output('channels-storage','data')],
              [Input('experiment', 'value'),
              Input('year', 'value'),
              Input('date_range', 'start_date'),
              Input('date_range', 'end_date')],
              [State('channels-storage','data')])
def update_channels(exp, year, start_date, end_date, data):
    if exp is not None and year is not None: 
        path = path_lab + '\\' + exp + r'\data' + '\\' + year
        channels_update = set()
       
        # get the all possible channels in the interval
        try:
            end_date = datetime.strptime(end_date,r'%Y-%m-%d')
            start_date = datetime.strptime(start_date, r'%Y-%m-%d')
            print(end_date)
            print(start_date)
        except TypeError as error:      
            print(error)
            print("Start day and end day have wrong filetype.")
        
        date_list = datelist(start_date, end_date) # timedate type
        
        # search all channels in the date interval
        for date in date_list: 
            single_date_str = date.strftime(r'%y-%m-%d')
            
            print(single_date_str)
            
            try:
                path_log = all_file_paths(path + '\\'+ single_date_str, '.log')
                log = get_channels(path_log)
                channels_update.update(set(log))
            except:
                print('No log files')
            try:
                path_chan = all_file_paths(path + '\\'+ single_date_str, '.chan')
                chan = get_channels(path_chan)
                channels_update.update(set(chan))
            except:
                print('No chan files')
    
        channels_update = list(channels_update)
        data = data or {}
        data['channels'] = channels_update
        if channels_update:
            return [{'label': i, 'value': i} for i in channels_update],channels_update[0], data
        else:
            return no_update, no_update, no_update
    else:
        return no_update, no_update, no_update

# Get effective date range 
@app.callback([Output('date_range', 'min_date_allowed'),
                Output('date_range', 'max_date_allowed'),
                Output('date_range', 'initial_visible_month'),
                Output('date_range', 'start_date'),
                Output('date_range', 'end_date'),],
               [Input('experiment', 'value'),
               Input('year', 'value')])
def update_date_range(exp, year):

    if exp is not None and year is not None: 
        path = path_lab + '\\' + exp + r'\data' + '\\' + year
        dates = all_folder_paths(path)
        min_date = datetime.strptime(path_leaf(dates[0]), r'%y-%m-%d')
        max_date = datetime.strptime(path_leaf(dates[-1]), r'%y-%m-%d')

        month = max_date
        start_date = max_date 

        return min_date, max_date, month, start_date, max_date
    else:
        return no_update, no_update, no_update, no_update, no_update

# Callback the update mode 
@app.callback(Output('dropdown-interval-control', 'value'),
                [Input('date_range', 'start_date'),
                 Input('date_range', 'end_date')])
def storage_mode(start_date, end_date):

    try:
        end_date = datetime.strptime(end_date,r'%Y-%m-%d')
        start_date = datetime.strptime(start_date, r'%Y-%m-%d')
    except TypeError as error:      

        print("Start day and end day have wrong filetype.")

    # Select record mode
    if end_date.date() < datetime.today().date():
        print('The update is needless for the data selected.' )
        return 'no'
    else: 
        return 'regular' 

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
  

# Dash can't have the same Input and Output
# Save the data as json file in cache
@app.callback([Output('before-log-storage', 'children'),
               Output('num-before-storage','data'),],
                  [Input('date_range', 'start_date'),
                  Input('date_range', 'end_date'),
                  Input('experiment', 'value'),
                  Input('channels-storage', 'data'),],
                 [
                  State('before-log-storage', 'children'),
                  State('num-before-storage','data'),
                  ])
# @cache.memoize(timeout=timeout)  # in seconds
def get_before_log(start_date, end_date, exp, data_channel, before, num_before):

    if exp is not None:
    
        # get the path from the selection of experiment
        path = path_lab +'\\' + exp +'\\data'
        
        # selected date range
        try:
            end_date = datetime.strptime(end_date,r'%Y-%m-%d')
            start_date = datetime.strptime(start_date, r'%Y-%m-%d')
            date_list = datelist(start_date, end_date)
        except TypeError as error:      
            print(error)
            print("start_date and end_date have wrong filetype.") 
        
        # the first time, the list of date_list_old is initialized as an empty list

        if before is not None:
            if exp != before['exp_before']:
                before.clear()
            date_list_old = list(before.keys())
            
            if 'exp_before' in date_list_old:
                            date_list_old.remove('exp_before')
            if 'exp_today' in date_list_old:
                            date_list_old.remove('exp_today')
            
            if  date_list_old:
                date_list_old.sort()
            
                start_date_old = datetime.strptime(date_list_old[0], r'%Y-%m-%d')
                end_date_old = datetime.strptime(date_list_old[-1],r'%Y-%m-%d')
                date_list_old = datelist(start_date_old, end_date_old)        
        else:
            date_list_old = [] 
        

        # the different dates between two lists
        date_update = [i.date() for i in date_list if i not in date_list_old]
        
        # remove today, it will update in another callback
        if datetime.today().date() in date_update:
            date_update.remove(datetime.today().date())


        # get the channel set from the channel storage
        if  data_channel is not None:
            
            cache_dic = {}
            num_total = 0
        
            channel_set = data_channel['channels'] 
            for single_date in date_update:

                # extract one day's data 
                try:
                    df = get_1day_data_str(single_date, channel_set, path)
                    single_date_str = single_date.strftime(r'%Y-%m-%d')
                except Exception as error: 
                    print(error)
                    print("Fail to read the data in disk.")
                else: 
                    print('Succeed to read the before data in disk.')
                
                try:
                    num_df = len(df)
                    json_data = df.to_json(orient='split')
                    # create individual store component according to the date
                    cache_dic[single_date_str] = json_data
                    
                except Exception as error: 
                    print(error)
                    print("Fail to transfer the data to json type.")
                else: 
                    print('Succeed to transfer the data to json type.')
                    num_total = num_total + num_df
            
            
            if num_before is not None:
                num_total = num_before['num_before'] + num_total
            
            if before is not None:
                before.update(cache_dic)  
            else:
                before = cache_dic
            
            before['exp_before'] = exp
            return before, {'num_before': num_total}

        else:
            print("The channel set is empty.")
            return no_update, no_update

    else:         
        return no_update, no_update

# Update today's json data 
@app.callback([Output('today-log-storage', 'children'),
               Output('num-today-storage','data')],
                  [ Input('dropdown-interval-control', 'value'),
                    Input('interval-log-update', 'n_intervals'),
                   Input('experiment', 'value'),
                  Input('channels-storage', 'data'),
                  Input('date_range', 'start_date'),
                  Input('date_range', 'end_date')],
                  [State('today-log-storage', 'children')])
def get_today_log(speed_value, n_intervals, exp, channels, start_date, end_date, data):

    if exp is not None:   
        if channels is not None:
            
            if data is not None:
                if exp != data['exp_today']:
                    data.clear()

            # get the path from the selection of experiment
            path = path_lab +'\\' + exp +'\\data'
            
            try:
                end_date = datetime.strptime(end_date, r'%Y-%m-%d')
                start_date = datetime.strptime(start_date, r'%Y-%m-%d')
            except TypeError as error:      
                print(error)
                print("start_date and end_date have wrong filetype.")

            # Select live mode
            if end_date.date() == datetime.today().date(): 
                
                today_str = datetime.today().strftime(r'%Y-%m-%d')

                num = 0
                
                # get the channel set from the channel storage
                channel_set = channels['channels']           
                
                try:
                    df = get_1day_data_str(datetime.today(),channel_set, path)

                except FileNotFoundError as error:      
                    print(error)
                    print("There is no data is placed in the today\'s directory.")
                
                num =len(df) 
                json_data = df.to_json(orient='split')
                
                if data is not None:
                    data[today_str] = json_data
                else:
                    data = {}
                    data[today_str] = json_data
                
                data['exp_today'] = exp
                return data, {'num_today': num}
            else: 
                return no_update, no_update
        else: 
            return no_update, no_update
    else:
        return no_update, no_update


# Display the data size
# The figure extend today's data instead of a enormous dataset
@app.callback(Output('div-num-display', 'children'),
              [Input('num-before-storage', 'data'),
              Input('num-today-storage', 'data'),
              Input('interval-log-update', 'n_intervals')])
def update_num_display_and_time(num_before, num_today, n_intervals):  

    if num_before is None:
        num_1 = 0
    else: 
        num_1 = num_before['num_before']
    if num_today is None:
        num_2 = 0
    else: 
        num_2 = num_today['num_today']

    total_num = num_1 + num_2
    return html.H2('{0}'.format(total_num), style={ 'margin-top': '3px'})

# # Callback the graph
# @app.callback(Output('temperature-graph', 'figure'),
#             [Input('before-log-storage', 'children'),
#             Input('channels_dropdown', 'value'),
#             Input('display_mode','value'),
#             Input('autoscale','n_clicks_timestamp')],)
# def update_graph(before, selected_dropdown_value, display_mode_value, click):
#     layout_set = {'colorway': color_list,
#                        'title':"The sensor channel monitor",
#                        'height':600,
#                         'xaxis':{"title":"Date",
#                             'rangeselector': {'buttons': list([
#                                 {'count': 10, 'label': '10m', 'step': 'minute', 'stepmode': 'backward'},
#                                 {'count': 1, 'label': '1h', 'step': 'hour', 'stepmode': 'backward'},
#                                 {'count': 6, 'label': '6h', 'step': 'hour', 'stepmode': 'backward'},
#                                 {'step': 'all'}])},
#                             'rangeslider': {'visible': True,'yaxis' :{"rangemode": "auto"} }, 'type': 'date'},
#                         'margin':{'l':60, 'b': 40, 't': 80, 'r': 10},
#                         'yaxis' : {"title":"Value",
#                                 },
#                         'uirevision': click,  
#             }

#     df = pd.DataFrame()
#     if before is not None:
#         for key, value in before.items():
#             before_df = pd.read_json(value, orient='split')
#             df = pd.concat([df, before_df], axis=0, sort=True)
    
#         # create empty trace     
#         trace = []
#         # to keep same format for single channel or mutiple channels
#         if not isinstance(selected_dropdown_value, (list,)):
#             selected_dropdown_value = [selected_dropdown_value]
        
#         for channel in selected_dropdown_value:
#             key_time = 'Time_'+ channel
#             key = channel
#             if key in df.keys() and key_time in df.keys():
#                 temp_df = pd.concat([df[key_time], df[key]], axis=1)
#                 temp_df[key_time] = pd.to_datetime(temp_df[key_time], format=r'%Y%m%d %H:%M:%S')
                
#                 # eliminate the NaN elements
#                 temp_df.dropna()
#                 trace.append(go.Scatter(x=temp_df[key_time], y=temp_df[key],mode='lines',
#                 opacity=0.7,name=channel, textposition='bottom center'))
#             else: 
#                 print('There is no trace required')

#         data = trace
#         # overlap display
#         if display_mode_value == 'overlap':
#             figure = {'data': data, 'layout': layout_set}
        
#         # separate dislay 
#         elif display_mode_value == 'separate':
#             num =  len(selected_dropdown_value)
#             figure = tools.make_subplots(rows=num, cols=1)
            
#             for index, (tra, chan) in enumerate(zip(trace, selected_dropdown_value)):     
#                 figure.append_trace(tra, index+1, 1)
#                 figure['layout']['xaxis{}'.format(index+1)].update(title='The channel of {0}'.format(chan)) 
            
#             figure['layout'].update(height=500*num)  

#         return figure       
#     else:
#         return no_update 

@app.callback([Output('temperature-graph', 'figure'),
               Output('div-data-display', 'children')],
            [Input('before-log-storage', 'children'),
            Input('date_range', 'end_date'),
            Input('date_range', 'start_date'),
            Input('today-log-storage', 'children'),
            Input('channels_dropdown', 'value'),
            Input('display_mode','value'),
            Input('autoscale','n_clicks_timestamp')],
            [State('temperature-graph', 'figure'),])
def update_graph(before_data, end_date, start_date, today_data, selected_dropdown_value, display_mode_value, click, figure):   

    layout_set = {'colorway': color_list,
                       'title':"The sensor channel monitor",
                       'height':600,
                        'xaxis':{"title":"Date",
                            'rangeselector': {'buttons': list([
                                {'count': 10, 'label': '10m', 'step': 'minute', 'stepmode': 'backward'},
                                {'count': 1, 'label': '1h', 'step': 'hour', 'stepmode': 'backward'},
                                {'count': 6, 'label': '6h', 'step': 'hour', 'stepmode': 'backward'},
                                {'step': 'all'}])},
                            'rangeslider': {'visible': True,'yaxis' :{"rangemode": "auto"} }, 'type': 'date'},
                        'margin':{'l':60, 'b': 40, 't': 80, 'r': 10},
                        'yaxis' : {"title":"Value",
                                },
                        'uirevision': click,  
            }
    start_date = datetime.strptime(start_date, r'%Y-%m-%d')
    end_date = datetime.strptime(end_date, r'%Y-%m-%d')
    date_list = datelist(start_date, end_date)

    
    if end_date.date() == datetime.today().date(): 
        # to keep same format for single channel or mutiple channels
        if not isinstance(selected_dropdown_value, (list,)):
            selected_dropdown_value = [selected_dropdown_value]
        
        if today_data is not None:
            trace = []
            dis = []
            data_df = pd.DataFrame()
            
            if before_data is not None:
                before_data.update(today_data)
            else:
                before_data = today_data
            
            date_log_list = list(before_data.keys())
            if 'exp_before' in date_log_list:
                date_log_list.remove('exp_before')
            if 'exp_today' in date_log_list:
                date_log_list.remove('exp_today')
            
            data_df = pd.DataFrame()
            for date in date_list:
                date_str = date.strftime(r'%Y-%m-%d')
                
                if date_str in date_log_list:
                    temp_df = pd.DataFrame()
                    temp_df = pd.read_json(before_data[date_str], orient='split')
                    data_df = pd.concat([data_df, temp_df], axis=0, sort=True) 
            
            if selected_dropdown_value is not None or selected_dropdown_value:
                for channel in selected_dropdown_value:
                    channel_time = 'Time_'+ channel
                    
                    if data_df[channel_time].iloc[0] == str:                 
                        data_df[channel_time] = pd.to_datetime(data_df[channel_time], format=r'%Y%m%d %H:%M:%S')
                    
                    trace.append(go.Scatter(x=data_df[channel_time].dropna(), y=data_df[channel].dropna(),mode='lines',
                        opacity=0.7,name=channel, textposition='bottom center'))
                        
                    dis.append(html.H6('{0} : {1}'.format(channel, data_df[channel].iloc[-1]), style={ 'margin-top': '3px'}))
                    

                # overlap display
                if display_mode_value == 'overlap':
                    figure = {'data': trace, 'layout': layout_set}
            
                # separate dislay 
                elif display_mode_value == 'separate':
                    num =  len(selected_dropdown_value)
                    
                    figure = tools.make_subplots(rows=num, cols=1)
                    for index, (tra, chan) in enumerate(zip(trace, selected_dropdown_value)):     
                        figure.append_trace(tra, index+1, 1)
                        figure['layout']['xaxis{}'.format(index+1)].update(title='The channel of {0}'.format(chan)) 
            
                    figure['layout'].update(height=500*num) 
                
                return figure, dis
            else: no_update, no_update
        else:
            return no_update, no_update
    else:
        
        # to keep same format for single channel or mutiple channels
        if not isinstance(selected_dropdown_value, (list,)):
            selected_dropdown_value = [selected_dropdown_value]
        
        if before_data is not None:
            trace = []
            dis = []
            
            date_log_list = list(before_data.keys())
            if 'exp_before' in date_log_list:
                date_log_list.remove('exp_before')
            if 'exp_today' in date_log_list:
                date_log_list.remove('exp_today')
                   
            data_df = pd.DataFrame()
            for date in date_list:
                date_str = date.strftime(r'%Y-%m-%d')
                
                if date_str in date_log_list:
                    temp_df = pd.DataFrame()
                    temp_df = pd.read_json(before_data[date_str], orient='split')
                    data_df = pd.concat([data_df, temp_df], axis=0, sort=True) 

            if selected_dropdown_value is not None or selected_dropdown_value:
                for channel in selected_dropdown_value:
                    channel_time = 'Time_'+ channel
                    if data_df[channel_time].iloc[0] == str:                 
                        data_df[channel_time] = pd.to_datetime(data_df[channel_time], format=r'%Y%m%d %H:%M:%S')

                    trace.append(go.Scatter(x=data_df[channel_time].dropna(), y=data_df[channel].dropna(),mode='lines',
                        opacity=0.7,name=channel, textposition='bottom center'))
                        
                    dis.append(html.H6('{0} : {1}'.format(channel, data_df[channel].iloc[-1]), style={ 'margin-top': '3px'}))
                    

                # overlap display
                if display_mode_value == 'overlap':
                    figure = {'data': trace, 'layout': layout_set}
            
                # separate dislay 
                elif display_mode_value == 'separate':
                    num =  len(selected_dropdown_value)
                    
                    figure = tools.make_subplots(rows=num, cols=1)
                    for index, (tra, chan) in enumerate(zip(trace, selected_dropdown_value)):     
                        figure.append_trace(tra, index+1, 1)
                        figure['layout']['xaxis{}'.format(index+1)].update(title='The channel of {0}'.format(chan)) 
            
                    figure['layout'].update(height=500*num) 
            
                return figure, no_update
            else: 
                return no_update, no_update
        else:
            return no_update, no_update
        
        
        
        
        
        
        
        
        
        
        
        
        
        # df = pd.DataFrame()
        # if before_data is not None:
        #     for key, value in before_data.items():
        #         before_df = pd.read_json(value, orient='split')
        #         df = pd.concat([df, before_df], axis=0, sort=True)
        
        #     # create empty trace     
        #     trace = []
        #     # to keep same format for single channel or mutiple channels
        #     if not isinstance(selected_dropdown_value, (list,)):
        #         selected_dropdown_value = [selected_dropdown_value]
            
        #     for channel in selected_dropdown_value:
        #         key_time = 'Time_'+ channel
        #         key = channel
        #         if key in df.keys() and key_time in df.keys():
        #             temp_df = pd.concat([df[key_time], df[key]], axis=1)
        #             temp_df[key_time] = pd.to_datetime(temp_df[key_time], format=r'%Y%m%d %H:%M:%S')
                    
        #             # eliminate the NaN elements
        #             temp_df.dropna()
        #             trace.append(go.Scatter(x=temp_df[key_time], y=temp_df[key],mode='lines',
        #             opacity=0.7,name=channel, textposition='bottom center'))
        #         else: 
        #             print('There is no trace required')

        #     data = trace
        #     # overlap display
        #     if display_mode_value == 'overlap':
        #         figure = {'data': data, 'layout': layout_set}
            
        #     # separate dislay 
        #     elif display_mode_value == 'separate':
        #         num =  len(selected_dropdown_value)
        #         figure = tools.make_subplots(rows=num, cols=1)
                
        #         for index, (tra, chan) in enumerate(zip(trace, selected_dropdown_value)):     
        #             figure.append_trace(tra, index+1, 1)
        #             figure['layout']['xaxis{}'.format(index+1)].update(title='The channel of {0}'.format(chan)) 
                
        #         figure['layout'].update(height=500*num)  

        #     return figure, dis       
        # else:
        #     return no_update, no_update

       

    # # live mode
    # if today_data is not None:
    #     end_date = datetime.strptime(end_date, r'%Y-%m-%d')
    #     if end_date.date() == datetime.today().date(): 
    #         if selected_dropdown_value is not None:
                
    #             trace = []
    #             dis = []
    #             data = pd.DataFrame()
    #             for key, value in today_data.items():
    #                 today_data = pd.read_json(value, orient='split')
    #                 data = pd.concat([data, today_data], axis=0, sort=True)

    #             if not isinstance(selected_dropdown_value, (list,)):
    #                 selected_dropdown_value = [selected_dropdown_value]
                
    #             for channel in selected_dropdown_value:
    #                 channel_time = 'Time_'+channel

    #                 data[channel_time] = pd.to_datetime(data[channel_time], format=r'%Y%m%d %H:%M:%S')

    #                 trace.append(go.Scatter(x=data[channel_time], y=data[channel],mode='lines',
    #                 opacity=0.7,name=channel, textposition='bottom center'))

    #                 dis.append(html.H6('{0} : {1}'.format(channel, data[channel].iloc[-1]), style={ 'margin-top': '3px'}))
        
    #             if len(trace) is not 0:
                    
    #                 # overlap display
    #                 if display_mode_value == 'overlap':
    #                     return trace, dis
    #                 # separate dislay 
    #                 elif display_mode_value == 'separate': 
    #                     return trace, dis
    #             else:
    #                 return no_update, no_update
    #         else: 
    #             return no_update, no_update
    #     else: 
    #         return no_update, no_update
    # else: 
    #     return no_update, no_update




# @app.callback([Output('temperature-graph', 'extendData'),
#                Output('div-data-display', 'children'),
#                Output('num-today-storage', 'data'),],
#             [Input('experiment', 'value'),
#             Input('channels-storage', 'data'),
#             Input('date_range', 'start_date'),
#             Input('date_range', 'end_date'),
            
#             Input('channels_dropdown', 'value'),
#             Input('display_mode','value'),
#             Input('autoscale','n_clicks_timestamp'),
#             Input('interval-log-update', 'n_intervals')],
#             [State('temperature-graph', 'figure'),])
# def update_graph_extend(exp, channels, start_date, end_date, selected_dropdown_value, display_mode_value, click,n_intervals, figure):
#     if exp is not None:
#         # Get the path from the selection of experiment
#         path = path_lab +'\\' + exp +'\\data'    

#         # Get the selected date range
#         try:
#             end_date = datetime.strptime(end_date, r'%Y-%m-%d')
#             start_date = datetime.strptime(start_date, r'%Y-%m-%d')
#         except TypeError as error:      
#             print(error)
#             print("start_date and end_date have wrong filetype.")

#         # Select live mode
#         if end_date.date() == datetime.today().date(): 
             
#             # Get the channel set from the channel storage
#             if channels is not None:
                
#                 channel_set = channels['channels']

#                 # Get today's data          
#                 try:
#                     df_today = get_1day_data_str(datetime.today(), channel_set, path)
#                 except FileNotFoundError as error:      
#                     print(error)
#                     print("There is no data is placed in the today\'s directory.")
#                 else: 
#                     num =len(df_today)
#                     trace = []
#                     dis = []

#                     print(selected_dropdown_value)
                    
#                     for channel in selected_dropdown_value:
#                         key_time = 'Time_'+channel
#                         key = channel
#                         print('1')
#                         try:
#                             df_today[key_time] = pd.to_datetime(df_today[key_time], format=r'%Y%m%d %H:%M:%S')
#                             print('succeed')
#                         except:
#                             print('erooooooooor')
#                         print(df_today[key_time])
#                         print(df_today.iloc[0][key_time])

#                         trace.append(go.Scatter(x=df_today[key_time], y=df_today[key],mode='lines',
#                         opacity=0.7,name=channel, textposition='bottom center'))
#                         print('2')

#                         try:
#                             dis.append(html.H2('{0} : {1}'.format(channel, df_today[key].iloc[-1]), style={ 'margin-top': '3px'}))
                    
#                         except:
#                             print('live display fails')
                
#                 print(num)
#                 if len(trace) is not 0:
#                     # overlap display
#                     if display_mode_value == 'overlap':

#                         return trace, dis, {'num_today': num}
#                     # separate dislay 
#                     elif display_mode_value == 'separate': 

#                         return trace, dis, {'num_today': num}
#                 else:

#                     return no_update, no_update, no_update    
#             else: 
#                 return no_update, no_update, no_update
#         else:
#             return no_update, no_update, no_update
#     else:
#         return no_update, no_update, no_update
        



# Main
if __name__ == '__main__':
    if len(sys.argv)>=2:
        path_lab = sys.argv[1]
    else:
        path_lab = None
    print(path_lab)
    app.server.run(debug=False, threaded=True)

# In Jupyter, debug = False 

#%%
