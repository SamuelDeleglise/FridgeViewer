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
trace1 = go.Scatter(
    x=[0, 1, 2],
    y=[10, 11, 12]
)
trace2 = go.Scatter(
    x=[2, 3, 4],
    y=[100, 110, 120],
)
trace3 = go.Scatter(
    x=[3, 4, 5],
    y=[1000, 1100, 1200],
)
fig = tools.make_subplots(rows=3, cols=1, specs=[[{}], [{}], [{}]],
                          shared_xaxes=True, shared_yaxes=True,
                          vertical_spacing=0.001)
fig.append_trace(trace1, 3, 1)
fig.append_trace(trace2, 2, 1)
fig.append_trace(trace3, 1, 1)

fig['layout'].update(height=600, width=600, title='Stacked Subplots with Shared X-Axes')


app.layout = html.Div([
    dcc.Graph(figure=fig, id='my-figure')
])

if __name__ == '__main__':
    app.run_server(debug=True, host='localhost')