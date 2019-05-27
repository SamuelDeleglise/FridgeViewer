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

from data import*

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


channels_auto = ['CH1 T', 'CH2 T']
years_auto = ['2019']
experiments_auto = ['DummyFridge']
min_date = datetime(2019, 4, 13)
max_date = datetime.today()
initial_month = datetime(2019, 4, 13)
initial_end_date = datetime(2019, 4, 14)
initial_start_date = datetime(2019, 4, 13)
path_data_auto = r'LOGS\DummyFridge\data'
path_lab = r'LOGS'

color_list = ["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056']

def create_cache_div(name, info):
    return dcc.Store(id='{0}-log-storage'.format(name), storage_type='memory', data = info)


# Create app layout
app.layout = html.Div([ 
    
    # Live mode or not according to end_date
    # Real time control
    dcc.Interval(
        id='interval-log-update',
        interval=1*1000, # in milliseconds
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
        html.Div(id='start-date-storage', style={'display': 'none'}),
        html.Div(id='end-date-storage', style={'display': 'none'}),
        
        dcc.Store(id='experiments-storage',storage_type='session'),
        dcc.Store(id='years-storage',storage_type='session'),
        dcc.Store(id='channels-storage',storage_type='session')
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
        ],id = 'header', className='row' , style={'margin-top': 5, 'margin-bottom': 5,}
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
                options=[{'label': i, 'value': i} for i in experiments_auto],
                multi=False,
                value= experiments_auto[0],
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
                options=[{'label': i, 'value': i} for i in years_auto],
                multi=False,
                value= years_auto[-1],
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
                    options=[{'label': i, 'value': i} for i in channels_auto],
                    # defaut selections
                    value=channels_auto,
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
                    html.Button('Update Date range', 
                                    id='update_date', 
                                    n_clicks_timestamp=0,
                                    style= {'width': '100%'})
                ], style={'width': '100%', 'margin-bottom': '20px' }
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
                            value='regular',
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
# Get the experiment list automatically 
@app.callback([Output('experiment', 'options'),
               Output('experiment', 'value'),
              Output('experiments-storage','data')],
              [Input('interval-info-update', 'n_intervals')],
              [State('experiments-storage','data')])
def update_experiments(n_intervals, data):
    print('callback 1')
    a = {}
    try:
        experiment_update = get_folder_names(all_folder_paths(path_lab))
    except FileNotFoundError as error:
        print(error)
        print('Cannot get the experiment list')
        return no_update, no_update
    else:
        data = data or {}
        a['experiments'] = experiment_update
        return [{'label': i, 'value': i} for i in experiment_update], experiment_update[0], a


# Get year list automatically
@app.callback([Output('year', 'options'),
              Output('year', 'value'),
               Output('years-storage','data')],
              [Input('experiment', 'value')],
              [State('years-storage','data')])
def update_years(exp, data):
    print('callback 2')
    try:
        years_update = get_folder_names(all_folder_paths(path_lab + '\\' + exp + r'\data'))
        data = data or {}
        data['years'] = years_update
        return [{'label': i, 'value': i} for i in years_update], years_update[-1], data
    
    except FileNotFoundError as error:
        print(error)
        print('Cannot get the year list')
        return no_update, no_update, no_update

# Get effective channels list
@app.callback([Output('channels_dropdown', 'options'),
               Output('channels_dropdown', 'value'),
              Output('channels-storage','data')],
              [Input('experiment', 'value'),
              Input('year', 'value')],
              [State('channels-storage','data')])
def update_channels(exp, year, data):
    print('callback 3')
    try:
        path = path_lab + '\\' + exp + r'\data' + '\\' + year
        dates = all_folder_paths(path)
        data_path = all_file_paths(dates[0], '.log')
        channels_update = get_effect_channels(data_path)
        
        data = data or {}
        data['channels'] = channels_update
        return [{'label': i, 'value': i} for i in channels_update], channels_update[0], data

    except FileNotFoundError as error:
        print(error)
        print('Cannot get the channel list')
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
  
    print('callback 4')
    try:
        path = path_lab + '\\' + exp + r'\data' + '\\' + year
        dates = all_folder_paths(path)
        min_date = datetime.strptime(path_leaf(dates[0]), r'%y-%m-%d')
        max_date = datetime.strptime(path_leaf(dates[-1]), r'%y-%m-%d')

        month = max_date
        start_date = max_date 

        return min_date, max_date, month, start_date,  max_date

    except FileNotFoundError as error:
        print(error)
        print('There is no data in this year.')
        return no_update, no_update, no_update, no_update
   
# Callback the update speed
@app.callback(Output('interval-log-update', 'interval'),
              [Input('dropdown-interval-control', 'value')])
def update_interval_log_update(interval_rate):
    print('callback 5')
    if interval_rate == 'fast':
        return 500

    elif interval_rate == 'regular':
        return 1000

    elif interval_rate == 'slow':
        return 5 * 1000

    # Refreshes every 24 hours
    elif interval_rate == 'no':
        return 24 * 60 * 60 * 1000

# Callback the update mode 
@app.callback(Output('dropdown-interval-control', 'value'),
                [Input('date_range', 'start_date'),
                 Input('date_range', 'end_date')])
def storage_mode(start_date, end_date):
    
    print('callback 6')
    try:
        end_date = datetime.strptime(end_date,r'%Y-%m-%d')
        start_date = datetime.strptime(start_date, r'%Y-%m-%d')
    except TypeError as error:      
        print(error)
        print("Start day and end day have wrong filetype.")

    # Select record mode
    if end_date.date() < datetime.today().date():
        print('The update is needless for the data selected.' )
        return 'no'
    else: 
        no_update    


# Dash can't have the same Input and Output
# Save the data as json file in cache

@app.callback([Output('before-log-storage', 'children'),
               Output('num-before-storage','data'),
               Output('start-date-storage', 'children'),
               Output('end-date-storage','children')],
                  [Input('date_range', 'start_date'),
                  Input('date_range', 'end_date'),
                  Input('experiment', 'value'),
                  Input('channels-storage', 'data'),],
                 [State('before-log-storage', 'children'),
                  State('num-before-storage','data'),
                  State('start-date-storage', 'children'),
                  State('end-date-storage','children')
                  ])
# @cache.memoize(timeout=timeout)  # in seconds
def get_before_log(start_date, end_date, exp, data_channel, before, num_before, start_date_old, end_date_old): 
    print('callback 7')
    # the first time, the list of date_list_old is initialized as an empty list
    if start_date_old == None and end_date_old == None:
        date_list_old = []
    else: 
        start_date_old = datetime.strptime(start_date_old['start_date_old'], r'%Y-%m-%d')
        end_date_old = datetime.strptime(end_date_old['end_date_old'],r'%Y-%m-%d')
        date_list_old = datelist(start_date_old, end_date_old)
    try:
        end_date = datetime.strptime(end_date,r'%Y-%m-%d')
        start_date = datetime.strptime(start_date, r'%Y-%m-%d')
    except TypeError as error:      
        print(error)
        print("start_date and end_date have wrong filetype.")
    # get the date list 
    date_list = datelist(start_date, end_date)
    
    # the different dates between two lists
    date_update = [i.date() for i in date_list if i not in date_list_old]
    
    # remove today, it will update in another callback
    if datetime.today().date() in date_update:
        date_update.remove(datetime.today().date())
    
    try:
        # get the path from the selection of experiment
        path = path_lab +'\\' + exp +'\\data'
        # get the channel set from the channel storage
        
        channel_set = data_channel['channels']  
         
    except Exception as error:      
        print(error)
        print("Please verify if the data is placed in the correct directory.")
        return no_update, no_update, no_update, no_update
    else:
        cache_dic = {}
        num_total = 0
        for single_date in date_update:
            print(single_date)
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

        return cache_dic, {'num_before': num_total}, {'start_date_old':start_date},  {'end_date_old':end_date}

# Update today's json data 
@app.callback([Output('today-log-storage', 'children'),
               Output('num-today-storage','data')],
                  [Input('interval-log-update', 'n_intervals'),
                   Input('experiment', 'value'),
                  Input('channels-storage', 'data'),
                  Input('date_range', 'start_date'),
                  Input('date_range', 'end_date')])
def get_today_log(n_intervals, exp, data_channel, start_date, end_date):
   
    print('callback 8')
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
        cache_dic = {}
        # get the path from the selection of experiment
        path = path_lab +'\\' + exp +'\\data'
        
        # get the channel set from the channel storage
        print(data_channel)
        channel_set = data_channel['channels']           
        try:
            df = get_1day_data_str(datetime.today(), channel_set, path)
        except FileNotFoundError as error:      
            print(error)
            print("There is no data is placed in the today's directory.")
        
        num =len(df) 
        json_data = df.to_json(orient='split')
        cache_dic[today_str].append(json_data)
        return cache_dic, {'num-today': num}
    else:
        return no_update, no_update
    


# Display the data size
# The figure extend today's data instead of a enormous dataset
@app.callback(Output('div-num-display', 'children'),
              [Input('num-before-storage', 'data'),Input('num-today-storage', 'data')])
def update_num_display_and_time(num_before, num_today):  
    print('callback 8')
    if num_before == None:
        num_1 = 0
    else: 
        num_1 = num_before['num_before']
    if num_today == None:
        num_2 = 0
    else: 
        num_2 = num_today['num_today']

    total_num = num_1 + num_2
    return html.H2('{0}'.format(total_num), style={ 'margin-top': '3px'})

@app.callback(Output('temperature-graph', 'figure'),
            [Input('before-log-storage', 'children'),
            Input('channels_dropdown', 'value'),
            Input('display_mode','value'),
            Input('autoscale','n_clicks_timestamp')],)
def update_graph(before, selected_dropdown_value, display_mode_value, click):
    layout_set = {'colorway': color_list,
                       'title':"The sensor channel monitor",
                       'height':600,
                        'xaxis':{"title":"Date",
                            'rangeselector': {'buttons': list([
                                {'count': 10, 'label': '10m', 'step': 'minute', 'stepmode': 'backward'},
                                {'count': 1, 'label': '1h', 'step': 'hour', 'stepmode': 'backward'},
                                {'count': 6, 'label': '6h', 'step': 'hour', 'stepmode': 'backward'},
                                {'step': 'all'}])},
                            'rangeslider': {'visible': True}, 'type': 'date'},
                        'margin':{'l':60, 'b': 40, 't': 80, 'r': 10},
                        'yaxis' : {"title":"Value"},
                        'uirevision': click,
                       
            }

    df = pd.DataFrame()
    if (before != None):        
        for key, value in before.items():
            before_df = pd.read_json(value, orient='split')
            df = pd.concat([df, before_df], axis=0)
        
            # create empty trace
        
        trace = []
        # to keep same format for single channel or mutiple channels
        if not isinstance(selected_dropdown_value, (list,)):
            selected_dropdown_value = [selected_dropdown_value]
        
        print(selected_dropdown_value)
        for channel in selected_dropdown_value:
            key_time = 'Time_'+ channel
            key = channel

            temp_df = pd.concat([df[key_time], df[key]], axis=1)
            temp_df[key_time] = pd.to_datetime(temp_df[key_time], format=r'%Y%m%d %H:%M:%S')

            trace.append(go.Scatter(x=temp_df[key_time], y=temp_df[key],mode='lines',
            opacity=0.7,name=channel, textposition='bottom center'))

        data = trace
        if len(trace) !=0:
            # overlap display
            if display_mode_value == 'overlap':
                print(len(data))
                figure = {'data': data, 'layout': layout_set}
            
            # separate dislay 
            elif display_mode_value == 'separate':
                num =  len(selected_dropdown_value)
                print(num)
                figure = tools.make_subplots(rows=num, cols=1)
                for index, (tra, chan) in enumerate(zip(trace, selected_dropdown_value)):   
                    print(index)    
                    figure.append_trace(tra, index+1, 1)
                    figure['layout']['xaxis{}'.format(index+1)].update(title='The channel of {0}'.format(chan)) 
                
                figure['layout'].update(height=500*num)         
                    
            return figure
        else:
            return no_update 
    else:
        return no_update


@app.callback(Output('temperature-graph', 'extendData'),
            [Input('today-log-storage', 'children'),
            Input('channels_dropdown', 'value'),
            Input('display_mode','value'),
            Input('autoscale','n_clicks_timestamp')],
            [State('temperature-graph', 'figure'),])
def update_graph_extend(today, selected_dropdown_value, display_mode_value, click, figure):
    # live mode
    if (today != None):
        df_today = pd.DataFrame()
        # only one item in today dictionary, just keep the format
        for key, value in today.items():
            today = pd.read_json(value, orient='split')
            df_today = pd.concat([df_today, today], axis=0)
        
        trace = []
        for channel in selected_dropdown_value:
            key_time = 'Time_'+channel
            key = channel

            temp_df = pd.concat([df_today[key_time], df_today[key]], axis=1)
            temp_df[key_time] = pd.to_datetime(temp_df[key_time], format=r'%Y%m%d %H:%M:%S')

            trace.append(go.Scatter(x=temp_df[key_time], y=temp_df[key],mode='lines',
            opacity=0.7,name=channel, textposition='bottom center'))
        
        if len(trace) !=0:
            # overlap display
            if display_mode_value == 'overlap':
                return trace
            # separate dislay 
            elif display_mode_value == 'separate': 
                return figure
        else:
            return no_update 
    else: 
        return no_update



# Main
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)

# In Jupyter, debug = False 

#%%
