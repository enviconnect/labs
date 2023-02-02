# set up Dash
# from jupyter_dash import JupyterDash

from dash import Dash, html, dcc
import dash

import dash_bootstrap_components as dbc


# ---------
# Build App
# ---------

app = Dash(
    __name__,
    use_pages=True,
    prevent_initial_callbacks=True,
    suppress_callback_exceptions=True,
)


def create_header_row():
    header = []

    return header


def create_nav_bar():
    navbar = dbc.Nav(
        [
            # left side
            html.Div(
                [
                    # logo and tagline
                    html.A(
                        [
                            html.Img(
                                src=app.get_asset_url("Logo_100H.png"),
                                style={"max-width": "100%", "max-height": "35px"},
                            ),
                            html.P(
                                "Innovations for wind energy",
                                className="tagline",
                                style={"text-decoration": "none"},
                            ),
                        ],
                        href="/",
                        target="_blank",
                        className="navbar-brand",
                    ),
                    html.A(
                        [html.P("Labs", className="display-4 school")],
                        href="/",
                        style={
                            "text-decoration": "none",
                            "color": "black",
                            "margin-left": "20px",
                        },
                    ),
                ],
                className="d-flex flex-grow-1",
            ),
            # right side
            html.Div(
                [
                    dbc.Button(
                        [
                            html.I(className="fa-solid fa-house"),
                            "  Visit our main website",
                        ],
                        href="".join("https://www.enviconnect.de"),
                        target="_blank",
                        color="primary",
                        disabled=False,
                        className="me-1 btn btn-primary",
                    ),
                ]
            ),
        ],
        className="navbar-light bg-white p-2 pt-4",
    )
    return navbar


def create_footer_row():
    """
    Create the footer layout

    Creates a multi-column footer

    Parameters
    ----------


    Returns
    -------
    footer : Dash HTML object

    """

    footer = dbc.Row(
        [
            dbc.Col(
                html.Div(
                    [
                        html.A(
                            [
                                html.Img(
                                    src=app.get_asset_url(
                                        "Logo_white_colourfulC_100H.png"
                                    ),
                                    style={"max-width": "100%", "max-height": "35px"},
                                    className="mb-2",
                                )
                            ],
                            href="https://www.enviconnect.de",
                            target="_blank",
                        ),
                        html.P(
                            "We're experts in finding and deploying new technologies for wind energy applications"
                        ),
                    ]
                ),
                className="col-12 col-md-3 my-2",
            ),
            dbc.Col([], className="col-12 col-md-3"),
            dbc.Col([], className="col-12 col-md-3"),
            dbc.Col(
                [
                    html.H2("Contact"),
                    html.P(
                        [
                            "TGU enviConnect",
                            html.Br(),
                            "TTI GmbH",
                            html.Br(),
                            "Nobelstrasse 15",
                            html.Br(),
                            "70569 Stuttgart",
                            html.Br(),
                            "Germany",
                        ]
                    ),
                    html.A(
                        ["info@enviconnect.de"],
                        href="mailto:info@enviconnect.de",
                    ),
                    html.A(
                        ["+49 1745 60 20 90"],
                        href="tel:+491745602090",
                    ),
                ],
                className="col-12 col-md-3 my-2",
            ),
        ],
        className="m-0 px-2 pt-2 footer",
    )

    return footer


def create_subfooter():
    """
    Create the sub footer layout

    Creates a multi-column sub footer

    Parameters
    ----------


    Returns
    -------
    sub-footer : Dash HTML object

    """

    subfooter = dbc.Row(
        [
            dbc.Col(
                [
                    html.Div(
                        [
                            # legal
                            html.Div(
                                [
                                    html.A("Publisher", href="/publisher"),
                                    html.A(
                                        "Privacy Policy",
                                        href="/privacy",
                                        style={"margin-left": "10px"},
                                    ),
                                ],
                                className="copyright",
                            ),
                            # copyright notice
                            html.Div(
                                [html.P("\u00A9 enviConnect 2022", className="mb-0")],
                                className="copyright",
                            ),
                        ],
                        className="sub-footer-inner",
                    )
                ],
                className="col-12 py-1",
            ),
        ],
        className="sub-footer m-0 px-2 py-1",
    )

    return subfooter


# -----------------------------
# Create the overall App layout
# -----------------------------

# Create an app with two columns:
# 3 cols on the left for filters, 9 on the right for map & information
app.layout = dbc.Container(
    [
        # nav bar
        html.Div(
            [dbc.Container(create_nav_bar(), fluid=False, className="px-0")],
        ),
        # content from other pages
        html.Div(
            [dbc.Container(dash.page_container, fluid=False, className="px-0")],
            className="content py-2",
            style={"min-height": "50vh"},
        ),
        # footer
        html.Div(
            [dbc.Container(create_footer_row(), fluid=False, className="px-0")],
            className="footer",
        ),
        # subfooter
        html.Div(
            [dbc.Container(create_subfooter(), fluid=False, className="px-0")],
            className="sub-footer",
        ),
    ],
    fluid=True,
    className="dbc p-0 m-0",
    style={"min-height": "100vh"},
)


if __name__ == "__main__":
    app.run_server(debug=True)
    # app.run_server()
