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

import dash # latest version 1.0.0
from dash import no_update
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from plotly import tools
import dash_table
import dash_daq as daq

from data import *


app = dash.Dash(__name__)

# external CSS
# https://cdnjs.cloudflare.com/ajax/libs/normalize/7.0.0/normalize.min.css
# https://codepen.io/chriddyp/pen/bWLwgP.css
# app.css.append_css({'external_url': 'https://rayonde.github.io/external_css/stylesheet.css'})  

app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

server = app.server
CORS(server)
####################################################################################
# Attributes
#
#
#
####################################################################################
global path_lab
global path_user
path_lab = r"C:\Users\YIFAN\Documents\GitHub\LOGS"

path_user = r"C:\Users\YIFAN\Documents\GitHub\LOGS"

color_list = ["#5E0DAC", '#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056']


initial_end_date = date.today()
initial_start_date = date.today()
min_date = date.today()
max_date = date.today()
initial_month = date.today()

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
####################################################################################
# General Functions
#
#
#
####################################################################################
def str_to_datetime(a):
    b = None
    try:
        b = datetime.strptime(a,"%Y-%m-%d %H:%M:%S")
    except:
        try:
            b = datetime.strptime(a,"%Y-%m-%d %H:%M:%S.%f")
        except:
            pass
    return b

def update_jsonfile(path, key, value, valuetype=str):
    # if not exist, create an empty json file 
    if not os.path.isfile(path):
        with open(path, 'w',  encoding='utf-8') as jsonfile:
            jsonfile.write(json.dumps({}))
    
    # Open the JSON file for reading
    with open(path, 'r+',  encoding='utf-8') as jsonfile:
        try:
            data = json.load(jsonfile) 
            # update data
        except:
            print(path)
    
        if key in data.keys():
            if valuetype is str:
                if value not in data[key]:
                    data[key].append(value)
            elif valuetype is dict:
                data[key].update(value)
            elif valuetype is list:
                for ele in value:
                    if ele not in data[key]:
                        data[key].append(ele)
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
    return None

def write_channels_config(path):
    try:
        date_list = get_folder_names(all_folder_paths(path))
    except FileNotFoundError as error:
        print(error)
        print('Cannot get the year list')
    else:

        i = 0
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
            

            update_jsonfile(path + r'\channels.json', single_date_str, list(channels_update), valuetype=list)
            
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
       
####################################################################################
# Layout Functions
#
#
#
####################################################################################

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
    return html.Div([
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
            ],className="modal-container",  id="modal-container", style={"display": "none"},
            )
        
# the row element of data display
def build_value_setter_line(icolor, channel, num, unit, vmin, vmax, precisioninput=True):
    if num > 10000 or num <0.001:
        precisioninput = True
    else:
        precisioninput = False

    if precisioninput ==True: 
        element_num = html.H6("{0:.5E}".format(num),id='value_{}'.format(channel),style={'width':'50%','float':'left'})
    else:
        element_num = html.H6(num,id='value_{}'.format(channel),style={'width':'50%','float':'left'})
    
    return html.Div(
        id='framework_{}'.format(channel),
        children=[
            element_num,
            html.P(unit, id='unit_{}'.format(channel),style={'width':'40%','float':'right'}),

            daq.Indicator(id='indicator_{}'.format(channel), value=True, color=icolor,style={'width':'15%','float':'left' } ),   
            html.P(channel,style={'font-weight': 'bold','width':'80%','float':'left'}),
        ],
        className='mini_container',
        style={'width':'19%', 'float':'left'}
    )

# a row of elements
def live_data_div(dic, data):
    number = len(data.keys())
    num_row = int(number/4) + 1
    rest = number%4
    row = [[None for i in range(4)] for j in range(num_row)]
    content = []
    keys_list = [i for i in dic.keys() if i in data.keys()]
     
    for num, channel in enumerate(keys_list):
        if dic[channel]['min']<= data[channel] and data[channel] <=dic[channel]['max']:
            color = "#00cc96"
        else:
            color = "#FE5C5C"
        
        row[int(num/4)][num%4]=(build_value_setter_line(color, channel, data[channel], dic[channel]['unit'],dic[channel]['min'],dic[channel]['max'], precisioninput=True))
        
    for i in range(num_row):
        content.append(html.Div(children = row[i],className = 'row', ))

    div = html.Div(id = 'data-content', 
                 children = content,)
    return div

# the row element of data display
def build_line(name, value, precisioninput=True):
    if value > 10000 or value <0.001:
        precisioninput = True
    else:
        precisioninput = False

    if precisioninput ==True: 
        element_num = html.H6('{:.5E}'.format(value))
    else:
        element_num = html.H6(value)
    
    return html.Div(
        id='max_min_framework_{}'.format(name),
        children=[
            element_num,
            html.P('{} value'.format(name)),
        ],
        className='mini_container',
        style={'width':'19%', 'float':'left'}
    )

def max_min_div(channel, data):
    vmax = data[channel]['max']
    vmin = data[channel]['min']
    content = [html.Div(children = build_line('Max', vmax,)), html.Div(children = build_line('Min', vmin,))]
    div = html.Div(id = 'max-min-content', children = content)
    return div









def get_data_configuratin(path, dic) :
    if os.path.isfile(path + r'\channels_threshold.json'): 
        pass
    else:
        update_data_configuration(path, dic)
    # read channel config file
    with open(path + r'\channels_threshold.json',  encoding='utf-8') as jsonfile:
        dic_config = json.load(jsonfile)
        

    for i in [i for i in dic.keys() if i not in dic_config.keys()]:
        update_jsonfile(path + r'\channels_threshold.json',i, dic[i], valuetype=dict)

    with open(path + r'\channels_threshold.json',  encoding='utf-8') as jsonfile:
        dic_config = json.load(jsonfile)

    return dic_config
    
def update_data_configuration(path, dic):
    for key in dic.keys():
        update_jsonfile(path + r'\channels_threshold.json',key, dic[key], valuetype=dict)

def display_subplot():
    return  html.Div([
                dcc.Graph(id='subplot-graph')
            ],
            )


####################################################################################
# Layout 
#
#
#
####################################################################################
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
        dcc.Store(id='live_data', storage_type='memory'),
        dcc.Store(id='max_min_data', storage_type='memory'),
        dcc.Store(id='live-data-configuration', storage_type='memory'),
        
        # dcc.Store(id='experiments-storage',storage_type='session'),
        # dcc.Store(id='years-storage',storage_type='session'),
        dcc.Store(id='channels-storage',storage_type='session'),
        dcc.Store(id='exp_info',storage_type='session'),
        dcc.Store(id='user_info',storage_type='session'),
    ], id = 'cache'
    ),
    
    modal(),
    html.Div([
        ], className="modal-backdrop", id="modal-backdrop", style={'display': 'none'}
    ),

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
                html.Div([
                    html.P('Experiment:',style={'font-weight': 'bold'}),
            ], className= 'droptitle' ,style={"width": "90px" , "padding": 5,"float": "left", }
                ),
                html.Div([
                    dcc.Dropdown( id ='experiment',
                    #options=[{'label': i, 'value': i} for i in experiments_auto],
                    multi=False,
                    #value= experiments_auto[0],
                    ),
                ], className= 'dropcontent', style={"width": "100%"}
                ), 
            ], id='experiment-framework',className='four columns',style={"display": "flex","flex-direction": "row",}   
            ),
        
            html.Div([
                html.Div([
                    html.P('Year:',style={'font-weight': 'bold'}),
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
            ], id='years-framework', className='four columns',style={"display": "flex","flex-direction": "row",}   
            ),

            html.Div([
                html.Div([
                    html.P("Scale:", style={'font-weight': 'bold'}),
                ], className= 'droptitle' ,style={ "width": "80px","padding": 5,"float": "left", }
                ), 
                html.Div([
                    dcc.DatePickerRange(id='date_range',
                                end_date = initial_end_date,
                                start_date = initial_start_date,
                                min_date_allowed=min_date,
                                max_date_allowed=max_date,
                                initial_visible_month=initial_month,
                    ),
                ], className= 'dropcontent', style={"width": "100%"}
                ), 
                ],id='range_framework', className='four columns',style={"display": "flex","flex-direction": "row",}   
            ),
                
        ],className='row' , style={"display": "flex","flex-direction": "row",'margin-top': 5, 'margin-bottom': 5,}
        ),

        html.Div([     
            html.Div([
                html.P('Channel:', style={'font-weight': 'bold'}),
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
    ], className= 'pretty_container row'),
    


    html.Div([
        html.Div([
            
            html.Div(
                    id="div-data-display", 
                    style={'width': '100%', 'margin-bottom': '15px','display':'none'},
            ),

            html.Div([
                dcc.Graph(id='temperature-graph')
            ], className="pretty_container",
               style={'width': '100%', 'margin-bottom': '15px'},
            ),
            
            

            html.Div([
                html.Div(id="max-min-display",className="row",style={'width': '100%','margin-bottom': '15px'}),
                
                html.Div([
                    dcc.Graph(id='subplot-graph')
                ], className="pretty_container",
                )
            ],id='subplot-graph-framework',
              style={'width': '100%','margin-bottom': '15px', 'display': 'none'}
            ),

            
            html.Div([
                    html.Div([
                        dcc.Dropdown(
                            id="selection-subplot",
                            options=[],
                            value='',
                            multi = False,
                        )
                    ],style={'width': '20%','float': 'left', 'margin-right': '15px','display': 'block'}
                    ),
                    
                    html.Div([
                        html.Button('Show Subplot',n_clicks = 0, id='subplot-graph-button',)
                    ],style={'float': 'left'}),
            ], className="row", style={'width': '100%',  'margin': '15px'}
            ),

        
        ],id='graph_framework', className ='eight columns',style={'display': 'block'}),

        html.Div([
            html.Div([

                html.Div([   
                    html.Span('Add Configuration',
                            id="new_configuration",
                            n_clicks=0,
                            className="button button-primary",
                            style= {'width': '100%'}
                    )
                ],style={'width': '100%', 'margin-bottom': '15px' }
                ),
                
                html.Div([
                    dcc.Dropdown(
                        id="selection_config",
                        options=[],
                        value=''
                    )
                ],style={'width': '100%', 'margin-bottom': '15px' }
                ),

                html.Div([
                    html.Span( 'Update config files',
                                id="reset_config",
                                n_clicks=0,
                                className="button",
                                style= {'width': '100%'}
                    ),
                ],style={'width': '100%', 'margin-bottom': '15px' }
                ),
            ], className="pretty_container",
            ),
                   
            html.Div([
                
                html.P("Real-time Data display:", style={'font-weight': 'bold', 'margin-bottom': '10px'}),
                
                html.Div([
                     html.Span('Real-time data', 
                                id='data-set', 
                                n_clicks=0,
                                className= 'button button-primary', 
                                style= {'width': '100%'})
                ],style={'width': '100%', 'margin-bottom': '15px' }
                ),

                html.Div([
                     html.Span('Store Data Config', 
                                id='store-data-config', 
                                n_clicks=0,
                                className= 'button', 
                                style= {'width': '100%', 'display': 'none'})
                ],style={'width': '100%', 'margin-bottom': '15px' }
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
                ], style={'width': '100%', 'margin-bottom': '15px' }
                ),
            ], className="pretty_container",
            ),

            html.Div([

                html.Div([
                    html.Button('Autoscale', 
                                    id='autoscale', 
                                    n_clicks=0,
                                    style= {'width': '100%'})
                ], style={'width': '100%', 'margin-bottom': '15px' }
                ),


                html.Div([
                    html.P("Plot Display mode:", style={'font-weight': 'bold', 'margin-bottom': '10px'}),

                    dcc.RadioItems(
                        options=[
                            {'label': ' Overlap', 'value': 'overlap'},
                            {'label': ' Timeslider', 'value': 'timeslider'},
                        ],
                        value='overlap',
                        id='display_mode'
                    ),
                ], style={'width': '100%', 'margin-bottom': '15px' }
                ),

                html.Div([
                    html.P("Number of data points in cache:", style={'font-weight': 'bold', 'margin-bottom': '10px'}),
                    
                    html.Div(id="div-num-display")

                ],style={'width': '100%', 'margin-bottom': '15px' }
                ),
                
            ], className="pretty_container",
            ),
        ],id='select_framework', className ='four columns', style={
                            'display': 'inline-block',
                            'float': 'right',}
        )
    ],className='row', style={'margin-top': 5, 'margin-bottom': 5,}
    ),     
],id ='page', className='ten columns offset-by-one',style={"display": "flex", "flex-direction": "column"},
)

# Create app layout
# Describe the layout, or the UI, of the app
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    page1,
])

####################################################################################
# Layout Display Callback
#
#
#
####################################################################################
# hide/show modal
@app.callback(Output("modal-container", "style"), 
            [Input("new_configuration", "n_clicks"),])
def display_configuration_modal_callback(n):
    if n > 0:
        return {"display": "inline"}
    return {"display": "none"}

@app.callback(Output("modal-backdrop", "style"), 
            [Input("new_configuration", "n_clicks"),])
def display_configuration_modal_callback(n):
    if n > 0:
        return {"display": "inline"}
    return {"display": "none"}

# reset to 0 add button n_clicks property
@app.callback(
    Output("new_configuration", "n_clicks"),
    [Input("configuration_modal_close", "n_clicks"),
    Input("submit_new_configuration", "n_clicks"),],)
def close_modal_callback(n, n2):
    return 0

# reset to 0 submit button n_clicks property
@app.callback(
    Output("submit_new_configuration", "n_clicks"),
    [Input("configuration_modal_close", "n_clicks"),],
    [State("submit_new_configuration", "n_clicks")])
def close_modal_callback(n, n2):
    return 0

#####################################
# Get static CSS
@app.server.route('/static/<path:path>')
def static_file(path):
    static_folder = os.path.join(os.getcwd(), 'static')
    return send_from_directory(static_folder, path)

####################################################################################
# Configuration Callback
#
#
#
####################################################################################
# Configuration data
@app.callback([Output('new_configuration_exp', 'options'), 
               Output('new_configuration_exp', 'value')],
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
              [Input('new_configuration_exp', 'value'),], 
              [State('exp_info','data')])
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
              Input('new_configuration_year', 'value')],
              [State('date_range', 'start_date'),
              State('date_range', 'end_date')],)
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
        with open(path + r'\channels.json',  encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)     
        
        # search all channels in the date interval
        for date in data.keys():
            channels_update.update(set(data[date]))
        
        channels_update = list(channels_update)

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
def new_configuration(n, data, name, exp, year, mode, figure, path, channels):
    if n>0:
        data = {} 
        data['name'] = name
        data['experiment'] = exp
        data['year'] = year
        data['mode'] = mode
        data['figure'] = figure
        data['path'] = path
        data['channels'] = channels
        update_jsonfile(path_user + r'\user.json', name, data, valuetype=dict)
        
        options = []
        with open(path_user + r'\user.json',  encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            options = [{'label': i, 'value': i} for i in data.keys()]
        return options
    elif n==0: 
        with open(path_user + r'\user.json',  encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            options = [{'label': i, 'value': i} for i in data.keys()]
        return options

####################################################################################
# Data Callback
#
#
#
####################################################################################
# Get the experiment information 
@app.callback(Output('exp_info','data'),
              [Input('interval-info-update', 'n_intervals'),
              Input('reset_config', 'n_clicks'),],
              [State('selection_config', 'value'),])
def update_exp_info(n_intervals, reset_click, value):
    # if reset new configuration, update 'path_lab'
    if value and reset_click>0: 
        global path_lab
        with open(path_user + r'\user.json', 'r') as json_file:
            data = json.load(json_file)
        
        if data and data[value]['path'] and path_lab !=  data[value]['path']:
            path_lab = data[value]['path']
            n_intervals = 0
            
    # 0: the first implementation
    if n_intervals is 0:
        # read exp information
        if os.path.isfile(path_lab + r'\exp_info.json'):
            pass
        
        # create exp information 
        else:
            write_info(path_lab)
        
        with open(path_lab + r'\exp_info.json', 'r',  encoding='utf-8') as json_file:
            data = json.load(json_file)       
        return data
    else: 
        return no_update

        
# Get the experiment list automatically every 24h
@app.callback([Output('experiment', 'options'),
               Output('experiment', 'value')],
              [Input('exp_info','data'), 
               Input('reset_config', 'n_clicks')],
              [State('selection_config', 'value')])
def update_experiments(info, reset_click, value):
    exp_options = no_update
    exp = no_update
     
    if info:  
        experiments = info['experiments']
        exp_options = [{'label': i, 'value': i} for i in experiments]
        exp = experiments[0]

    if value and reset_click>0: 
        with open(path_lab + r'\user.json', 'r') as json_file:
            data = json.load(json_file)

        if value in data.keys() and data[value]['experiment']:
            exp = data[value]['experiment']

    return exp_options, exp

###########################################
# Get year list automatically
@app.callback([Output('year', 'options'),
              Output('year', 'value'),],
              [Input('experiment', 'value'), 
              Input('exp_info','data'),
              Input('reset_config', 'n_clicks')],
              [State('selection_config', 'value')])
def update_years(exp, info, reset_click, value):
    year_options = no_update
    year = no_update
    
    if exp and info:
        years_update = info['years'][exp] 
        year_options = [{'label': i, 'value': i} for i in years_update]
        year = years_update[-1]
        
    if value and reset_click>0: 
        with open(path_lab + r'\user.json', 'r') as json_file:
            data = json.load(json_file)
        
        if data[value]['year']:
            year = data[value]['year']
            
    return year_options, year
    
############################################
@app.callback([Output('channels_dropdown', 'options'),
               Output('channels_dropdown', 'value'),
              Output('channels-storage','data')],
              [Input('experiment', 'value'),
              Input('year', 'value'),
              Input('date_range', 'start_date'),
              Input('date_range', 'end_date'),
              Input('reset_config', 'n_clicks')],
              [State('selection_config', 'value')])
def update_channels(exp, year, start_date, end_date,reset_click, value):
    # By default
    options = no_update
    channels_selected = no_update
    data_returned = no_update
    data_user = None
    data_channel = {}
    
    
    if value and reset_click>0: 
        with open(path_lab + r'\user.json', 'r') as json_file:
            data_user = json.load(json_file)
        
        exp = data_user[value]['experiment']
        year = data_user[value]['year']

    if exp and year:    
        path = path_lab + '\\' + exp + r'\data' + '\\' + year
        channels_update = set()
        data_channel = {'experiment': exp}
        
        # the date interval
        try:
            end_date_td = datetime.strptime(end_date,r'%Y-%m-%d')
            start_date_td = datetime.strptime(start_date, r'%Y-%m-%d')
        except TypeError as error:      
            print(error)
            print("Start day and end day have wrong filetype.")
        else:
            date_list_td = datelist(start_date_td, end_date_td) # timedate type
        
        # check if there is channels configuration file
        if os.path.isfile(path + r'\channels.json'): 
            pass
        else:
            # reset the channel config file
            write_channels_config(path)  
        
        # read channel config file
        with open(path + r'\channels.json',  encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)     

        # search all channels in the date interval
        for date in date_list_td:
            single_date_str = date.strftime(r'%y-%m-%d')
            if single_date_str in data.keys():
                channels_update.update(set(data[single_date_str]))
            else: 
                write_channels_config(path)
                if single_date_str in data.keys():
                    channels_update.update(set(data[single_date_str]))

        channels_update = list(channels_update)
        data_channel.update({'channels': channels_update})
        
        options = [{'label': i, 'value': i} for i in channels_update]
        channels_selected = channels_update
        
       
        if value and reset_click>0: 
            channels_selected = data_user[value]['channels']
    
    return options, channels_selected, data_channel



@app.callback(Output('selection-subplot', 'options'),
              [Input('channels_dropdown', 'options'),])
def update_selection_subplot(options):
    if options:
        return options
    else: 
        return no_update

@app.callback(Output('selection-subplot', 'value'),
              [Input('reset_config', 'n_clicks')],
              [State('selection_config', 'value')])
def update_selection_value(reset_click, value):
    sub_channel = no_update
    
    if value and reset_click>0: 
        with open(path_lab + r'\user.json', 'r') as json_file:
            data = json.load(json_file)
            
        if data[value]['channels']:
            channels = data[value]['channels']
            sub_channel = channels[0]
    
    return sub_channel
    


# Get effective date range 
@app.callback([Output('date_range', 'min_date_allowed'),
                Output('date_range', 'max_date_allowed'),
                Output('date_range', 'initial_visible_month'),
                Output('date_range', 'start_date'),
                Output('date_range', 'end_date'),],
               [Input('experiment', 'value'),
               Input('year', 'value'),
               Input('reset_config', 'n_clicks')],
               [State('selection_config', 'value')])
def update_date_range(exp, year, reset_click, value):
    if exp and year: 
        path = path_lab + '\\' + exp + r'\data' + '\\' + year
        dates = []
        
        if os.path.isfile(path + r'\channels.json'): 
            pass
        else:
            # reset the channel config file
            write_channels_config(path)  
        
        # read channel config file
        with open(path + r'\channels.json',  encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)    
        
        for date in data.keys():
            dates.append(datetime.strptime(date,r'%y-%m-%d'))

        min_date =min(dates)
        max_date = max(dates)

        if value and reset_click>0: 
            with open(path_lab + r'\user.json', 'r') as json_file:
               data = json.load(json_file)
            
            if data[value]['mode'] and data[value]['mode'] == "Live mode":
                max_date = datetime.today().date()

        return min_date, max_date, max_date, max_date, max_date
    else:
        return no_update, no_update, no_update, no_update, no_update

# Callback the update mode 
@app.callback(Output('dropdown-interval-control', 'value'),
                [Input('date_range', 'start_date'),
                 Input('date_range', 'end_date'),
                 Input('reset_config', 'n_clicks')],
                 [State('selection_config', 'value')])
def storage_mode(start_date, end_date, reset_click, value):
    try:
        end_date = datetime.strptime(end_date,r'%Y-%m-%d')
        start_date = datetime.strptime(start_date, r'%Y-%m-%d')
    except TypeError as error:      

        print("Start day and end day have wrong filetype.")

    # Select record mode
    update_speed = 'no' 
    if end_date.date() < datetime.today().date():
        print('The update is needless for the data selected.' )
        update_speed = 'no' 
    else: 
        update_speed = 'regular'  
    
    if value and reset_click>0: 
        with open(path_lab + r'\user.json', 'r') as json_file:
            data = json.load(json_file)
        
        if data[value]['mode']:
            if data[value]['mode'] == "Live mode":
                update_speed = 'regular' 
            elif data[value]['mode'] == "No update":
                update_speed = 'no' 
    
    return update_speed

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

# Display the store button
@app.callback([Output('div-data-display', 'style'),
                Output('store-data-config', 'style'),
                Output('data-set', 'children')],
                [Input('data-set', 'n_clicks')],
                [State('store-data-config', 'style')])
def stop_production(n, current):
    if n>0:
        if current['display'] =='none':
            return {'display': 'block'}, {'display': 'block'}, 'Close Data Display'
        elif current['display'] =='block':
            return {'display': 'none'}, {'display': 'none', 'background-color': '#FE5C5C',
  'border-color':'#FE5C5C'}, 'Real-time data'
        else:
            return no_update, no_update, no_update
    else:
        return no_update, no_update, no_update

# Store the live data configuration (threshold, unit) 
@app.callback(Output('live-data-configuration', 'data'),
              [Input('data-set', 'n_clicks'), 
               Input('experiment', 'value'),
               Input('year', 'value')],
              [State('live_data', 'data'),])
def data_configuration(title, exp, year, data):

    if exp and year and data:
        path = path_lab + '\\' + exp + '\\data' + '\\' + year
        
        if 'experiment' in data.keys() and  data['experiment'] == exp:
            
            # delete {'expriment'}
            data.pop('experiment', None)
            # the inital setting
            dic = {}

            for key in data.keys():
                dic[key]={'unit':'', 'min':data[key], 'max':data[key]}

            dic_config = get_data_configuratin(path, dic)

            return dic_config 
        else:
            return no_update
    else:
        return no_update


# Update the real-time data
@app.callback(Output('div-data-display', 'children'),
              [Input('live_data', 'data'),],
              [State('live-data-configuration', 'data')])
def data_display(data, dic_config):
    
    if dic_config:
        if data and 'experiment' in data.keys():
            data.pop('experiment', None)
            
            return live_data_div(dic_config, data)
        else: 
            return no_update
    else:
        return no_update


# Dash can't have the same Input and Output
# Save the data as json file in cache
@app.callback([Output('before-log-storage', 'children'),
               Output('num-before-storage','data'),],
                  [Input('date_range', 'start_date'),
                  Input('date_range', 'end_date'),
                  Input('channels-storage', 'data'),],
                 [State('experiment', 'value'),
                  State('year', 'value'),
                  State('before-log-storage', 'children'),
                  State('num-before-storage','data'),])
def get_before_log(start_date, end_date, data_channel, exp, year,  before, num_before):

    if exp and year and end_date and start_date and data_channel:
        if data_channel['experiment'] ==exp:
            
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
            
            if end_date.date() != datetime.today().date():
        
                is_clear_data = False
                date_update = []
                # if before is None(empty)
                
                if not before:
                    date_update = date_list
                   
                # the previous 'before' stores the same experiment as the selected
                elif before and 'exp_before' in before and exp == before['exp_before']:
                    date_list_old = list(before.keys())
                    
                    # remove the key indicating the experiment name
                    if 'exp_before' in date_list_old:
                        date_list_old.remove('exp_before')
                    if 'exp_today' in date_list_old:
                        date_list_old.remove('exp_today')
                        
                    # convert 'date_list_old' in datetime type
                    if  date_list_old:
                        date_list_temp = []
                        for date in date_list_old:
                            date_list_temp.append(datetime.strptime(date, r'%Y-%m-%d'))
                        date_list_old = date_list_temp

                    # the different dates between two lists
                    date_update = [i.date() for i in date_list if i not in date_list_old]
                    
                
                elif before and 'exp_before' in before and exp != before['exp_before']:
                    is_clear_data = True 
                    date_update = date_list
                
                if  is_clear_data: 
                    before = {}
                    num_before['num_before'] = 0
                else:
                    before = before or {}
                
                if date_update: 
                    # remove today, it will update in another callback
                    if datetime.today().date() in date_update:
                        date_update.remove(datetime.today().date())      
                    
                    # get the channel set from the channel storage
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
                
                        if num_before:
                            num_total = num_before['num_before'] + num_total

                    before.update(cache_dic)
                    before['exp_before'] = exp
                    
                    return before, {'num_before': num_total}
                
                else:
                    return no_update, no_update
            else: 
                return no_update, no_update
        else: 
            return None, None
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
def get_today_log(speed_value, n_intervals, exp, channels, start_date, end_date, today):
    if exp and channels and start_date and end_date:
        
        if channels['experiment'] == exp:
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
                cache_dic = {}

                # get the channel set from the channel storage
                channel_set = channels['channels']   

                today = today or {}
                try:
                    df = get_1day_data_str(datetime.today().date(),channel_set, path)
                except FileNotFoundError as error:      
                    print(error)
                    print("There is no data is placed in the today\'s directory.")
                else: 
                    num =len(df) 
                    json_data = df.to_json(orient='split')
                    cache_dic[today_str] = json_data
                    cache_dic['exp_today'] = exp
                
                today = today or {}
                today.update(cache_dic)
                today['exp_today'] = exp
                return today, {'num_today': num}
            else:
                return no_update, no_update
        else:
            return no_update, no_update
    else:
        return no_update, no_update


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


@app.callback([Output('temperature-graph', 'figure'),
               Output('live_data', 'data')],
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
    start_date = datetime.strptime(start_date, r'%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, r'%Y-%m-%d').date()
    date_list =  [start_date + timedelta(days=x) for x in range((end_date-start_date).days + 1)]

    if end_date == datetime.today().date():   
        if today_data:
            trace = []
            last_data = {}
            if today_data and 'exp_today' in today_data.keys():
                last_data.update({'experiment': today_data['exp_today']})
            
            # read data from json cache
            if before_data:
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
                    temp_df = pd.read_json(before_data[date_str], orient='split', convert_dates =True)
                    data_df = pd.concat([data_df, temp_df], axis=0) 
            

            # selected_dropdown_value is not None or not empty
            if selected_dropdown_value:
                # to keep same format for single channel or multiple channels
                if not isinstance(selected_dropdown_value, (list,)):
                    selected_dropdown_value = [selected_dropdown_value]
                
                maxtime_list = pd.Series()
                mintime_list = pd.Series()
                
                # append each traces
                for channel in selected_dropdown_value:
                    channel_time = channel+'_time'

                    # drop all NaN
                    if channel in data_df:
                        temp = pd.DataFrame()
                        temp[channel] = data_df[channel]
                        temp[channel_time] = data_df[channel_time]
                        temp.dropna(inplace=True)

                        maxtime_list.append(pd.Series(temp[channel_time].iloc[-1]))
                        mintime_list.append(pd.Series(temp[channel_time].iloc[0]))


                        trace.append(go.Scatter(x=temp[channel_time], y=temp[channel],mode='lines', opacity=0.7,name=channel, textposition='bottom center'))
                        last_data[channel] = temp[channel].iloc[-1]
                 
                # the time of last data

                maxtime = datetime.today()
                if not maxtime_list.empty:
                    maxtime = maxtime_list.max()
                if not mintime_list.empty:
                    mintime = mintime_list.max()

                # overlap display
                if display_mode_value == 'overlap':
                    figure = {'data': trace, 'layout': layout_set1}
                
                # time slider 
                elif display_mode_value == 'timeslider':
                    figure = {'data': trace, 'layout': layout_set2}
                
                # keep the zoom 
                if figure:
                    # have attribute 'relayout, the attribute 'range' exists only execute the zoom 
                    if relayout:
                        relayout_maxrange = None
                        # get the relayout x-axis maximum
                        if 'xaxis.range[1]' in relayout or 'xaxis.range' in relayout:
                            try:
                                relayout_maxrange = str_to_datetime(relayout['xaxis.range[1]'])
                            except:
                                relayout_maxrange = str_to_datetime(relayout['xaxis.range'][1])
                        
                        # now_maxrange is the last time or the actual range maximum 
                        if 'xaxis' in figure['layout']:
                            if 'range' in figure['layout']['xaxis']:
                                if figure['layout']['xaxis']['range']:
                                    now_maxrange =  str_to_datetime(figure['layout']['xaxis']['range'][1])
                                else:
                                    now_maxrange = maxtime
                            else:
                                now_maxrange = maxtime

                        elif 'xaxis1' in figure['layout']:
                            temp_now_list = []
                            
                            for index, tra in enumerate(trace):     
                                if 'range' in figure['layout']['xaxis{}'.format(index+1)]:
                                    temp_now =  str_to_datetime(figure['layout']['xaxis{}'.format(index+1)]['range'][1])
                                    temp_now_list.append(temp_now)
                                    
                            now_maxrange = max(temp_now_list)
                        elif maxtime:
                            now_maxrange = maxtime
                        
                        # the threshold of showing the updated data
                        threshold = (maxtime -timedelta(seconds=100))
                        
                        if relayout_maxrange:
                            # 'xaxis.range[0]', ['xaxis.range'][0] mean different types of zoom (zoom on the figure, selection on the timeslider)
                            # when the reset of maximal range exceeds a threshold value, the range maximum is assigned as maxtime_updated
                            # when the 'now_maxrange' always exceeds the last data, then update the 'now_maxrange' to keep a constant distance between the last data and the range maximum
                            
                            if relayout_maxrange > threshold or now_maxrange > maxtime:
                                
                                maxtime_updated = (maxtime + timedelta(seconds=300))
                                if 'xaxis.range[1]' in relayout:
                                    the_range = [relayout['xaxis.range[0]'], maxtime_updated]
                                    figure['layout']['xaxis']['range'] = the_range
                                elif 'xaxis.range' in relayout:
                                    the_range = [relayout['xaxis.range'][0], maxtime_updated]
                                    figure['layout']['xaxis']['range'] = the_range

                            else:
                                if 'xaxis.range[1]' in relayout:
                                    figure['layout']['xaxis']['range'] = [relayout['xaxis.range[0]'],
                                                                          relayout['xaxis.range[1]']]
                                elif 'xaxis.range' in relayout:
                                    figure['layout']['xaxis']['range'] = [relayout['xaxis.range'][0],
                                                                         relayout['xaxis.range'][1]]
                    
                        # reset y-axis range
                        if 'yaxis.range[1]' in relayout and 'yaxis.range[0]' in relayout:
                                figure['layout']['yaxis']['range'] = [relayout['yaxis.range[0]'],
                                                                      relayout['yaxis.range[1]']]
                        elif 'yaxis.range' in relayout:
                             figure['layout']['yaxis']['range'] = [relayout['yaxis.range'][0], 
                                                                      relayout['yaxis.range'][1]] 
                    # autorange when no update
                    if click>0:
                        figure['layout']['xaxis']['autorange'] = True
                
                return figure, last_data
            else: 
                return no_update, no_update
        else:
            return no_update, no_update
    elif before_data: 
        trace = []
        last_data = {}
        if before_data and 'exp_before' in before_data.keys():
            last_data.update({'experiment': before_data['exp_before'] })

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
                temp_df = pd.read_json(before_data[date_str], orient='split', convert_dates =True)
                data_df = pd.concat([data_df, temp_df], axis=0) 

        if selected_dropdown_value is not None and selected_dropdown_value:
            # to keep same format for single channel or multiple channels
            if not isinstance(selected_dropdown_value, (list,)):
                selected_dropdown_value = [selected_dropdown_value]
            
            maxtime_list = pd.Series()
            mintime_list = pd.Series()
                
            # append each traces
            for channel in selected_dropdown_value:
                channel_time = channel+'_time'

                # drop all NaN
                if channel in data_df:
                    temp = pd.DataFrame()
                    temp[channel] = data_df[channel]
                    temp[channel_time] = data_df[channel_time]
                    temp.dropna(inplace=True)

                    maxtime_list.append(pd.Series(temp[channel_time].iloc[-1]))
                    mintime_list.append(pd.Series(temp[channel_time].iloc[0]))

                    trace.append(go.Scatter(x=temp[channel_time], y=temp[channel],mode='lines', opacity=0.7,name=channel, textposition='bottom center'))
                    
                    last_data[channel] = temp[channel].iloc[-1]
            
            # overlap display
            if display_mode_value == 'overlap':
                figure = {'data': trace, 'layout': layout_set1}
                figure['layout'].update(uirevision= click)

            # time slider 
            elif display_mode_value == 'timeslider':
                figure = {'data': trace, 'layout': layout_set2}
                figure['layout'].update(uirevision=click)
            
            return figure, last_data
        else:
            return no_update, no_update
    else:
        return no_update, no_update





# Display the store button
@app.callback([Output('subplot-graph-framework', 'style'),
                Output('subplot-graph-button', 'children')],
                [Input('subplot-graph-button', 'n_clicks'),
                 Input('reset_config', 'n_clicks')],
                [State('subplot-graph-framework', 'style'),
                 State('selection-subplot', 'value'),
                 State('selection_config', 'value')])
def update_subplot(n, reset_click, current, channel, value):
    is_mutiple_plots = False
    if value and reset_click>0: 
        with open(path_lab + r'\user.json', 'r') as json_file:
            data = json.load(json_file)
        
        if data[value]['figure'] and data[value]['figure'] == "Multiple plots":
            is_mutiple_plots = True
    
    if n==1 and channel:
        return {'display': 'block'}, 'Close Subplot' 
    elif n>1 and channel:
        if current['display'] =='none':
            return {'display': 'block'}, 'Close Subplot'
        elif current['display'] =='block':
            return {'display': 'none'}, 'Show Subplot'
        else:
            return no_update, no_update
    
    elif is_mutiple_plots and channel:
        return {'display': 'block'}, 'Close Subplot'
    else:
        return no_update, no_update

@app.callback([Output('subplot-graph', 'figure'),
               Output('max-min-display', 'children')],
            [Input('before-log-storage', 'children'),
            Input('date_range', 'end_date'),
            Input('date_range', 'start_date'),
            Input('today-log-storage', 'children'),
            Input('selection-subplot', 'value'),
            Input('display_mode','value'),
            Input('autoscale','n_clicks'),
            Input('subplot-graph-button', 'n_clicks'),
            Input('subplot-graph', 'relayoutData'),],
            [State('subplot-graph-framework', 'style'),
             State('subplot-graph', 'figure'),
             State('dropdown-interval-control', 'value')])
def update_sub_graph(before_data, end_date, start_date, today_data, selected_dropdown_value, display_mode_value, click, open_close_click, relayout,  current, figure,updated_speed):
    if current['display'] =='none' and (not updated_speed == 'no'):
        return no_update, no_update
    else:
        start_date = datetime.strptime(start_date, r'%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, r'%Y-%m-%d').date()
        date_list =  [start_date + timedelta(days=x) for x in range((end_date-start_date).days + 1)]
        
        if end_date == datetime.today().date():   
            if today_data:
                trace = []
                max_min_data = {}

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
                        temp_df = pd.read_json(before_data[date_str], orient='split', convert_dates =True)
                        data_df = pd.concat([data_df, temp_df], axis=0) 

                # selected_dropdown_value is not None or not empty
                if selected_dropdown_value:
                    
                    maxtime_list = pd.Series()
                    mintime_list = pd.Series()
                    
                    # append each traces
                    channel = selected_dropdown_value
                    channel_time = channel+'_time'

                    # drop all NaN
                    if channel in data_df:
                        temp = pd.DataFrame()
                        temp[channel] = data_df[channel]
                        temp[channel_time] = data_df[channel_time]
                        temp.dropna(inplace=True)

                        maxtime_list.append(pd.Series(temp[channel_time].iloc[-1]))
                        mintime_list.append(pd.Series(temp[channel_time].iloc[0]))
                        trace.append(go.Scatter(x=temp[channel_time], y=temp[channel],mode='lines', opacity=0.7,name=channel, textposition='bottom center'))
                        
                        max_min_data[channel] = {'min': temp[channel].min()}
                        max_min_data[channel].update({'max': temp[channel].max()})
                    
                    # the time of last data
                    maxtime = datetime.today()
                    if not maxtime_list.empty:
                        maxtime = maxtime_list.max()
                    if not mintime_list.empty:
                        mintime = mintime_list.max()

                    # overlap display
                    if display_mode_value == 'overlap':
                        figure = {'data': trace, 'layout': layout_set1}
                    
                    # time slider 
                    elif display_mode_value == 'timeslider':
                        figure = {'data': trace, 'layout': layout_set2}
                    
                    # keep the zoom 
                    if figure:
                        # have attribute 'relayout, the attribute 'range' exists only execute the zoom 
                        if relayout:
                            relayout_maxrange = None
                            # get the relayout x-axis maximum
                            if 'xaxis.range[1]' in relayout or 'xaxis.range' in relayout:
                                try:
                                    relayout_maxrange = str_to_datetime(relayout['xaxis.range[1]'])
                                except:
                                    relayout_maxrange = str_to_datetime(relayout['xaxis.range'][1])
                            
                            # now_maxrange is the last time or the actual range maximum 
                            if 'xaxis' in figure['layout']:
                                if 'range' in figure['layout']['xaxis']:
                                    if figure['layout']['xaxis']['range']:
                                        now_maxrange =  str_to_datetime(figure['layout']['xaxis']['range'][1])
                                    else:
                                        now_maxrange = maxtime
                                else:
                                    now_maxrange = maxtime

                            elif 'xaxis1' in figure['layout']:
                                temp_now_list = []
                                
                                for index, tra in enumerate(trace):     
                                    if 'range' in figure['layout']['xaxis{}'.format(index+1)]:
                                        temp_now =  str_to_datetime(figure['layout']['xaxis{}'.format(index+1)]['range'][1])
                                        temp_now_list.append(temp_now)
                                        
                                now_maxrange = max(temp_now_list)
                            elif maxtime:
                                now_maxrange = maxtime
                            
                            # the threshold of showing the updated data
                            threshold = (maxtime - timedelta(seconds=100))
                            
                            if relayout_maxrange and now_maxrange:
                                # 'xaxis.range[0]', ['xaxis.range'][0] mean different types of zoom (zoom on the figure, selection on the timeslider)
                                # when the reset of maximal range exceeds a threshold value, the range maximum is assigned as maxtime_updated
                                # when the 'now_maxrange' always exceeds the last data, then update the 'now_maxrange' to keep a constant distance between the last data and the range maximum
                                the_range = []
                                if relayout_maxrange > threshold or now_maxrange > maxtime:
                                    
                                    maxtime_updated = (maxtime +  timedelta(seconds=300))
                                    if 'xaxis.range[1]' in relayout:
                                        the_range = [relayout['xaxis.range[0]'], maxtime_updated]
                                    elif 'xaxis.range' in relayout:
                                        the_range = [relayout['xaxis.range'][0], maxtime_updated]
                                
                                elif 'xaxis.range[1]' in relayout:
                                    the_range = [relayout['xaxis.range[0]'], relayout['xaxis.range[1]']]
                                    
                                elif 'xaxis.range' in relayout:
                                    the_range = [relayout['xaxis.range'][0], relayout['xaxis.range'][1]]

                                if the_range: 
                                    figure['layout']['xaxis']['range'] = the_range
                                    
                                    condition = (data_df[channel_time] >= the_range[0]) & (data_df[channel_time]<= the_range[0])
                                    temp_data = data_df[channel][condition]
                                    max_min_data[channel] = {'min': temp_data.max()}
                                    max_min_data[channel] = {'max': temp_data.max()}
                        
                            # reset y-axis range
                            if 'yaxis.range[1]' in relayout and 'yaxis.range[0]' in relayout:
                                y_range = [relayout['yaxis.range[0]'],relayout['yaxis.range[1]']]
                                
                                figure['layout']['yaxis']['range'] = y_range
                                if y_range[0] >  max_min_data[channel]['min']:
                                    max_min_data[channel]['min'] =  y_range[0] 
                                if y_range[1] <  max_min_data[channel]['max']:
                                    max_min_data[channel]['max'] =  y_range[1] 
                            
                            elif 'yaxis.range' in relayout:
                                y_range = [relayout['yaxis.range'][0], relayout['yaxis.range'][1]] 

                                figure['layout']['yaxis']['range'] = y_range
                                if y_range[0] >  max_min_data[channel]['min']:
                                    max_min_data[channel]['min'] =  y_range[0] 
                                if y_range[1] <  max_min_data[channel]['max']:
                                    max_min_data[channel]['max'] =  y_range[1] 
                        # autorange when no update
                        if click>0:
                            figure['layout']['xaxis']['autorange'] = True
                    

                    return figure,max_min_div(channel, max_min_data)
                else: 
                    return no_update, no_update
            else:
                return no_update, no_update
        elif before_data: 
            trace = []
            max_min_data = {}
            
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
                    temp_df = pd.read_json(before_data[date_str], orient='split', convert_dates =True)
                    data_df = pd.concat([data_df, temp_df], axis=0, sort=False) 

            if selected_dropdown_value:
                    
                # append each traces
                channel = selected_dropdown_value
                channel_time = channel+'_time'

                # drop all NaN
                if channel in data_df:
                    temp = pd.DataFrame()
                    temp[channel] = data_df[channel]
                    temp[channel_time] = data_df[channel_time]
                    temp.dropna(inplace=True)

                    trace.append(go.Scatter(x=temp[channel_time], y=temp[channel],mode='lines', opacity=0.7,name=channel, textposition='bottom center'))
                    
                    max_min_data[channel]={'min': temp[channel].min()}
                    max_min_data[channel].update({'max': temp[channel].max()})
                    print(max_min_data)
                # overlap display
                if display_mode_value == 'overlap':
                    figure = {'data': trace, 'layout': layout_set1}
                    figure['layout'].update(uirevision= click)

                # time slider 
                elif display_mode_value == 'timeslider':
                    figure = {'data': trace, 'layout': layout_set2}
                    figure['layout'].update(uirevision=click)
                
                x_range = []
                y_range = []
            
                # maximum and minimum in x-axis relayout
                if 'xaxis.range[1]' in relayout and 'xaxis.range[0]' in relayout:
                    x_range = [relayout['xaxis.range[0]'],relayout['xaxis.range[1]']]
                    
                elif 'xaxis.range' in relayout:
                    x_range = [relayout['xaxis.range'][0], relayout['xaxis.range'][1]] 
                
                if x_range:
                    figure['layout']['xaxis']['range'] = x_range
                    condition = (data_df[channel_time] >= x_range[0]) & (data_df[channel_time]<= x_range[1])

                    temp_data = data_df[channel][condition]
                    max_min_data[channel]['min']=temp_data.min()
                    max_min_data[channel]['max']=temp_data.max()
                elif 'xaxis.autorange' in relayout:
                    figure['layout']['xaxis']['autorange'] = True

                        
                # maximum and minimum in y-axis relayout
                if 'yaxis.range[1]' in relayout and 'yaxis.range[0]' in relayout:
                    y_range = [relayout['yaxis.range[0]'],relayout['yaxis.range[1]']]

                elif 'yaxis.range' in relayout:
                    y_range = [relayout['yaxis.range'][0], relayout['yaxis.range'][1]] 

                if y_range:  
                    figure['layout']['yaxis']['range'] = y_range
                    if y_range[0] >  max_min_data[channel]['min']:
                        max_min_data[channel]['min'] =  y_range[0] 
                    if y_range[1] <  max_min_data[channel]['max']:
                        max_min_data[channel]['max'] =  y_range[1] 
                elif 'yaxis.autorange' in relayout:
                    figure['layout']['yaxis']['autorange'] = True
                
                print('222222222222222222222222')
                print(max_min_data)
                return figure, max_min_div(channel, max_min_data)
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


# # separate dislay
# elif display_mode_value == 'separate':
#     num =  len(selected_dropdown_value)
#     figure = tools.make_subplots(rows=num, cols=1)

#     for index, (tra, chan) in enumerate(zip(trace, selected_dropdown_value)):     
#         figure.append_trace(tra, index+1, 1)
#         figure['layout']['xaxis{}'.format(index+1)].update(title='The channel of {0}'.format(chan)) 

#     figure['layout'].update(height=600*num) 




# @app.callback([Output('temperature-graph', 'figure'),
#                Output('live_data', 'data')],
#             [Input('before-log-storage', 'children'),
#             Input('date_range', 'end_date'),
#             Input('date_range', 'start_date'),
#             Input('today-log-storage', 'children'),
#             Input('channels_dropdown', 'value'),
#             Input('display_mode','value'),
#             Input('autoscale','n_clicks')],
#             [State('temperature-graph', 'figure'),
#              State('temperature-graph', 'relayoutData')])
# def update_graph(before_data, end_date, start_date, today_data, selected_dropdown_value, display_mode_value, click, figure, relayout):
#     start_date = datetime.strptime(start_date, r'%Y-%m-%d')
#     end_date = datetime.strptime(end_date, r'%Y-%m-%d')
#     date_list = datelist(start_date, end_date)
  
#     if end_date.date() == datetime.today().date():   
#         if today_data is not None:
#             trace = []
#             dis = {}

#             # read data from json cache
#             if before_data is not None:
#                 before_data.update(today_data)
#             else:
#                 before_data = today_data
            
#             # The keys of 'before_data' contains the keywords 'exp_before' or 'exp_today' and corresponding years
#             date_log_list = list(before_data.keys())
#             if 'exp_before' in date_log_list:
#                 date_log_list.remove('exp_before')
#             if 'exp_today' in date_log_list:
#                 date_log_list.remove('exp_today')
            
#             data_df = pd.DataFrame()
#             for date in date_list:
#                 date_str = date.strftime(r'%Y-%m-%d')
                
#                 if date_str in date_log_list:
#                     temp_df = pd.DataFrame()
#                     temp_df = pd.read_json(before_data[date_str], orient='split', convert_dates =True)
#                     data_df = pd.concat([data_df, temp_df], axis=0) 

#             # selected_dropdown_value is not None or not empty
#             if selected_dropdown_value is not None and selected_dropdown_value:
#                 # to keep same format for single channel or multiple channels
#                 if not isinstance(selected_dropdown_value, (list,)):
#                     selected_dropdown_value = [selected_dropdown_value]
#                 maxtime_list = []
#                 mintime_list = []

#                 for channel in selected_dropdown_value:
#                     channel_time = channel+'_time'

#                     # drop all NaN
#                     if channel in data_df:
#                         temp = pd.DataFrame()
#                         temp[channel] = data_df[channel]
#                         temp[channel_time] = data_df[channel_time]
#                         temp.dropna(inplace=True)

#                         maxtime_list.append(temp[channel_time].iloc[-1])
#                         mintime_list.append(temp[channel_time].iloc[0])

#                         trace.append(go.Scatter(x=temp[channel_time], y=temp[channel],mode='lines', opacity=0.7,name=channel, textposition='bottom center'))
#                         dis[channel] = temp[channel].iloc[-1]
                 
#                 # the time of last data
#                 # 'pd.to_datetime' converts the time in UTC, so here we use 'datetime.strptime' to keep same format 
#                 maxtime =datetime.today()
#                 if maxtime_list:
#                     max_list =[]
#                     for time in maxtime_list:
#                         max_list.append(datetime.strptime(time, '%Y-%m-%d %H:%M:%S'))
#                     maxtime = max(max_list)
                
#                 if mintime_list:
#                     min_list =[]
#                     for time in mintime_list:
#                         min_list.append(datetime.strptime(time, '%Y-%m-%d %H:%M:%S'))
#                     mintime = max(min_list)

#                 # overlap display
#                 if display_mode_value == 'overlap':
#                     figure = {'data': trace, 'layout': layout_set1}
                
#                 # time slider 
#                 elif display_mode_value == 'timeslider':
#                     figure = {'data': trace, 'layout': layout_set2}
                
                
#                 # keep the zoom 
#                 if figure is not None:
                    
#                     # have attribute 'relayout, the attribute 'range' exists only execute the zoom 
#                     if relayout is not None:
#                         relayout_maxrange = None
#                         # x range maximum
#                         if 'xaxis.range[1]' in relayout or 'xaxis.range' in relayout:
                             
#                             # get the previous range
#                             try:
#                                 maxrange = datetime.strptime(relayout['xaxis.range[1]'],"%Y-%m-%d %H:%M:%S")
#                                 relayout_maxrange = maxrange.timestamp()
#                             except:
#                                 try:
#                                     relayout_maxrange = datetime.strptime(relayout['xaxis.range[1]'],"%Y-%m-%d %H:%M:%S.%f").timestamp()
#                                 except:
#                                     try:
#                                         relayout_maxrange = datetime.strptime(relayout['xaxis.range'][1],"%Y-%m-%d %H:%M:%S").timestamp()
#                                     except:
#                                         relayout_maxrange = datetime.strptime(relayout['xaxis.range'][1],"%Y-%m-%d %H:%M:%S.%f").timestamp()
                        
#                         # the range shown in the figure 
#                         # now_maxrange is the last time or the actual range maximum 
#                         #print(figure['layout'])
#                         if 'xaxis' in figure['layout']:

#                             if 'range' in figure['layout']['xaxis']:

#                                 if figure['layout']['xaxis']['range'] is not None:
#                                     try:
#                                         now_maxrange =  datetime.strptime(figure['layout']['xaxis']['range'][1],"%Y-%m-%d %H:%M:%S")
#                                     except:
#                                         now_maxrange =  datetime.strptime(figure['layout']['xaxis']['range'][1],"%Y-%m-%d %H:%M:%S%f")
#                                 else:
#                                     now_maxrange = maxtime
#                             elif maxtime:
#                                     now_maxrange = maxtime

#                         elif 'xaxis1' in figure['layout']:
#                             temp_now_list = []
#                             for index, tra in enumerate(trace):     
                                
#                                 if 'range' in figure['layout']['xaxis{}'.format(index+1)]:
#                                     try:
#                                          temp_now =  datetime.strptime(figure['layout']['xaxis{}'.format(index+1)]['range'][1],"%Y-%m-%d %H:%M:%S")
#                                     except:
#                                         temp_now =  datetime.strptime(figure['layout']['xaxis{}'.format(index+1)]['range'][1],"%Y-%m-%d %H:%M:%S%f")
#                                     temp_now_list.append(temp_now)
                                    
#                             now_maxrange = max(temp_now_list)
#                         elif maxtime:
#                             now_maxrange = maxtime
                        
#                         # the threshold of showing the updated data
#                         threshold = (maxtime.timestamp()-100)
                        
#                         if relayout_maxrange:
                         
#                             # when the reset of maximal range exceeds a threshold value, the range maximum is assigned as maxtime_updated
#                             # print(relayout_maxrange)
#                             if relayout_maxrange > threshold or now_maxrange > maxtime:
                                
#                                 # print(maxtime)
#                                 maxtime_updated = (maxtime + timedelta(seconds=300)).strftime("%Y-%m-%d %H:%M:%S")
#                                 # print(maxtime_updated)
#                                 # print(relayout['xaxis.range[0]'])
#                                 if 'xaxis.range[1]' in relayout:
#                                     the_range = [relayout['xaxis.range[0]'], maxtime_updated]
#                                     figure['layout']['xaxis']['range'] = the_range
#                                 elif 'xaxis.range' in relayout:
#                                     the_range = [relayout['xaxis.range'][0], maxtime_updated]
#                                     figure['layout']['xaxis']['range'] = the_range
                                
#                                 # print(the_range)
#                             else:
#                                 if 'xaxis.range[1]' in relayout:
#                                     figure['layout']['xaxis']['range'] = [relayout['xaxis.range[0]'],
#                                                                           relayout['xaxis.range[1]']]
#                                 elif 'xaxis.range' in relayout:
#                                     figure['layout']['xaxis']['range'] = [relayout['xaxis.range'][0],
#                                                                          relayout['xaxis.range'][1]]
                        
                        
#                         # y range 
#                         if 'yaxis.range[1]' in relayout and 'yaxis.range[0]' in relayout:
#                                 figure['layout']['yaxis']['range'] = [relayout['yaxis.range[0]'],
#                                                                       relayout['yaxis.range[1]']]
#                         elif 'yaxis.range' in relayout:
#                              figure['layout']['yaxis']['range'] = [relayout['yaxis.range'][0], 
#                                                                       relayout['yaxis.range'][1]] 

#                     if click>0:
#                         figure['layout']['xaxis']['autorange'] = True
                
#                 return figure, dis
#             else: 
#                 return no_update, no_update
#         else:
#             return no_update, no_update
#     elif before_data is not None:
            
#         trace = []
#         dis = {}
        
#         date_log_list = list(before_data.keys())
#         if 'exp_before' in date_log_list:
#             date_log_list.remove('exp_before')
#         if 'exp_today' in date_log_list:
#             date_log_list.remove('exp_today')
                
#         data_df = pd.DataFrame()
#         for date in date_list:
#             date_str = date.strftime(r'%Y-%m-%d')
            
#             if date_str in date_log_list:
#                 temp_df = pd.DataFrame()
#                 temp_df = pd.read_json(before_data[date_str], orient='split')
#                 data_df = pd.concat([data_df, temp_df], axis=0)

#         if selected_dropdown_value is not None and selected_dropdown_value:
#             # to keep same format for single channel or multiple channels
#             if not isinstance(selected_dropdown_value, (list,)):
#                 selected_dropdown_value = [selected_dropdown_value]
            
#             for channel in selected_dropdown_value:
#                 channel_time = channel +'_time'

#                 # if data_df[channel_time].iloc[0] == str:

#                 # drop all NaN
#                 if channel in data_df:
#                     temp = pd.DataFrame()
#                     temp[channel] = data_df[channel]
#                     temp[channel_time] = data_df[channel_time]
#                     temp.dropna(inplace=True)

#                     trace.append(
#                         go.Scatter(x=temp[channel_time], y=temp[channel], mode='lines', opacity=0.7, name=channel,
#                                 textposition='bottom center'))

#                     dis[channel] = temp[channel].iloc[-1]

            
#             # overlap display
#             if display_mode_value == 'overlap':
#                 figure = {'data': trace, 'layout': layout_set1}
#                 figure['layout'].update(uirevision= click)

#             # time slider 
#             elif display_mode_value == 'timeslider':
#                 figure = {'data': trace, 'layout': layout_set2}
#                 figure['layout'].update(uirevision=click)
            
#             return figure, no_update
#         else:
#             return no_update, no_update
#     else:
#         return no_update, no_update