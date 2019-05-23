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

TEST_MODE = True
test_data = get_data_string(datetime(2019, 4, 13), datetime(2019, 4, 13), channels_auto)
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
                #dcc.Graph(id='temperature-graph')
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
                )

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
def get_run_log(start_date, end_date):

    # Select record mode
    try: 

        if end_date.date() < datetime.today().date():
            storage_end_date = end_date
            run_log_df = get_data_string(start_date, storage_end_date, channels_auto)      
        else: 
            storage_end_date = end_date + timedelta(days=-1)
            run_log_df = get_data_string(start_date, storage_end_date, channels_auto)
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
def get_run_log(n_intervals, start_date, end_date):

    # Select live mode
    try: 
        if end_date.date() < datetime.today().date():
            return None,'0'
        elif end_date.date() == datetime.today().date(): 
            try:
                today_log_df = get_data_string(datetime.today(), datetime.today(), channels_auto)
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



# Main
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
