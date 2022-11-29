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
    title="Privacy and data protection policy",
    name="Privacy and data protection policy",
    description="Information about how we collect data about our website's users, process it, and protect it.",
    image="images/explorer.png",
)


def basis():

    basis_element = dbc.Row(
        dbc.Col(
            [
                html.P(
                    "This privacy and data protection policy (“Policy”) outlines the personal information that we (“enviConnect”, “we”, “us” or “our”) gathers, how we use that personal information, and the options you have to access, correct, or delete such personal information."
                ),
                html.P(
                    "Note that this policy applies only to the enviConnect Labs pages. Other sites operated by us may have different policies."
                ),
            ]
        )
    )

    return basis_element


def provider():
    provider_element = dbc.Row(
        dbc.Col(
            [
                html.H2("Service Provider", id="service-provider"),
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
                html.P(
                    [
                        "If you have any comments or questions about this website please ",
                        html.A("contact us.", href="mailto:info@enviconnect.de"),
                    ]
                ),
            ]
        )
    )

    return provider_element


def personal_data():

    personal_data_element = dbc.Row(
        dbc.Col(
            [
                html.H2("Personal Data", id="personal-data"),
                html.P(
                    "To offer this website we process data. According to legislation in the EU and elsewhere, some of this data may be considered personal data in that it could directly or indirectly identify a person."
                ),
            ]
        )
    )

    return personal_data_element


def info_we_collect():

    info_we_collect_element = dbc.Row(
        dbc.Col(
            [
                html.H2("Information we collect about you", id="info-collected"),
                html.P(
                    "We collect information in a variety of ways. These are listed below."
                ),
                html.H3("Information you provide"),
                html.P(
                    "You may choose to contact us with questions, comments, or feedback about this site or our business. In that case we will use your contact details to communicate with you on directly related matters."
                ),
                html.H3("Information we collect when you use our services"),
                html.P(
                    "When you use our services we collect very limited data in the form of server logs. These logs include the IP address of clients that have accessed the services. We use this information to help ensure the security of this service."
                ),
                html.H3("Information we collect from Third Parties"),
                html.P("We do not collect information from Third Parties."),
            ]
        )
    )

    return info_we_collect_element


def how_we_use_information():

    how_we_use_info_element = dbc.Row(
        dbc.Col(
            [
                html.H2("How we use information we have collected", id="info-use"),
                html.P(
                    "In order to provide you with the best services and experience, we may use information that we collect about you to:"
                ),
                html.Ul(
                    [
                        html.Li("deliver and improve our products and services;"),
                        html.Li("manage our business; and"),
                        html.Li(
                            "perform functions and services as otherwise described to you at the time of collection."
                        ),
                    ]
                ),
            ]
        )
    )

    return how_we_use_info_element


def retention():
    retention_element = dbc.Row(
        dbc.Col(
            [
                html.H2("Data retention", id="retention"),
                html.P(
                    "We retain the data we collect from you in different ways. These include:"
                ),
                html.Ul(
                    [
                        html.Li(
                            [
                                html.B("Server logs"),
                                " are retained each day until midnight to allow us to monitor and improve site security."
                                ]
                            ),
                        html.Li(
                            [
                                html.B("Contact emails"),                               
                                " are retained indefinitely to allow us to evaluate our performance and our customers' needs."                                
                            ]
                        ),
                    ]
                ),
                html.P(
                    [
                        "You may request the deletion of your information at any time. Please ",
                        html.A("contact us", href="mailto:info@enviconnect.de"),
                        " to request this.",
                    ]
                ),
            ]
        )
    )

    return retention_element


def protection():
    protection_element = dbc.Row(
        dbc.Col(
            [
                html.H2("How we protect your information", id="data-protection"),
                html.P(
                    "We work hard to protect your data from unauthorized access, use, modification, disclosure, or deletion. We take the following measures to protect your data:"
                ),
                html.Ul(
                    [
                        html.Li(
                            [
                                html.B("Administrator access."),
                            " Access to our services on the server side is limited to selected staff who have been trained on our data protection policy."
                            ]
                        ),
                        html.Li(
                            [
                                html.B("Server security."),
                                "We use python anywhere to host this website. We use servers operated by them and located in the European Union."
                            ]
                        ),
                        html.Li(
                            [
                                html.B("Logging."),
                                " We collect server logs to help monitor the traffic to this service for security purposes. We analyse those logs to look for attacks or security risks."
                            ]
                        ),
                        html.Li(
                            [
                                html.B("Regular software updates."),
                                " We aim to keep the software used for this service as up-to-date as possible."
                            ]
                        ),
                    ]
                ),
                html.P(
                    [
                        "We welcome any suggestions to improve our data protection. Please contact ",
                        html.A(
                            "info@enviconnect.de", href="mailto:info@enviconnect.de"
                        ),
                        " with feedback.",
                    ]
                ),
            ]
        )
    )

    return protection_element


def sharing():
    sharing_element = dbc.Row(
        dbc.Col(
            [
                html.H2("How we share your information", id="info-sharing"),
                html.P(
                    "We share limited data with third parties to deliver the services on this website. Under certain legislation these may be considered data processors. These include:"
                ),
                html.Ul(
                    [
                        html.Li(
                            [
                                html.B("Mapbox mapping service. "),
                                "This website uses map information provided by Mapbox, Inc. ('Mapbox', registered at 740 15th Street NW, 5th Floor, Washington DC 20005, United States; ",
                                html.A("mapbox.com", href="https://www.mapbox.com"),
                                ") to generate maps. ",
                                "When you use our services you may be provided with static or interactive maps using their data. As a result your IP address and other limited information may be shared with them. "
                                "We selected mapbox as our mapping provider because we believe their data protection policies conform to relevant data protection legislation in the EU and elsewhere, as described in ",
                                html.A(
                                    "their privacy policy",
                                    href="https://www.mapbox.com/legal/privacy",
                                ),
                                ".",
                                " We consider their service to be essential to the operation of this site.",
                            ]
                        ),
                        # html.Li(
                        #     [
                        #         html.B("Fontawesome icons. "),
                        #         "This website uses icons provided by Fonticons, Inc. ('Fonticons', registered at 307 S Main St Ste 202 Bentonville, AR, 72712-9214 United States; ",
                        #         html.A(
                        #             "fontawesome.com", href="https://fontawesome.com/"
                        #         ),
                        #         ") to help you navigate the site. ",
                        #         "When you use our services you may be provided with icons, that are provided by them through a content delivery network. As a result your IP address and other limited information may be shared with them. "
                        #         "We selected Fonticons as our icon provider because we believe their data protection policies conform to relevant data protection legislation in the EU and elsewhere, as described in ",
                        #         html.A(
                        #             " their privacy policy",
                        #             href="https://fontawesome.com/privacy",
                        #         ),
                        #         ".",
                        #         " We consider their service to be essential to the operation of this site."
                        #     ]
                        # ),
                    ]
                ),
            ]
        )
    )

    return sharing_element


def links():
    links_element = dbc.Row(
        dbc.Col(
            [
                html.H2("External links", id="external-links"),
                html.P(
                    "You may find links to third-party content on our website. We do not control the content on those sites and are not responsible for the content or the data protection policies of those websites. We recommend you read the privacy policies and other terms and conditions of those sites."
                ),
            ]
        )
    )

    return links_element


def cookies():
    # Cookies
    cookies_element = dbc.Row(
        dbc.Col(
            [
                html.H2("Cookies and scripts", id="cookies-scripts"),
                html.P(
                    [
                        html.B("Cookies"),
                        " ",
                        "are small text files that can be generated by web sites to store information on your computer. No cookies are set by this website.",
                    ]
                ),
                html.P(
                    [
                        html.B("Scripts"),
                        " ",
                        "are text files that contain instructions for your browser to carry out certain functions. This site uses some scripts, for example to sort tables. Some of those scripts may have been written by third parties. At this time we host those scripts and deliver them directly to you. We do not deliver any scripts directly from third-parties. All scripts are essential to delivering our services.",
                    ]
                ),
            ]
        )
    )

    return cookies_element


def fonts():

    fonts_element = dbc.Row(
        dbc.Col(
            [
                html.H2("Fonts and design", id="fonts-design"),
                html.P(
                    "We use several third party fonts and design tools to help us deliver this service."
                ),
                html.Ul(
                    [
                        html.Li(
                            [
                                html.B("Bootstrap layout."),
                                " ",
                                "This website uses locally hosted styles and scripts from Bootstrap. This means that they are stored in the website files on our servers and served to you at the time of use (like the text and images). No data is transferred to, or from, Bootstrap to display them to you. These styles and scripts are used under the MIT license. Details about Bootstrap can be found ",
                                html.A("here", href="https://getbootstrap.com/"),
                                ".",
                            ]
                        ),
                        html.Li(
                            [
                                html.B("Fontawesome icons."),
                                " ",
                                "This website uses locally hosted fonts from Font Awesome. This means that they are stored in the website files on our servers and served to you at the time of use (like the text and images). No data is transferred to, or from, Font Awesome to display them to you. The font provider is Fonticons, Inc. ('Fonticons', registered at 307 S Main St Ste 202 Bentonville, AR, 72712-9214 United States). Details about Font Awesome fonts can be found ",
                                html.A("here", href="https://fontawesome.com/"),
                                ".",
                            ]
                        ),
                        html.Li(
                            [
                                html.B("Google Fonts."),
                                " ",
                                "This website uses locally hosted fonts from Google. This means that they are stored in the website files on our servers and served to you at the time of use (like the text and images). No data is transferred to, or from, Google to display them to you. The font provider is Google Inc, 1600 Amphitheatre Parkway, Mountain View, CA 94043, USA (also 'Google'). Details about Google fonts can be found ",
                                html.A(
                                    "here",
                                    href="https://www.google.com/fonts#AboutPlace:about",
                                ),
                                ".",
                            ]
                        ),
                    ]
                ),
            ]
        )
    )

    return fonts_element


def questions():
    questions_element = dbc.Row(
        dbc.Col(
            [
                html.H2("Questions, comments, and feedback", id="contact"),
                html.P(
                    [
                    "We welcome all questions, comments, and feedback. Please contact us at ",                
                    html.A("info@enviconnect.de", href="mailto:info@enviconnect.de"),
                    "."
                    ]
                ),
            ]
        )
    )

    return questions_element


def toc():

    toc_element = dbc.Col(
        [
            html.P("It includes information about:"),
            html.Ul(
                [
                    html.Li(html.A("Service provider", href="#service-provider")),
                    html.Li(
                        html.A(
                            "What we consider to be personal data",
                            href="#personal-data",
                        )
                    ),
                    html.Li(
                        html.A(
                            "Information we collect about you", href="#info-collected"
                        )
                    ),
                    html.Li(html.A("How we use that information", href="#info-use")),
                    html.Li(html.A("Data retention", href="#retention")),
                    html.Li(
                        html.A(
                            "How we protect your information", href="#data-protection"
                        )
                    ),
                    html.Li(
                        html.A("How we share your information", href="#info-sharing")
                    ),
                    html.Li(html.A("External links", href="#external-links")),
                    html.Li(html.A("Cookies and scripts", href="#cookies-scripts")),
                    html.Li(html.A("Fonts and design", href="#fonts-design")),
                    html.Li(
                        html.A("Questions, comments, and feedback", href="#contact")
                    ),
                ]
            ),
        ]
    )

    return toc_element


layout = dbc.Container(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("Privacy and data protection", className="display-3"),
                        html.P(
                            "We take your privacy seriously.",
                            className="lead",
                        ),
                    ]
                )
            ],
        ),
        basis(),
        toc(),
        provider(),
        personal_data(),
        info_we_collect(),
        how_we_use_information(),
        retention(),
        protection(),
        sharing(),
        links(),
        cookies(),
        fonts(),
        questions(),
    ],
    class_name="col-12 col-md-9 mt-2",
)
