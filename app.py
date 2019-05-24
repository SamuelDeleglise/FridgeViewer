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

app.css.append_css({'external_url': 'https://rayonde.github.io/external_css/fridge.css'})  
server = app.server
CORS(server)

channels_auto = ['CH1 T']
years_auto = ['2019']
experiments_auto = ['DummyFridge']
min_date = datetime(2019, 4, 13)
max_date = datetime(2019, 4, 14)
initial_month = datetime(2019, 4, 13)
initial_end_date = datetime(2019, 4, 14)
initial_start_date = datetime(2019, 4, 13)
path_data_auto = r'LOGS\DummyFridge\data'
color_list = ["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056']
test_data = get_data_str(datetime(2019, 4, 13), datetime(2019, 4, 13), channels_auto, path_data_auto)
# Create app layout
app.layout = html.Div(
    [   
        # # Hidden Div Storing JSON-serialized dataframe of run log
        html.Div(id='before-log-storage', style={'display': 'none'}),
        html.Div(id='today-log-storage', style={'display': 'none'}),
        html.Div(id='num-before-log-storage', style={'display': 'none'}),
        html.Div(id='num-today-log-storage', style={'display': 'none'}),
        
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
                dcc.Graph(id='temperature-graph' )
            ],id='graph_framework', className ='nine columns'
            ),
            html.Div([
                html.Div([
                    html.P("Scale:", style={'font-weight': 'bold', 'margin-bottom': '10px'}),

                    dcc.DatePickerRange(id='date_range',

                        end_date = initial_end_date,
                        start_date = initial_start_date,
                        min_date_allowed=min_date,
                        max_date_allowed=max_date,
                        initial_visible_month=initial_month,
                        style={'width': '100%'},

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

                html.Div(id="div-num-display",
                    style={'width': '100%', 'margin-bottom': '20px' }
                ),
                html.Div([html.Button('Autoscale', id='autoscale', n_clicks_timestamp=0),],
                    style={'width': '100%', 'margin-bottom': '20px' }
                ),
                


            ],id='select_framework', className ='three columns', style={
                                'height':'100%', 
                                'float': 'right', 
                                'padding': 15, 
                                'margin': 5, 
                                'borderRadius': 5, 
                                'border': 'thin lightgrey solid'}
            )
        ],className='row', style={'margin-top': 5, 'margin-bottom': 5,}
        ),
            
    ],
    className='ten columns offset-by-one'
)


########################################################

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
    # Select record mode
    if end_date.date() < datetime.today().date():
        return 'no'
    else: 
        pass

# Dash can't have the same Input and Output
# Save the data as json file in cache
@app.callback([Output('before-log-storage', 'children'),
               Output('num-before-log-storag','children')],
                  [ Input('date_range', 'start_date'),
                  Input('date_range', 'end_date')])
def get_before_log(start_date, end_date):

    # Select record mode
    try: 

        if end_date.date() < datetime.today().date():
            storage_end_date = end_date
            run_log_df = get_data_str(start_date, storage_end_date, channels_auto, path_data_auto)      
        else: 
            storage_end_date = end_date + timedelta(days=-1)
            run_log_df = get_data_str(start_date, storage_end_date, channels_auto, path_data_auto)
        num = len(run_log_df)                       
        json_data = run_log_df.to_json(orient='split')

    except FileNotFoundError as error:      
        print(error)
        print("Please verify if the data is placed in the correct directory.")
        return None, '0'
    return json_data, str(num)


# Update today's json data 
@app.callback([Output('today-log-storage', 'children'),
               Output('num-today-log-storag','children')],
                  [Input('interval-log-update', 'n_intervals'), 
                  Input('date_range', 'start_date'),
                  Input('date_range', 'end_date')])
def get_today_log(n_intervals, start_date, end_date):

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
    total_num = int(num_before) + int(num_today)
    
    if total_num != 0:
        return html.Div([html.P("Number of data points:", style={'font-weight': 'bold', 'margin-bottom': '10px'}),
                html.H2('{0}'.format(total_num), style={'margin-top': '3px'})])
    else:
        print('There is no cache data')

@app.callback(Output('temperature-graph', 'figure'),
            [Input('before-log-storage', 'children'),
             Input('today-log-storage', 'children'),
            Input('channels_dropdown', 'value'),
            Input('display_mode','value'),
            Input('autoscale','n_clicks_timestamp')])
def update_graph(before, today, selected_dropdown_value, display_mode_value, click):
    try:   
        before_df = pd.read_json(before, orient='split')
        today_df = pd.read_json(today, orient='split')


    except FileNotFoundError as error:
        print(error)
        print("Please verify if the json file is correct.")
        print("Please verify if the data is placed in the correct directory.")

    # create vide trace
    trace = []
    for channel in selected_dropdown_value:
        key_time = 'Time_'+channel
        key = channel
        
        temp_before = pd.concat([before_df[key_time], before_df[key]], axis=1)
        temp_today = pd.concat([today_df[key_time], today_df[key]], axis=1)

        temp_before[key_time] = datetime.strptime(temp_before[key_time], r'%y%m%d %H:%M:%S')
        temp_today[key_time] = datetime.strptime(temp_today[key_time], r'%y%m%d %H:%M:%S')

        temp = pd.concat([temp_before, temp_today], axis=0)

        trace.append(go.Scatter(x=temp[key_time], y=temp[key],mode='lines',
        
        opacity=0.7,name=channel, textposition='bottom center'))

    data = trace
    if display_mode_value == 'overlap':
        figure = {'data': data,
            'layout': {'colorway': color_list,
                       'height':600,
                       'title':" The sensor channel monitor",
                        'xaxis':{"title":"Date",
                            'rangeselector': {'buttons': list([
                                {'count': 10, 'label': 'last 10 mins', 'step': 'minute', 'stepmode': 'backward'},
                                {'count': 1, 'label': 'last 1 hour', 'step': 'hour', 'stepmode': 'backward'},
                                {'count': 6, 'label': 'last 6 hour', 'step': 'hour', 'stepmode': 'backward'},
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
            fig['layout'] = {'colorway': color_list,
                       'height':600,
                       'title':" The sensor channel monitor",
                        'xaxis':{"title":"Date",
                            'rangeselector': {'buttons': list([
                                {'count': 10, 'label': 'last 10 mins', 'step': 'minute', 'stepmode': 'backward'},
                                {'count': 1, 'label': 'last 1 hour', 'step': 'hour', 'stepmode': 'backward'},
                                {'count': 6, 'label': 'last 6 hour', 'step': 'hour', 'stepmode': 'backward'},
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
