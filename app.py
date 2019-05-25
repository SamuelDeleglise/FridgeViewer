# In[]:
# Import required libraries
import os
import pickle
import copy
import datetime as dt

import pandas as pd
from flask import Flask
from flask_cors import CORS
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
from datetime import timedelta, date, time, datetime
import plotly.graph_objs as go
from plotly import tools
import numpy as np

from data import*
# Multi-dropdown options

app = dash.Dash(__name__)

#https://codepen.io/chriddyp/pen/bWLwgP.css
app.css.append_css({'external_url': 'https://rayonde.github.io/external_css/fridge.css'})  
server = app.server
CORS(server)

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



# Create app layout
app.layout = html.Div(
    [   
        # # Hidden Div Storing JSON-serialized dataframe of run log
        html.Div(id='before-log-storage', style={'display': 'none'}),
        html.Div(id='today-log-storage', style={'display': 'none'}),
        html.Div(id='num-before-storage', style={'display': 'none'}),
        html.Div(id='num-today-storage', style={'display': 'none'}),
        
        
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
        ],className='row' , style={'margin-top': 5, 'margin-bottom': 5,}
        ),
        
        html.Div(
            [
            html.Div([
                html.P('Experiment:'),
                
                html.Div([
                    dcc.Dropdown( id ='experiment',
                    options=[{'label': i, 'value': i} for i in experiments_auto],
                    multi=False,
                    value= experiments_auto[0],
                     ),
                ]
                ), 
            ], id='experiment-framework',className='six columns'
            ),
        
            html.Div([
                html.P('Year:'), 
                html.Div([
                    dcc.Dropdown(id='year',
                    options=[{'label': i, 'value': i} for i in years_auto],
                    multi=False,
                    value= years_auto[-1],
                    ),
                ]
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
            
            # Live mode or not according to end_date
            # Real time control
            dcc.Interval(
                id='interval-log-update',
                interval=1*1000, # in milliseconds
                n_intervals=0
            ),

            html.Div([
                dcc.Graph(id='temperature-graph',)
            ],id='graph_framework', className ='nime columns',style={'width': '76%','float':'left','border': 'thin lightgrey solid','borderRadius': 5}),

            html.Div([
                html.Div([
                    html.P("Scale:", style={'font-weight': 'bold', 'margin-bottom': '10px'}),

                    dcc.DatePickerRange(id='date_range',

                        end_date = initial_end_date,
                        start_date = initial_start_date,
                        min_date_allowed=min_date,
                        max_date_allowed=max_date,
                        initial_visible_month=initial_month,
                    )
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
                
                html.Div([
                    html.Button('Autoscale', 
                                    id='autoscale', 
                                    n_clicks_timestamp=0,
                                    style= {'width': '100%'})
                ], style={'width': '100%', 'margin-bottom': '20px' }
                ),
            ],id='select_framework', className ='three columns', style={
                                'height':'100%', 
                                'float': 'right', 
                                'padding': 15,  
                                'borderRadius': 5, 
                                'border': 'thin lightgrey solid'}
            )
        ],className='row', style={'margin-top': 5, 'margin-bottom': 5,}
        ),
            
    ],id ='page',
    className='ten columns offset-by-one'
)


########################################################
# Callback the update speed
@app.callback(Output('experiment', 'options'),
              [Input('interval-log-update', 'n_intervals')])
def update_experiments(n_intervals):
    if n_intervals == 0:
        experiment_update = get_folder_names(all_folder_paths(path_lab))

        return [{'label': i, 'value': i} for i in experiment_update]

@app.callback(Output('year', 'options'),
              [Input('experiment', 'value')])
def update_years(exp):
    years_update = get_folder_names(all_folder_paths(path_lab + '\\' + exp + r'\data'))
    return [{'label': i, 'value': i} for i in years_update]


@app.callback(Output('channels_dropdown', 'options'),
              [Input('experiment', 'value'),
              Input('year', 'value')])
def update_channels(exp, year):
    
    try:
        path = path_lab + '\\' + exp + r'\data' + '\\' + year

        dates = all_folder_paths(path)
        print(dates)
        data_path = all_file_paths(dates[0], '.log')
        channels_update = get_effect_channels(data_path)
    
    except FileNotFoundError as error:
        print(error)
        print('There is no data in this folder')

    return [{'label': i, 'value': i} for i in channels_update]



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

# 
@app.callback(Output('dropdown-interval-control', 'value'),
                [Input('date_range', 'start_date'),
                 Input('date_range', 'end_date')])
def storage_mode(start_date, end_date):
    try:
        end_date = datetime.strptime(end_date,r'%Y-%m-%d')
        start_date = datetime.strptime(start_date, r'%Y-%m-%d')
    except TypeError as error:      
        print(error)
        print("Start day and end day have wrong filetype.")

    # Select record mode
    if end_date.date() < datetime.today().date():
        return 'no'
    else: 
        pass

# Dash can't have the same Input and Output
# Save the data as json file in cache
@app.callback([Output('before-log-storage', 'children'),
               Output('num-before-storage','children')],
                  [ Input('date_range', 'start_date'),
                  Input('date_range', 'end_date')])
def get_before_log(start_date, end_date):

    try:
        end_date = datetime.strptime(end_date,r'%Y-%m-%d')
        start_date = datetime.strptime(start_date, r'%Y-%m-%d')
    except TypeError as error:      
        print(error)
        print("Start day and end day have wrong filetype.")

    # Select record mode
    try: 

        if end_date.date() < datetime.today().date():
            storage_end_date = end_date
            run_log_df = get_data_str(start_date, storage_end_date, channels_auto, path_data_auto)      
        else: 
            storage_end_date = end_date + timedelta(days=-1)
            run_log_df = get_data_str(start_date, storage_end_date, channels_auto, path_data_auto)
        
        num = len(run_log_df)  
        print(run_log_df)                     
        json_data = run_log_df.to_json(orient='split')
       
        return json_data, str(num)

    except FileNotFoundError as error:      
        print(error)
        print("Please verify if the data is placed in the correct directory.")
        return None, '0'


# Update today's json data 
@app.callback([Output('today-log-storage', 'children'),
               Output('num-today-storage','children')],
                  [Input('interval-log-update', 'n_intervals'), 
                  Input('date_range', 'start_date'),
                  Input('date_range', 'end_date')])
def get_today_log(n_intervals, start_date, end_date):
    

    try:
        end_date = datetime.strptime(end_date, r'%Y-%m-%d')
        start_date = datetime.strptime(start_date, r'%Y-%m-%d')
    except TypeError as error:      
        print(error)
        print("Start day and end day have wrong filetype.")

    # Select live mode
    try: 
        if end_date.date() < datetime.today().date():
            return None,'0'
        elif end_date.date() == datetime.today().date(): 
            try:
                today_log_df = get_data_str(datetime.today(), datetime.today(), channels_auto, path_data_auto)
            except FileNotFoundError as error:      
                print(error)
                print("There is no data is placed in the today's directory.")
                return None, '0'
        else: 
            print(FileNotFoundError)
            print("The election of time range is wrong.")
            return None, '0'  
        num =len(today_log_df)             
        today_data = today_log_df.to_json(orient='split')

    except FileNotFoundError as error:      
        print(error)
        print("Please verify if the data is placed in the correct directory.")
        return None, '0'
    return today_data, str(num)

# display the data size
@app.callback(Output('div-num-display', 'children'),
              [Input('num-before-storage', 'children'),Input('num-today-storage', 'children')])
def update_num_display_and_time(num_before, num_today):  

    if num_before ==None:
        num_before = '0'
    if num_today==None:
        num_today = '0'

    total_num = int(num_before) + int(num_today)
    
    if total_num != 0:
        return html.H2('{0}'.format(total_num), style={ 'margin-top': '3px'})
    else:
        print('There is no cache data')

@app.callback(Output('temperature-graph', 'figure'),
            [Input('before-log-storage', 'children'),
             Input('today-log-storage', 'children'),
            Input('channels_dropdown', 'value'),
            Input('display_mode','value'),
            Input('autoscale','n_clicks_timestamp')])
def update_graph(before, today, selected_dropdown_value, display_mode_value, click):

    if (before != None) and (today != None):
        before_df = pd.read_json(before, orient='split')
        today_df = pd.read_json(today, orient='split')
        df = pd.concat([before_df, today_df], axis=0)
        
    elif (before != None) and (today == None): 
        before_df = pd.read_json(before, orient='split')
        df = before_df

    elif (before == None) and (today != None): 
        today_df = pd.read_json(today, orient='split')
        df = today_df
    else:
        raise FileNotFoundError('No json file')

    # create empty trace
    trace = []
    for channel in selected_dropdown_value:
        key_time = 'Time_'+channel
        key = channel
\\\\\\\\\\\\\\\\\\\\\\          ```````     `
        temp_df = pd.concat([df[key_time], df[key]], axis=1)
        temp_df[key_time] = pd.to_datetime(temp_df[key_time], format=r'%Y%m%d %H:%M:%S')

        trace.append(go.Scatter(x=temp_df[key_time], y=temp_df[key],mode='lines',
        opacity=0.7,name=channel, textposition='bottom center'))

    data = trace
    if display_mode_value == 'overlap':
        figure = {'data': data,
            'layout': {'colorway': color_list,
                       'height':600,
                       'title':" The sensor channel monitor",
                        'xaxis':{"title":"Date",
                            'rangeselector': {'buttons': list([
                                {'count': 10, 'label': '10m', 'step': 'minute', 'stepmode': 'backward'},
                                {'count': 1, 'label': '1h', 'step': 'hour', 'stepmode': 'backward'},
                                {'count': 6, 'label': '6h', 'step': 'hour', 'stepmode': 'backward'},
                                {'step': 'all'}])},
                        'rangeslider': {'visible': True}, 'type': 'date'},
                        'yaxis' : {"title":"Value"},
                        'uirevision': click,}}
        return  figure

    elif display_mode_value == 'separate':

        num =  len(selected_dropdown_value)

        fig = tools.make_subplots(rows=num, cols=1)
        
        color_small_list = color_list[:num]

        for index, (tra, chan, col) in enumerate(zip(trace, selected_dropdown_value, color_small_list)):
            
            fig.append_trace(tra, index, 1)
            fig['layout'] = {'colorway': col,
                       'height':600,
                       'title':" The channel of {0}".format(chan),
                        'xaxis':{"title":"Date",
                            'rangeselector': {'buttons': list([
                                {'count': 10, 'label': '10m ', 'step': 'minute', 'stepmode': 'backward'},
                                {'count': 1, 'label': '1h', 'step': 'hour', 'stepmode': 'backward'},
                                {'count': 6, 'label': '6h', 'step': 'hour', 'stepmode': 'backward'},
                                {'step': 'all'}])},
                        'rangeslider': {'visible': True}, 'type': 'date'},
                        'yaxis' : {"title":"Value"},
                       'uirevision': click,}                 
        return fig
    else:
        print('The creation of graph figure fails')


# Main
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)

# In Jupyter, debug = False 