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
    external_stylesheets=[#dbc.themes.BOOTSTRAP,
        #dbc.icons.FONT_AWESOME
        ],
    use_pages=True,
    suppress_callback_exceptions=True
)


def create_header_row():
    header =[]

    return header

def create_nav_bar():
    navbar = dbc.Nav(
        [
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
                        href="https://www.enviconnect.de",
                        target="_blank",
                        className="navbar-brand",
                    )
                ],
                className="d-flex flex-grow-1",
            ),
            html.Div([html.P("Labs", className="display-4 school")]),
        ],
        className="navbar-light bg-white px-0 pt-2",
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
                        html.A([
                        html.Img(src=app.get_asset_url('Logo_100H.png'),
                                 style={"max-width": "100%", "height":"35px" },
                                 className="my-2")
                                 ],
                    href="https://www.enviconnect.de",
                    target="_blank"
                    ),
                        html.P(
                            "We're experts in finding and deploying new technologies for wind energy applications"
                        ),
                    ]
                ),
                className="col-12 col-md-3",
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
                ],
                className="col-12 col-md-3",
            ),
        ],
        className="h-md-20 pt-2 footer",
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
                                [html.P("\u00A9 enviConnect 2022")],
                                className="copyright",
                            ),
                        ],
                        className="sub-footer-inner",
                    )
                ],
                className="col-12",
            ),
        ],
        className="sub-footer",
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
            [
                create_nav_bar()
            ],
        ),        
        # content from other pages
        html.Div(
            [
            dash.page_container
            ],
            className="content"
        ),
        # footer
        html.Div(
            [
                create_footer_row(),
            ],
            className="h-20 footer",
        ),
        # subfooter
        html.Div([create_subfooter()], className="h-10 sub-footer"),
        # dcc.Store stores the intermediate value
        # dcc.Store(id='intermediate-value')
    ],
    fluid=True,
    className="dbc h-100",
    style={"min-height": "100vh"},
)


if __name__ == "__main__":
    app.run_server(debug=True)
