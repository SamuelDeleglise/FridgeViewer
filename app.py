# In[]:
# Import required libraries
import os
import pandas as pd
import json
from flask import Flask
from flask_cors import CORS
from datetime import timedelta, date, time, datetime
import numpy as np
import sys
import time
from data import *

# need to update the latest version
#######################################################
import dash #latest version 1.0.0
from dash import no_update
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from plotly import tools

app = dash.Dash(__name__)

# external CSS
# https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css
# https://codepen.io/chriddyp/pen/bWLwgP.css
app.css.append_css({'external_url': 'https://rayonde.github.io/external_css/stylesheet.css'})  

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

server = app.server
CORS(server)
#######################################################


years_auto = ['2019']
experiments_auto = ['DummyFridge']
min_date = datetime(2019, 4, 13)
max_date = datetime.today()
initial_month = datetime(2019, 4, 13)
initial_end_date = datetime(2019, 4, 14)
initial_start_date = datetime(2019, 4, 13)
path_data_auto = r'LOGS\DummyFridge\data'

global path_lab
path_lab = r"C:\Users\YIFAN\Documents\GitHub\LOGS"
path_lab2 = path_lab
path_lab3 = path_lab
color_list = ["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056']




#########################################################
# General Functions
#
#
#
#########################################################

def update_jsonfile(path, key, value, valuetype=str):
    # if not exist, create an empty json file 
    if not os.path.isfile(path):
         with open(path, 'w') as jsonfile:
            jsonfile.write(json.dumps({}))
    
    # Open the JSON file for reading
    with open(path, 'r+') as jsonfile:
        data = json.load(jsonfile) 
        # update data
        
        if key in data.keys():
            if valuetype is str:
                if value not in data[key]:
                    data[key].append(value)
            elif valuetype is dict:
                data[key].update(value)
            elif valuetype is list:
                data[key].extend(value)
        else:
            if valuetype is dict:
                data.update({key: value})
            elif valuetype is str:
                data.update({key: [value]})
            elif valuetype is list:
                data.update({key: value})

        jsonfile.seek(0)  # rewind
        jsonfile.write(json.dumps(data, indent=4))

        # this deals with the case where the new data is smaller than the previous.
        jsonfile.truncate()

def write_channels_config(path):
    try:
        date_list = get_folder_names(all_folder_paths(path))
    except FileNotFoundError as error:
        print(error)
        print('Cannot get the year list')
    else:
        for single_date_str in date_list: 
            channels_update = set()
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
            update_jsonfile(path + r'\channels.json', single_date_str, channels_update, valuetype=list)
    return None

def write_info(path_lab):
    try:
        experiment_update = get_folder_names(all_folder_paths(path_lab))
    except FileNotFoundError as error:
        print(error)
        print('Cannot get the experiment list')
    else:
        for exp in experiment_update:
            update_jsonfile(path_lab + r'\exp_info.json', 'experiments', exp)
    
            try:
                years_update = get_folder_names(all_folder_paths(path_lab + '\\' + exp + r'\data'))
            except FileNotFoundError as error:
                print(error)
                print('Cannot get the year list')
            else:
                temp = {}
                temp[exp] = years_update
                update_jsonfile(path_lab + r'\exp_info.json', 'years', temp, valuetype= dict)  
    return None    
        
#########################################################
# Layout Functions
#
#
#
#########################################################

def create_cache_div(name, info):
    return dcc.Store(id='{0}-log-storage'.format(name), storage_type='memory', data = info)

def get_menu():
    menu = html.Div([
        html.Div([
            dcc.Link('Cryogenic Fridge', href='/opto/cryogenic-fridge', className='tab first',),
        ],className='two columns', style={'display': 'inline-block'}),
        html.Div([
            dcc.Link('Membrance', href='/opto/membrance', className='tab',),
        ],className='two columns', style={'display': 'inline-block'}),
        html.Div([
            dcc.Link(' Micro cavity', href='/opto/micro-cavity', className='tab',),
        ],className='two columns', style={'display': 'inline-block'}),
    
    ],style={ 'display': 'inline-block'})
    return menu


# returns modal (hidden by default)
def modal():
    return html.Div(
        html.Div(  
            html.Div([
                    # modal header
                    html.Div(
                        [
                            html.Span(
                                "Configuration",
                                style={
                                    "color": "#506784",
                                    "fontWeight": "bold",
                                    "fontSize": "20",
                                },
                            ),
                            html.Span(
                                "×",
                                id="configuration_modal_close",
                                n_clicks=0,
                                style={
                                    "float": "right",
                                    "cursor": "pointer",
                                    "margin-top": "0",
                                    "margin-bottom": "17",
                                },
                            ),
                        ],
                        className="row",
                        style={"borderBottom": "1px solid #C8D4E3"},
                    ),


                    # modal form 
                    html.Div([
                        
                        html.Div([      
                            # left div
                            html.Div(
                                [
                                    html.P(
                                        [
                                            "Name"
                                        ],
                                        style={
                                            "float": "left",
                                            "margin-top": "4",
                                            "margin-bottom": "2",
                                        },
                                        className="row",
                                    ),
                                    dcc.Input(
                                        id="new_configuration_name",
                                        placeholder="Name of user",
                                        type="text",
                                        value="",
                                        style={"width": "100%"},
                                    ),

                                    html.P(
                                        [
                                            "Data mode"
                                        ],
                                        style={
                                            "textAlign": "left",
                                            "margin-bottom": "2",
                                            "margin-top": "4",
                                        },
                                    ),
                                    dcc.Dropdown(
                                        id="new_configuration_mode",
                                        options=[
                                            {
                                                "label": "Live mode",
                                                "value": "Live mode",
                                            },
                                            {
                                                "label": "No update",
                                                "value": "No update",
                                            },
                                        ],
                                        clearable=False,
                                        value="Live mode",
                                    ),

                                    html.P(
                                        [
                                            "Figure setting"
                                        ],
                                        style={
                                            "textAlign": "left",
                                            "margin-bottom": "2",
                                            "margin-top": "4",
                                        },
                                    ),
                                    dcc.Dropdown(
                                        id="new_configuration_figure",
                                        options=[
                                            {
                                                "label": "Single plot",
                                                "value": "Single plot",
                                            },
                                            {
                                                "label": "Multiple plots",
                                                "value": "Multiple plots",
                                            },
                                        ],
                                        clearable=False,
                                        value="Single plot",
                                    ),

                                ],
                                className="six columns",
                                style={"padding-right": "15"},
                            ),
                            
                            # right div
                            html.Div(
                                [
                                    html.P(
                                        "Experiment",
                                        style={
                                            "textAlign": "left",
                                            "marginBottom": "2",
                                            "marginTop": "4",
                                        },
                                    ),
                                    dcc.Dropdown(
                                        id="new_configuration_exp",
                                        options=[],
                                    ),

                                    html.P(
                                        "Year",
                                        style={
                                            "textAlign": "left",
                                            "marginBottom": "2",
                                            "marginTop": "4",
                                        },
                                    ),
                                    dcc.Dropdown(
                                        id="new_configuration_year",
                                        options=[],
                                    ),
                                    
                                    
                                ],
                                className="six columns",
                                style={"paddingLeft": "15"},
                            ),
                        ],className="row",
                        ),
                        
                        # large div
                        html.Div([
                            html.P(
                                    [
                                        "Path of dataset"
                                    ],
                                    style={
                                        "float": "left",
                                        "margin-top": "4",
                                        "margin-bottom": "2",
                                    },
                                    className="row",
                                ),
                                dcc.Input(
                                    id="new_configuration_path",
                                    #placeholder="Path of dataset",
                                    type="text",
                                    value=path_lab,
                                    style={"width": "100%"},
                                ),

                                html.P(
                                    [
                                        "Channel"
                                    ],
                                    style={
                                        "textAlign": "left",
                                        "margin-bottom": "2",
                                        "margin-top": "4",
                                    },
                                ),
                                dcc.Dropdown(
                                    id="new_configuration_channel",
                                    options=[],
                                    multi = True
                                ),
                        ],className="row",
                        style={"margin-top": "5"},),
                    ]
                    ),

                    # submit button
                    html.Div([
                        html.Span(
                        "Submit",
                        id="submit_new_configuration",
                        n_clicks=0,
                        className="button button-primary",
                        
                    ),
                    ], style={'margin-top': 5})
                
                    
            ],className="modal-content", style={"textAlign": "center"},
            )
        ), id="configuration_modal", style={"display": "none"},
    )


#####################################################################################

page1 = html.Div([ 
    
    # CSS
    html.Link(
        rel='stylesheet',
        href='/static/stylesheet.css'
    ),

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
        html.Div(id='today-update-storage', style={'display': 'none'}),

        dcc.Store(id='num-before-storage', storage_type='memory'),
        dcc.Store(id='num-today-storage', storage_type='memory'),
        
        # dcc.Store(id='experiments-storage',storage_type='session'),
        # dcc.Store(id='years-storage',storage_type='session'),
        dcc.Store(id='channels-storage',storage_type='session'),
        dcc.Store(id='exp_info',storage_type='session'),
        dcc.Store(id='user_info',storage_type='session'),
    ], id = 'cache'
    ),
    
    modal(),

    html.Div(
        [
            html.H1(
                'Fridge Viewer',
                style={ 
                'float': 'left',
                },
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
    
    html.Div([
        
        
        html.Div([
            html.Div([
            html.Span( 'Reset config files',
                        id="reset_config",
                        n_clicks=0,
                        className="button",
                        style={"float": "right",}
                ),
            ], style={'margin-right': 5,}
            ),
            html.Div([
                dcc.Dropdown(
                    id="selection_config",
                    options=[],
                    value=''
                )
            ], style={"flex": "auto","width" : "100%", "float": "left",'margin-right': 5,}
            ),
   
            html.Div([   
                html.Span( 'Add Configuration',
                        id="new_opportunity",
                        n_clicks=0,
                        className="button button-primary",
                        style={"float": "right",}
                )
            ]
            ),

        ],className="six columns", style={"display": "flex","flex-direction": "row", "float": "right",}
        ),
    ], className='row' , style={'margin-top': 5, 'margin-bottom': 5,}
    ),


    html.Div([
        html.Div([
            html.Div([
                html.P('Experiment:',style={}),
        ], className= 'droptitle' ,style={"width": "80px" , "padding": 5,"float": "left", }
            ),
            html.Div([
                dcc.Dropdown( id ='experiment',
                #options=[{'label': i, 'value': i} for i in experiments_auto],
                multi=False,
                #value= experiments_auto[0],
                ),
            ], className= 'dropcontent', style={"width": "100%"}
            ), 
        ], id='experiment-framework',className='six columns',style={"display": "flex","flex-direction": "row",}   
        ),
    
        html.Div([
            html.Div([
                html.P('Year:'),
            ], className= 'droptitle' ,style={ "width": "80px","padding": 5,"float": "left", }
            ), 
            html.Div([
                dcc.Dropdown(id='year',
                #options=[{'label': i, 'value': i} for i in years_auto],
                multi=False,
                #value= years_auto[-1],
                ),
            ], className= 'dropcontent', style={"width": "100%"}
            ), 

        ], id='years-framework', className='six columns',style={"display": "flex","flex-direction": "row",}   
        )
    ],className='row' , style={'margin-top': 5, 'margin-bottom': 5,}
    ),

    html.Div([
        
        html.Div([
            html.P('Channel:'),
            # head style
        ], className= 'droptitle' ,style={"width": "80px" , "padding": 5,"float": "left", }
        ),

        html.Div([    
            # Channel selection dropdown
            dcc.Dropdown(id='channels_dropdown',
                    multi=True,
            )
            # channel selection style
        ], className= 'dropcontent', style={"width": "100%"}
        ),
    ],className='row' , style={"display": "flex","flex-direction": "row",'margin-top': 5, 'margin-bottom': 5,}
    ),

    html.Div([
        html.Div([
            html.Div([

                html.Div(id="div-data-display")

                ],style={'width': '100%', 'margin-bottom': '20px' }
                ),

            html.Div([
                dcc.Graph(id='temperature-graph')
            ],style={}
            )
        ],id='graph_framework', className ='nine columns',style={'display': 'inline-block'}),

        html.Div([
            html.Div([

                html.Div([
                     html.Button('Real-time data', 
                                    id='data_set', 
                                    n_clicks=0,
                                    style= {'width': '100%'})

                ],style={'width': '100%', 'margin-bottom': '20px' }
                ),

                html.Div([
                    html.Button('Autoscale', 
                                    id='autoscale', 
                                    n_clicks=0,
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
                            {'label': ' Overlap', 'value': 'overlap'},
                            {'label': ' Timeslider', 'value': 'timeslider'},
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
        ],id='select_framework', className ='three columns', style={
                            'height':'100%', 
                            'display': 'inline-block',
                            'float': 'right',}
        )
    ],className='row', style={'margin-top': 5, 'margin-bottom': 5,}
    ),
        
],id ='page', className='ten columns offset-by-one'
)


page2 = page1

page3 = page1



# Create app layout
# Describe the layout, or the UI, of the app
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', children = page1)
])

#########################################################
#
#
#
#
#########################################################
# hide/show modal
@app.callback(Output("configuration_modal", "style"), 
            [Input("new_opportunity", "n_clicks"),])
def display_configuration_modal_callback(n):
    if n > 0:
        return {"display": "block"}
    return {"display": "none"}


# reset to 0 add button n_clicks property
@app.callback(
    Output("new_opportunity", "n_clicks"),
    [
        Input("configuration_modal_close", "n_clicks"),
        Input("submit_new_configuration", "n_clicks"),
    ],
)
def close_modal_callback(n, n2):
    return 0

# reset to 0 submit button n_clicks property
@app.callback(
    Output("submit_new_configuration", "n_clicks"),
    [Input("configuration_modal_close", "n_clicks"),],
    [State("submit_new_configuration", "n_clicks")])
def close_modal_callback(n, n2):
    return 0

# Update page
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/opto' or pathname == '/' or pathname == '/opto/cryogenic-fridge':
        return page2
    elif pathname == '/opto/membrance':

        path_lab = path_lab2
        return page2
    elif pathname == '/opto/micro-cavity':

        path_lab = path_lab3
        return page3
    else:
        return no_update


# Get static CSS
@app.server.route('/static/<path:path>')
def static_file(path):
    static_folder = os.path.join(os.getcwd(), 'static')
    return send_from_directory(static_folder, path)
#########################################################
#
#
#
#
#########################################################

@app.callback([Output('new_configuration_exp', 'options'), Output('new_configuration_exp', 'value')],
              [Input('exp_info','data')])
def new_experiments(info):
    if info:  
        experiments = info['experiments']
        temp = {}
        temp['experiments'] = experiments
        
        return [{'label': i, 'value': i} for i in experiments], experiments[0]
    else:
        return no_update, no_update


@app.callback([Output('new_configuration_year', 'options'),
              Output('new_configuration_year', 'value'),],
              [Input('new_configuration_exp', 'value'), 
              Input('exp_info','data')],)
def new_years(exp, info):
    if exp: 
        if info:
            years_update = info['years'][exp] 
            return [{'label': i, 'value': i} for i in years_update], years_update[-1]
        else: 
            return no_update, no_update
    return no_update, no_update


@app.callback([Output('new_configuration_channel', 'options'),
               Output('new_configuration_channel', 'value'),],
              [Input('new_configuration_exp', 'value'),
              Input('new_configuration_year', 'value'),
              Input('date_range', 'start_date'),
              Input('date_range', 'end_date')],)
def new_channels(exp, year, start_date, end_date):
    if exp is not None and year is not None:    
        path = path_lab + '\\' + exp + r'\data' + '\\' + year
        channels_update = set()
        data = {}
        
        # the date interval
        try:
            end_date_td = datetime.strptime(end_date,r'%Y-%m-%d')
            start_date_td = datetime.strptime(start_date, r'%Y-%m-%d')
        except TypeError as error:      
            print(error)
            print("Start day and end day have wrong filetype.")
        else:
            date_list_td = datelist(start_date_td, end_date_td) # timedate type
        
        if os.path.isfile(path + r'\channels.json'): 
            pass
        else:
            # reset the channel config file
            write_channels_config(path)  
        
        # read channel config file
        with open(path + r'\channels.json') as jsonfile:
            data = json.load(jsonfile)     
        
        # search all channels in the date interval
        for date in date_list_td:
            single_date_str = date.strftime(r'%y-%m-%d')
            if single_date_str in data.keys():
                channels_update.update(set(data[single_date_str]))
            else: 
                pass
        
        channels_update = list(channels_update)
        data['channels'] = channels_update
        
        if channels_update:
            return [{'label': i, 'value': i} for i in channels_update], channels_update
        else:
            return no_update, no_update
    else:
        return no_update, no_update



@app.callback(Output('selection_config', 'options'),
              [Input('submit_new_configuration', 'n_clicks'),
              Input('exp_info', 'data')],
              [State('new_configuration_name', 'value'),
               State('new_configuration_exp', 'value'),
              State('new_configuration_year', 'value'),
              State('new_configuration_mode', 'value'),
              State('new_configuration_figure', 'value'),
              State('new_configuration_path', 'value'),
              State('new_configuration_channel', 'value'),])
def new_configuration(n, name, exp, year, mode, figure, path, channels):
    if n>0:
        data = {} 
        data['name'] = name
        data['experiment'] = exp
        data['year'] = year
        data['mode'] = mode
        data['figure'] = figure
        data['path'] = path
        data['channels'] = channels
        update_jsonfile(path_lab + r'\user.json', name, data, valuetype=dict)
        
        options = []
        with open(path_lab + r'\user.json') as jsonfile:
            data = json.load(jsonfile)
            options = [{'label': i, 'value': i} for i in data.keys()]
        return options
    else: 
        return no_update

#########################################################
#
#
#
#
#########################################################
# Reset config file  
# @app.callback(Output('interval-info-update', 'n_intervals'),
#               [Input('reset_config', 'n_clicks')],)
# def reset_configuration(n):
#     if n>0:
#         # rewrite exp_info.json
#         write_info(path_lab)
#         with open(path_lab + r'\exp_info.json', 'r') as json_file:
#             data = json.load(json_file)

#         # rewrite channels.json
#         for exp in data['experiments']:
#             for year in data['years'][exp]:
#                 path = path = path_lab + '\\' + exp + r'\data' + '\\' + year
#                 write_channels_config(path)
#         return  0
#     return no_update

# Get the experiment information 
@app.callback(Output('exp_info','data'),
              [Input('interval-info-update', 'n_intervals')],
              [State('exp_info','data')])
def update_exp_info(n_intervals, data):
    if n_intervals is 0:
        # read exp information
        if os.path.isfile(path_lab + r'\exp_info.json'):
            pass
        
        # create exp information 
        else:
            write_info(path_lab)
        
        with open(path_lab + r'\exp_info.json', 'r') as json_file:
            data = json.load(json_file)
                
        return data
    else: 
        return no_update

        
# Get the experiment list automatically every 24h
@app.callback([Output('experiment', 'options'), Output('experiment', 'value')],
              [Input('exp_info','data')])
def update_experiments(info):
    if info:  
        experiments = info['experiments']
        temp = {}
        temp['experiments'] = experiments
        
        print(experiments)
        return [{'label': i, 'value': i} for i in experiments], experiments[0]
    else:
        return no_update, no_update

# # Information is sotred individually
# # Get the experiment list automatically every 24h
# @app.callback([Output('experiment', 'options'),
#                Output('experiment', 'value'),
#               Output('experiments-storage','data')],
#               [Input('interval-info-update', 'n_intervals')],
#               [State('experiments-storage','data')])
# def update_experiments(n_intervals, data):
#     if n_intervals is 0:
#         a = {}
#         try:
#             experiment_update = get_folder_names(all_folder_paths(path_lab))
#         except FileNotFoundError as error:
#             print(error)
#             print('Cannot get the experiment list')
#             return no_update, no_update, no_update
#         else:
#             data = data or {}
#             a['experiments'] = experiment_update
#             return [{'label': i, 'value': i} for i in experiment_update], experiment_update[0], a
#     return no_update, no_update, no_update
#########################################################

# Get year list automatically
@app.callback([Output('year', 'options'),
              Output('year', 'value'),],
              [Input('experiment', 'value'), 
              Input('exp_info','data')],)
def update_years(exp, info):
    if exp: 
        if info:
            years_update = info['years'][exp] 
            return [{'label': i, 'value': i} for i in years_update], years_update[-1]
        else: 
            return no_update, no_update
    return no_update, no_update

# # Get year list automatically
# @app.callback([Output('year', 'options'),
#               Output('year', 'value'),
#                Output('years-storage','data')],
#               [Input('experiment', 'value')],
#               [State('years-storage','data')])
# def update_years(exp, data):

#     if exp is not None: 
#         years_update = get_folder_names(all_folder_paths(path_lab + '\\' + exp + r'\data'))
#         data = data or {}
#         data['years'] = years_update
#         return [{'label': i, 'value': i} for i in years_update], years_update[-1], data
    # else: 
    #     return no_update, no_update, no_update
#########################################################
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
        data = data or {}
        
        # the date interval
        try:
            end_date_td = datetime.strptime(end_date,r'%Y-%m-%d')
            start_date_td = datetime.strptime(start_date, r'%Y-%m-%d')
        except TypeError as error:      
            print(error)
            print("Start day and end day have wrong filetype.")
        else:
            date_list_td = datelist(start_date_td, end_date_td) # timedate type
        
        if os.path.isfile(path + r'\channels.json'): 
            pass
        else:
            # reset the channel config file
            write_channels_config(path)  
        
        # read channel config file
        with open(path + r'\channels.json') as jsonfile:
            data = json.load(jsonfile)     
        
        # search all channels in the date interval
        for date in date_list_td:
            single_date_str = date.strftime(r'%y-%m-%d')
            if single_date_str in data.keys():
                channels_update.update(set(data[single_date_str]))
            else: 
                pass
        
        channels_update = list(channels_update)
        data['channels'] = channels_update
        
        if channels_update:
            return [{'label': i, 'value': i} for i in channels_update], channels_update, data
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
        dates = []
        
        if os.path.isfile(path + r'\channels.json'): 
            pass
        else:
            # reset the channel config file
            write_channels_config(path)  
        
        # read channel config file
        with open(path + r'\channels.json') as jsonfile:
            data = json.load(jsonfile)    
        
        for date in data.keys():
            dates.append(datetime.strptime(date,r'%y-%m-%d'))

        min_date =min(dates)
        max_date = max(dates)

        return min_date, max_date, max_date, max_date, max_date
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
                 [State('before-log-storage', 'children'),
                  State('num-before-storage','data'),])

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
            # 
            if 'exp_before' in before:
                # the stored data is same as the selected exp
                if exp == before['exp_before']:
                    
                    date_list_old = list(before.keys())
                    if 'exp_before' in date_list_old:
                                    date_list_old.remove('exp_before')
                    if 'exp_today' in date_list_old:
                                    date_list_old.remove('exp_today')

                    # date_list_old is not empty 
                    if  date_list_old:
                        date_list_temp = []
                        for date in date_list_old:
                            date_list_temp.append(datetime.strptime(date, r'%Y-%m-%d'))
                        
                        start_date_old = min(date_list_temp)
                        end_date_old = max(date_list_temp)
                        date_list_old = date_list_temp
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
                        
                        before['exp_before'] = exp
                        before.update(cache_dic)  
                        return before, {'num_before': num_total}
                    else:
                        print("The channel set is empty.")
                        return no_update, no_update
                else:
                    return None, {'num_before': 0}
            else: 
                return no_update, no_update
        else:
            # before is None 
            date_update = date_list
            
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

                cache_dic['exp_before'] = exp   
                return cache_dic, {'num_before': num_total}
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

n_clicks_autoscale = 0

@app.callback([Output('temperature-graph', 'figure'),
               Output('div-data-display', 'children')],
            [Input('before-log-storage', 'children'),
            Input('date_range', 'end_date'),
            Input('date_range', 'start_date'),
            Input('today-log-storage', 'children'),
            Input('channels_dropdown', 'value'),
            Input('display_mode','value'),
            Input('autoscale','n_clicks')],
            [State('temperature-graph', 'figure'),
             State('temperature-graph', 'relayoutData')])
def update_graph(before_data, end_date, start_date, today_data, selected_dropdown_value, display_mode_value, click, figure, relayout):
    
    global n_clicks_autoscale
    if click is None:
        click = 0
    if click>n_clicks_autoscale:
        do_autoscale = True
        print("autoscale was clicked")
        n_clicks_autoscale = click
    else:
        do_autoscale = False

    layout_set1 = {'colorway': color_list,
                       'title':"The sensor channel monitor",
                       'height':700,
                        'xaxis':{"title":"Date",
                                'rangeselector': {'buttons': list([
                                {'count': 10, 'label': '10m', 'step': 'minute', 'stepmode': 'backward'},
                                {'count': 1, 'label': '1h', 'step': 'hour', 'stepmode': 'backward'},
                                {'count': 6, 'label': '6h', 'step': 'hour', 'stepmode': 'backward'},
                                {'count': 1, 'label': '1 day', 'step': 'day', 'stepmode': 'backward'},
                                {'count': 3, 'label': '3 days', 'step': 'day', 'stepmode': 'backward'},
                                {'count': 7, 'label': '1 week', 'step': 'day', 'stepmode': 'backward'},
                                {'step': 'all'}])}, 'type': 'date'},
                        'margin':{'l':60, 'b': 40, 't': 80, 'r': 10},
                        'yaxis' : {"title":"Value",
                                },
                }

    layout_set2 = {'colorway': color_list,
                       'title':"The sensor channel monitor",
                       'height':700,
                        'xaxis':{"title":"Date",
                                'rangeselector': {'buttons': list([
                                {'count': 10, 'label': '10m', 'step': 'minute', 'stepmode': 'backward'},
                                {'count': 1, 'label': '1h', 'step': 'hour', 'stepmode': 'backward'},
                                {'count': 6, 'label': '6h', 'step': 'hour', 'stepmode': 'backward'},
                                {'count': 1, 'label': '1 day', 'step': 'day', 'stepmode': 'backward'},
                                {'count': 3, 'label': '3 days', 'step': 'day', 'stepmode': 'backward'},
                                {'count': 7, 'label': '1 week', 'step': 'day', 'stepmode': 'backward'},
                                {'step': 'all'}])}, 'type': 'date',
                        'rangeslider':{'visible':'True'}},
                        'margin':{'l':60, 'b': 40, 't': 80, 'r': 10},
                        'yaxis' : {"title":"Value",
                                },
                }
    
    start_date = datetime.strptime(start_date, r'%Y-%m-%d')
    end_date = datetime.strptime(end_date, r'%Y-%m-%d')
    date_list = datelist(start_date, end_date)
  
    if end_date.date() == datetime.today().date(): 
        # to keep same format for single channel or multiple channels
        if not isinstance(selected_dropdown_value, (list,)):
            selected_dropdown_value = [selected_dropdown_value]
        
        if today_data is not None:
            trace = []
            dis = []

            # read data from json cache
            if before_data is not None:
                before_data.update(today_data)
            else:
                before_data = today_data
            
            # The keys of 'before_data' contains the keywords 'exp_before' or 'exp_today' and corresponding years
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
                    data_df = pd.concat([data_df, temp_df], axis=0) 

            # selected_dropdown_value is not None or not empty
            if selected_dropdown_value is not None or selected_dropdown_value:
                
                maxtime_list = []
                mintime_list = []

                for channel in selected_dropdown_value:
                    channel_time = 'Time_'+ channel

                    # drop all NaN
                    if channel in data_df:
                        temp = pd.DataFrame()
                        temp[channel] = data_df[channel]
                        temp[channel_time] = data_df[channel_time]
                        temp.dropna(inplace=True)

                        maxtime_list.append(temp[channel_time].iloc[-1])
                        mintime_list.append(temp[channel_time].iloc[0])

                        trace.append(go.Scatter(x=temp[channel_time], y=temp[channel],mode='lines', opacity=0.7,name=channel, textposition='bottom center'))
                        dis.append(html.H6('{0} : {1}'.format(channel, temp[channel].iloc[-1]), style={ 'margin-top': '3px'}))
                 
                # the time of last data
                # 'pd.to_datetime' converts the time in UTC, so here we use 'datetime.strptime' to keep same format 
                maxtime =datetime.today()
                if maxtime_list:
                    max_list =[]
                    for time in maxtime_list:
                        max_list.append(datetime.strptime(time, '%Y-%m-%d %H:%M:%S'))
                    maxtime = max(max_list)
                
                if mintime_list:
                    min_list =[]
                    for time in mintime_list:
                        min_list.append(datetime.strptime(time, '%Y-%m-%d %H:%M:%S'))
                    mintime = max(min_list)

                # overlap display
                if display_mode_value == 'overlap':
                    figure = {'data': trace, 'layout': layout_set1}
                
                # time slider 
                elif display_mode_value == 'timeslider':
                    figure = {'data': trace, 'layout': layout_set2}
                
                # separate dislay
                elif display_mode_value == 'separate':
                    num =  len(selected_dropdown_value)
                    figure = tools.make_subplots(rows=num, cols=1)
    
                    for index, (tra, chan) in enumerate(zip(trace, selected_dropdown_value)):     
                        figure.append_trace(tra, index+1, 1)
                        figure['layout']['xaxis{}'.format(index+1)].update(title='The channel of {0}'.format(chan)) 

                    figure['layout'].update(height=600*num) 
                
                # keep the zoom 
                if figure is not None:
                    
                    # have attribute 'relayout, the attribute 'range' exists only execute the zoom 
                    if relayout is not None:
                        relayout_maxrange = None
                        # x range maximum
                        if 'xaxis.range[1]' in relayout or 'xaxis.range' in relayout:
                             
                            # get the previous range
                            try:
                                maxrange = datetime.strptime(relayout['xaxis.range[1]'],"%Y-%m-%d %H:%M:%S")
                                relayout_maxrange = maxrange.timestamp()
                            except:
                                try:
                                    relayout_maxrange = datetime.strptime(relayout['xaxis.range[1]'],"%Y-%m-%d %H:%M:%S.%f").timestamp()
                                except:
                                    try:
                                        relayout_maxrange = datetime.strptime(relayout['xaxis.range'][1],"%Y-%m-%d %H:%M:%S").timestamp()
                                    except:
                                        relayout_maxrange = datetime.strptime(relayout['xaxis.range'][1],"%Y-%m-%d %H:%M:%S.%f").timestamp()
                        
                        # the range shown in the figure 
                        # now_maxrange is the last time or the actual range maximum 
                        #print(figure['layout'])
                        if 'xaxis' in figure['layout']:

                            if 'range' in figure['layout']['xaxis']:

                                if figure['layout']['xaxis']['range'] is not None:
                                    try:
                                        now_maxrange =  datetime.strptime(figure['layout']['xaxis']['range'][1],"%Y-%m-%d %H:%M:%S")
                                    except:
                                        now_maxrange =  datetime.strptime(figure['layout']['xaxis']['range'][1],"%Y-%m-%d %H:%M:%S%f")
                                else:
                                    now_maxrange = maxtime
                            elif maxtime:
                                    now_maxrange = maxtime

                        elif 'xaxis1' in figure['layout']:
                            temp_now_list = []
                            for index, tra in enumerate(trace):     
                                
                                if 'range' in figure['layout']['xaxis{}'.format(index+1)]:
                                    try:
                                         temp_now =  datetime.strptime(figure['layout']['xaxis{}'.format(index+1)]['range'][1],"%Y-%m-%d %H:%M:%S")
                                    except:
                                        temp_now =  datetime.strptime(figure['layout']['xaxis{}'.format(index+1)]['range'][1],"%Y-%m-%d %H:%M:%S%f")
                                    temp_now_list.append(temp_now)
                                    
                            now_maxrange = max(temp_now_list)
                        elif maxtime:
                            now_maxrange = maxtime
                        
                        # the threshold of showing the updated data
                        threshold = (maxtime.timestamp()-100)
                        
                        # print('maxtime', maxtime)
                        # print(maxtime.timestamp())
                        # print('relayout_maxrange', relayout_maxrange)
                        # print('threshold', threshold)
                        
                        if relayout_maxrange:
                         
                            # when the reset of maximal range exceeds a threshold value, the range maximum is assigned as maxtime_updated
                            # print(relayout_maxrange)
                            if relayout_maxrange > threshold or now_maxrange > maxtime:
                                
                                # print(maxtime)
                                maxtime_updated = (maxtime + timedelta(seconds=300)).strftime("%Y-%m-%d %H:%M:%S")
                                # print(maxtime_updated)
                                # print(relayout['xaxis.range[0]'])
                                if 'xaxis.range[1]' in relayout:
                                    the_range = [relayout['xaxis.range[0]'], maxtime_updated]
                                    figure['layout']['xaxis']['range'] = the_range
                                elif 'xaxis.range' in relayout:
                                    the_range = [relayout['xaxis.range'][0], maxtime_updated]
                                    figure['layout']['xaxis']['range'] = the_range
                                
                                # print(the_range)
                            else:
                                if 'xaxis.range[1]' in relayout:
                                    figure['layout']['xaxis']['range'] = [relayout['xaxis.range[0]'],
                                                                          relayout['xaxis.range[1]']]
                                elif 'xaxis.range' in relayout:
                                    figure['layout']['xaxis']['range'] = [relayout['xaxis.range'][0],
                                                                         relayout['xaxis.range'][1]]
                        
                        
                        # y range 
                        if 'yaxis.range[1]' in relayout and 'yaxis.range[0]' in relayout:
                                figure['layout']['yaxis']['range'] = [relayout['yaxis.range[0]'],
                                                                      relayout['yaxis.range[1]']]
                        elif 'yaxis.range' in relayout:
                             figure['layout']['yaxis']['range'] = [relayout['yaxis.range'][0], 
                                                                      relayout['yaxis.range'][1]] 

                    if do_autoscale:
                        figure['layout']['xaxis']['autorange'] = True
                
                return figure, dis
            
            else: no_update, no_update
        else:
            return no_update, no_update
    else:
        # to keep same format for single channel or multiple channels
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
                    data_df = pd.concat([data_df, temp_df], axis=0)

            if selected_dropdown_value is not None or not selected_dropdown_value:
                for channel in selected_dropdown_value:
                    channel_time = 'Time_'+ channel

                    # if data_df[channel_time].iloc[0] == str:

                    # drop all NaN
                    if channel in data_df:
                        temp = pd.DataFrame()
                        temp[channel] = data_df[channel]
                        temp[channel_time] = data_df[channel_time]
                        temp.dropna(inplace=True)

                        trace.append(
                            go.Scatter(x=temp[channel_time], y=temp[channel], mode='lines', opacity=0.7, name=channel,
                                    textposition='bottom center'))

                        dis.append(
                            html.H6('{0} : {1}'.format(channel, temp[channel].iloc[-1]), style={'margin-top': '3px'}))

                
                # overlap display
                if display_mode_value == 'overlap':
                    figure = {'data': trace, 'layout': layout_set1}
                    figure['layout'].update(uirevision= click)

                # time slider 
                elif display_mode_value == 'timeslider':
                    figure = {'data': trace, 'layout': layout_set2}
                    figure['layout'].update(uirevision=click)
                
                # separate dislay
                elif display_mode_value == 'separate':
                    num =  len(selected_dropdown_value)
                    figure = tools.make_subplots(rows=num, cols=1)
    
                    for index, (tra, chan) in enumerate(zip(trace, selected_dropdown_value)):     
                        figure.append_trace(tra, index+1, 1)
                        figure['layout']['xaxis{}'.format(index+1)].update(title='The channel of {0}'.format(chan)) 

                    figure['layout'].update(height=500*num)
                    figure['layout'].update(uirevision= click)

                return figure, no_update
            else: 
                return no_update, no_update
        else:
            return no_update, no_update
        
        

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

 
# df = pd.DataFrame()
# if before_data is not None:
#     for key, value in before_data.items():
#         before_df = pd.read_json(value, orient='split')
#         df = pd.concat([df, before_df], axis=0, sort=True)

#     # create empty trace     
#     trace = []
#     # to keep same format for single channel or multiple channels
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
