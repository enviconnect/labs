import dash
from dash import Dash, html, Input, Output
from dash import dcc
from dash import dash_table
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc

# --------------------
# Register this page
# --------------------

dash.register_page(__name__,
        title = "Publisher",
        name = "Publisher",
        description ="Information about the website publisher",
        image = "images/explorer.png"
)


def basis():
    basis_element = dbc.Row(
        dbc.Col(
            [
                html.P("Information provided pursuant to § 5 of the TMG (German Telemedia Act):")  
            ]
            )
    )

    return basis_element

def contact():
    contact_element = dbc.Row(
        dbc.Col(
            [
                html.H2("Contact"),
                html.P(
                    [
                        "Email: ",
                        html.A("info@enviconnect.de", href="mailto:info@enviconnect.de")
                    ]
                ),
                html.P(
                    [
                        "Phone: ",
                        html.A("+49 1745 60 20 90", href="tel:00491745602090")
                    ]
                ),
                html.P("Contact via email is preferred.")
            ]
            )
    )

    return contact_element

def VAT():
    VAT_element = dbc.Row(
        dbc.Col(
            [
                html.H2("VAT Registration"),
                html.P("VAT Registration Number pursuant to §27a of the German Value Added Tax Act: DE 194-532-993")
            ]
            )
    )

    return VAT_element

def provider():
    provider_element = dbc.Row(
        dbc.Col(
            [                
                # Service provider
                html.H2("Service Provider"),
                html.P("This website is provided by:"),
                html.P(
                    [
                        "Andrew Clifton",
                        html.Br(),
                        "TGU enviConnect",
                        html.Br(),
                        "TTI – Technologie-Transfer-Initiative GmbH an der Universität Stuttgart (TTI GmbH)",
                        html.Br(),
                        "Nobelstrasse 15",
                        html.Br(),
                        "70569 Stuttgart",
                        html.Br(),
                        "Germany",
                    ]
                ),                
            ]
        )
    )

    return provider_element



layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("Publisher", className="display-3"),                        
                    ]
                )
            ],
        ),
        basis(),
        provider(),
        contact(),
        VAT()
    ],
    class_name="col-12 col-md-9 mt-2",
)
