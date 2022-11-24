import dash
from dash import Dash, html, Input, Output
from dash import dcc
from dash import dash_table
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc

# --------------------
# Register this page
# --------------------

dash.register_page(__name__, path="/")

layout = dbc.Container(
    [
        # title row
        dbc.Row(
            [
                dbc.Col([html.H1("Wind Energy Apps")], width=12),
            ],
            className="title h-10 pt-2 mb-2",
        ),
        # content row
        dbc.Row(
            dbc.Col(
                [
                    dbc.Card(
                        [
                            dbc.CardImg(
                                src="/assets/images/explorer.png", top=True
                            ),
                            dbc.CardBody(
                                [
                                    html.H4(
                                        "Wind Energy R&D Facilities",
                                        className="card-title",
                                    ),
                                    html.P(
                                        "A searchable overview of wind energy R&D facilities",
                                        className="card-text",
                                    ),
                                    html.Div(
                                        [
                                            dbc.Button(
                                                "Go", color="primary", href="explorer"
                                            ),
                                        ],
                                        className="d-grid gap-2 col-6 mx-auto",
                                    ),
                                ]
                            ),
                        ],
                        style={"width": "18rem"},
                    )
                ]
            )
        ),
    ],
    fluid=True,
    className="dbc h-80",
    style={"min-height": "80vh"},
)
