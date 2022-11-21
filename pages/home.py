import dash
from dash import Dash, html, Input, Output
from dash import dcc
from dash import dash_table
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc

# --------------------
# Register this page
# --------------------

dash.register_page(__name__, path = "/")

layout = dbc.Container(
[
    html.H1("Home page")

]
)