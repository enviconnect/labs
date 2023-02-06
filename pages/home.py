import dash
from dash import Dash, html, Input, Output
from dash import dcc
from dash import dash_table
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc

# --------------------
# Register this page
# --------------------

dash.register_page(
    __name__,
    path="/",
    title="enviConnect Labs",
    name="enviConnect Labs",
    description="A collection of demo or early-stage software created by us for wind energy applications",
    image="images/explorer.png",
)

layout = dbc.Container(
    [
        # Information row
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("Welcome to enviConnect Labs", className="display-2"),
                        html.P(
                            "enviConnect Labs is where we keep our work in progress.",
                            className="lead",
                        ),
                    ],
                    class_name="col_12 col_md6",
                )
            ]
        ),
        # content row
        dbc.Row(
            [
                # Facilities explorer
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
                                            "R&D Facilities",
                                            className="card-title",
                                        ),
                                        html.P(
                                            "A searchable overview of global wind energy R&D facilities",
                                            className="card-text",
                                        ),
                                        html.Div(
                                            [
                                                dbc.Button(
                                                    "Go",
                                                    color="primary",
                                                    href="explorer",
                                                    className="stretched-link",
                                                ),
                                            ],
                                            className="d-grid gap-2 col-6 mx-auto",
                                        ),
                                    ]
                                ),
                            ],
                            # style={"width": "18rem"},
                        ),
                    ],
                    className="col-12 col-md-4 col-lg-3",
                ),
                # Lidar usage
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardImg(
                                    src="/assets/images/lidar_survey.png", top=True
                                ),
                                dbc.CardBody(
                                    [
                                        html.H4(
                                            "Lidar usage survey",
                                            className="card-title",
                                        ),
                                        html.P(
                                            "Interactive results of a survey about how wind lidar are  used in the wind energy industry",
                                            className="card-text",
                                        ),
                                        html.Div(
                                            [
                                                dbc.Button(
                                                    "Go",
                                                    color="primary",
                                                    href="lidar_usage_survey2023",
                                                    className="stretched-link",
                                                ),
                                            ],
                                            className="d-grid gap-2 col-6 mx-auto",
                                        ),
                                    ]
                                ),
                            ],
                            # style={"width": "18rem"},
                        ),
                    ],
                    className="col-12 col-md-4 col-lg-3",
                ),
                # talk.inductionzone.org
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardImg(
                                    src="/assets/images/inductionzone.png", top=True
                                ),
                                dbc.CardBody(
                                    [
                                        html.H4(
                                            "Induction Zone",
                                            className="card-title",
                                        ),
                                        html.P(
                                            "A community for startups and early adopters in wind energy",
                                            className="card-text",
                                        ),
                                        html.Div(
                                            [
                                                dbc.Button(
                                                    "Go",
                                                    color="primary",
                                                    href="https://talk.inductionzone.org",
                                                    className="stretched-link",
                                                ),
                                            ],
                                            className="d-grid gap-2 col-6 mx-auto",
                                        ),
                                    ]
                                ),
                            ],
                            # style={"width": "18rem"},
                        )
                    ],
                    className="col-12 col-md-4 col-lg-3",
                ),
            ]
        ),
    ],
    fluid=False,
    className="dbc h-80",
    style={"min-height": "80vh"},
)
