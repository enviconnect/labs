import plotly.express as px
import plotly.graph_objects as go

# set up Dash
#from jupyter_dash import JupyterDash

import dash
from dash import Dash, html, Input, Output
from dash import dcc
from dash import dash_table
from dash.dependencies import Input, Output

import dash_bootstrap_components as dbc

# math routines
import math

# import pyyaml module
import yaml
from yaml.loader import SafeLoader

# import pandas (needed for the data table)
import pandas as pd

# import numpy
import numpy as np

# get domain from URLs
from urllib.parse import urlparse


# --------------------
# Get and prepare data
# --------------------

# Open the file and load the file
with open('data/facilities.yaml') as f:
    data = yaml.load(f, 
                     Loader=SafeLoader)

def prepare_data(data):

    # convert data to a datatable - easier later
    df_in = pd.DataFrame(data["features"])
    df_in.reset_index(inplace=True)


    # explode and join the dictionaries
    df_geom = pd.DataFrame(df_in.pop('geometry').values.tolist())
    df_geom.reset_index(inplace=True)

    df_properties = pd.DataFrame(df_in.pop('properties').values.tolist())
    df_properties.reset_index(inplace=True)
    # pop out the coordinates from the geometry
    df_coordinates = pd.DataFrame(df_geom.pop('coordinates').values.tolist(),
                                columns=["lon","lat","elev"])
    df_coordinates.reset_index(inplace=True)
    # join them
    df = df_geom.join(df_properties.set_index('index'),
                    lsuffix = "_geom",
                    rsuffix= "_property"
                    )

    df = df.join(df_coordinates.set_index('index'))

    # information
    df_information = pd.DataFrame(df_in.pop('information'))
    df_information.reset_index(inplace=True)
    df = df.join(df_information.set_index('index'))

    # infrastructure is a column of lists
    df_infrastructure = pd.DataFrame(df_in.pop('infrastructure'))
    df_infrastructure.reset_index(inplace=True)

    df = df.join(df_infrastructure.set_index('index'))

    # data is a column of lists
    df_availabledata = pd.DataFrame(df_in.pop('availabledata'))
    df_availabledata.reset_index(inplace=True)

    df = df.join(df_availabledata.set_index('index'))

    return df

df = prepare_data(data)

# ---------
# Build App
# ---------

# Define the app using an external stylesheet
# Use https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/ to find stylesheets

# https://hellodash.pythonanywhere.com/adding-themes/dcc-components
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.css"

app = Dash(__name__, 
                external_stylesheets=[
                      dbc.themes.BOOTSTRAP, 
                      dbc_css,
                      dbc.icons.FONT_AWESOME
                  ],
                  use_pages=True
                  )


# -----------
# Filter data
# -----------

def get_countries(df_in):
    countries = sorted(df_in.country.dropna().unique())
    return countries

def get_countries_label_value_pairs(df_in):
    label_value_pairs = []
    for i in get_countries(df_in):
        label_value_pairs.append({'label':i,
                               'value':i})
    
    return label_value_pairs

def get_facility_types(df_in):
    return sorted(df_in.type_property.dropna().unique())            
 
def get_facility_types_label_value_pairs(df_in):
    label_value_pairs = []
    for i in get_facility_types(df_in):
        label_value_pairs.append({'label':i,
                               'value':i})
    
    return label_value_pairs

def get_infrastructure_info(df_in):

    infrastructure_list=[]
    for sublist in df_in.infrastructure.dropna():
        infrastructure_list.extend(sublist)

    infrastructure_list = list(set(infrastructure_list))
    infrastructure_list.sort(key=str.lower)

    return infrastructure_list

def get_infrastructure_label_value_pairs(df_in):

    label_value_pairs = []
    for i in get_infrastructure_info(df_in):
        label_value_pairs.append({'label':i,
                               'value':i})
    
    return label_value_pairs

def get_availabledata(df_in):

    availabledata_list=[]
    for sublist in df['availabledata'].dropna():
        availabledata_list.extend(sublist)

    availabledata_list = list(set(availabledata_list))
    availabledata_list.sort(key=str.lower)

    return availabledata_list

def get_availabledata_label_value_pairs(df_in):

    label_value_pairs = []
    for i in get_availabledata(df_in):
        label_value_pairs.append({'label':i,
                               'value':i})
    
    return label_value_pairs


# create a dropdown for the countries
# TODO: Turn this into a function!
countrySelector = dbc.Col(
    [dbc.Label("Country"),
        dcc.Dropdown(id='country_selector',
                    options=get_countries_label_value_pairs(df),
                    multi=True,
                    value="",
                    ),
    ],
    className="col-12 col-md-6 col-lg-3"
)

facilityTypeSelector = dbc.Col(
    [dbc.Label("Facility type"),
        dcc.Dropdown(id='facilitytype_selector',
                    options=get_facility_types_label_value_pairs(df),
                    multi=True,
                    value="",
                    ),
    ],
    className="col-12 col-md-6 col-lg-3"
)

infrastructureSelector = dbc.Col(
    [dbc.Label("Infrastructure"),
        dcc.Dropdown(id='infrastructure_selector',
                    options=get_infrastructure_label_value_pairs(df),
                    multi=True,
                    value="",
                    ),
    ],
    className="col-12 col-md-6 col-lg-3"
)

availabledataSelector = dbc.Col(
    [dbc.Label("Available data"),
        dcc.Dropdown(id='availabledata_selector',
                    options=get_availabledata_label_value_pairs(df),
                    multi=True,
                    value="",
                    ),
    ],
    className="col-12 col-md-6 col-lg-3"
)

filters = [
    countrySelector,
    facilityTypeSelector,
    infrastructureSelector,
    availabledataSelector
]

def filterIcon():
    # define an icon for filtering
    filterIcon = [
        html.I(className="fa-solid fa-filter me-2"),
                "Filter facilities",
    ]
    return filterIcon


def filter_facilities(
    df_in,
    countries_selected="",
    facilitytypes_selected="",
    infrastructure_selected="",
    availabledata_selected=""
    ):
    
    # get the indices where any of the countries match
    if not countries_selected:    
        country_i = df_in.index
    else:
        country_i = df_in.index[df_in['country'].isin(countries_selected)]        

    # get the indices where any of the facility types match
    if not facilitytypes_selected:
        facilitytype_i = df_in.index
    else:
        facilitytype_i = df_in.index[df_in['type_property'].isin(facilitytypes_selected)]

    # get the indices where any of the infrastructure match
    if not infrastructure_selected:
        infrastructure_i = df_in.index
    else:
        #infrastructure_i = df_in.index
        df_infrastructure = df_in.dropna(subset=['infrastructure'], inplace=False)
        infrastructure_i = df_infrastructure.index[pd.DataFrame(df_infrastructure['infrastructure'].tolist()).isin(infrastructure_selected).any(1).values]        

    # get the indices where any of the available data match
    if not availabledata_selected:
        availabledata_i = df_in.index
    else:
        #availabledata_i = df_in.index
        df_availabledata = df_in.dropna(subset=['availabledata'], inplace=False)
        availabledata_i = df_availabledata.index[pd.DataFrame(df_availabledata['availabledata'].tolist()).isin(availabledata_selected).any(1).values]
        
    dff = df_in.loc[(country_i) & (facilitytype_i) & (infrastructure_i) & (availabledata_i)]
    
    return dff


# -----------------
# Utility functions
# -----------------

def create_www_link(url):

    if any(pd.isna(url)):
        www_link = []
    else:
        www_link = html.A(
            [
                html.I(className="fa-solid fa-globe"),
                ' link'
            ],
            className = "btn btn-outline-secondary mr-2",
            href=''.join(url), target="_blank")

    return www_link

def create_www_link_button(url, button_text=" link"):

    if not url.strip():
        return dbc.Button(
            [
                html.I(className="fa-solid fa-globe"),
                " ",
                button_text
            ],
            href = '#', target="_blank",
            color="primary",            
            disabled=True,
            className="me-1 btn btn-outline-primary btn-sm"
        )
    else:
        return dbc.Button(
            [
                html.I(className="fa-solid fa-globe"),
                " ",
                button_text
            ],
            href = ''.join(url), target="_blank",
            color="primary",            
            active=True,
            className="me-1 btn btn-primary btn-sm"
        )

def create_googlemaps_link_button(lat,lon):

    if any(pd.isna([lat, lon])):
        return []
    else:
        url_str = "https://www.google.com/maps/search/?api=1&query=" + lat.apply(str) + "%2C" + lon.apply(str) + ""
        return dbc.Button(
            [
                html.I(className="fa-solid fa-map-location-dot"),
                ' Google maps'
            ],
            href=''.join(url_str), target="_blank",
            active=True,
            className="me-1 btn btn-primary btn-sm"
            )

# --------------
# Create the map
# --------------

def create_facility_map(df_in):
    """
    Create the map of all facilities

    Maps all facilities that match the filters. The map is clickable.

    Parameters
    ----------
    dff : DataFrame 
        data frame containing the subset of facilities that match the filters.

    Returns
    -------
    fig : a plotly express figure object containing the map

    """

    # establish the bounds of the map
    if len(df_in) >= 2:
        dlat = 1+df_in["lat"].max()-df_in["lat"].min()-1
        dlon = 1+df_in["lon"].max()-df_in["lon"].min()-1
        max_bound = max(abs(dlat), abs(dlon)) * 111
        map_zoom = math.floor(11.5 - np.log(max_bound))
    elif len(df_in) == 0:
        map_zoom = 1
    else:
        map_zoom = 5

    fig = px.scatter_mapbox(
        df_in,
        lat="lat",
        lon="lon",
        hover_name="name",
        hover_data=dict(
            lat=False,
            lon=False,
        ),
        zoom=map_zoom,
        #size = 5
    )
    fig.update_layout(
        mapbox_style="open-street-map",
        hovermode='closest',
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    #fig.update_traces(
    #    cluster=dict(enabled=True, size=2, step=3))    

    return fig


# -----------------------
# Create a sortable table
# -----------------------

def create_sortable_facility_table(df_in):
    """
    Create a sortable table for the facilities

    Displays information about the facilities matching the filters in a sortable, searchable table. 

    Parameters
    ----------
    df_in : data frame
        A data fram containing a subset of the data about the facilities

    Returns
    -------
    sortable_facility_table
        A Dash data table 

    """

    df_table = df_in[["name", "country", "type_property"]].copy()

    df_table["id"] =df_table.index

    df_table.rename(columns={"type_property": "type"}, inplace=True)

    # create a list of columns to display
    show_columns = ["name","country","type"]

    sortable_facility_table = dash_table.DataTable(
        id="sortable-facility-table",
        columns=[
            {"name": i, "id": i, "deletable": False, "selectable": False} for i in show_columns #df_table.columns
        ],
        data=df_table.to_dict('records'),
        #data = df_table.to_dict('index'),
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            'lineHeight': '15px'
        },
        style_cell_conditional=[
            {'if': {'column_id': 'id'},
             'width': '10%'},
            {'if': {'column_id': 'name'},
             'width': '30%'},
            {'if': {'column_id': 'country'},
             'width': '25%'},
            {'if': {'column_id': 'type'},
             'width': '30%'},
        ],
        style_as_list_view=True,
        style_cell={'padding': '5px'},
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold'
        },
        editable=False,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        column_selectable="single",
        # row_selectable="multi",
        row_deletable=False,
        selected_columns=[],
        selected_rows=[],
        page_action="native",
        page_current=0,
        page_size=6,
    ),

    return sortable_facility_table

# ----------------------------------------------------
# Generate an information card for a specific facility
# ----------------------------------------------------

def get_card_facility_title_element(dff_selected):
    """
    Create an HTML title element

    Creates the text to use as the card title from the table.

    Parameters
    ----------

    Returns
    -------
    Dash HTML object

    """

    return html.H4(dff_selected["name"])

def get_card_facility_description_element(dff_selected):
    """
    Create a text block containing a description of a facility

    Return a description of a facility with a source (if given). Otherwise, just return an empty text block

    Parameters
    ----------
    dff_selected : data frame
        a single row from a data frame. Contains the row of data selected from the map or data table.

    Returns
    -------
    card_content : HMTL object
        a Dash HTML object with a description of the selected facility.

    """

    if dff_selected["information"].any():

        # convert the dataframe in to a dictionary
        info_dict = dff_selected["information"].squeeze()

        # get the description text
        if info_dict.get("description"):
            description_text = info_dict.get('description')
        else:
            description_text = "Description is empty"

        # check if it has a source we need to acknowledge
        if info_dict.get("copied"):
            description_text_element = html.Blockquote('"' + description_text + '"')
            description_source_element = html.P(
                    [
                        "source: ",
                        html.A(
                            urlparse(info_dict.get("source")).netloc,
                            href=''.join(info_dict.get("source"))
                        )
                    ]
                )
        else:
            description_text_element = html.P(description_text)
            description_source_element = []

        # create links to go with it
        if info_dict.get("homepage"):
            link_button_home = create_www_link_button(info_dict["homepage"], "homepage")
        else:
            link_button_home = create_www_link_button("", "homepage")

    else:
        description_text_element = html.P("No information found")
        description_source_element = []
        link_button_home = create_www_link_button("", "homepage")
    
    
    link_button_GoogleMaps = create_googlemaps_link_button(dff_selected["lat"],
                                                        dff_selected["lon"])
                                                                

    card_content = dbc.Row(
        [
            dbc.Col(
                [
                    description_text_element,
                    description_source_element,
                    html.Div(
                        [
                            link_button_home,
                            link_button_GoogleMaps
                        ]
                    )
                ]
            )
        ]
    )
    
    return card_content

def create_Ul(contents):
    """
    Create an unordered HTML list from a list or array

    Creates an unordered HTML list (<ul></ul>) from a list or array. Returns a multi-level list for nested input data.

    Parameters
    ----------
    contents : list or array
        the data to be parsed into a list

    Returns
    -------
    HTML object
        a Dash HTML.ul object

    """
    h = []
    for i in contents:
        if isinstance(i, list):
            h.append(create_Ul(i))
        else:
            h.append(html.Li(i))
    return html.Ul(h) 


def get_card_infrastructure_element(dff_selected):
    """
    Create an element containing information about the infrastructure

    Parses the infrastructure data to generate a list of infrastructure at a facility.

    Parameters
    ----------
    dff_selected : data frame
        a single row of a data frame, containing information about the facility

    Returns
    -------
    HTML element
        A Dash HTML element with information about the facility

    """

    if not dff_selected["infrastructure"].isnull().values.any():

        infrastructure_list = create_Ul(dff_selected['infrastructure'].squeeze())

        infrastructure_element = [
            html.P("Available infrastructure:"),
            infrastructure_list
        ]        
        return infrastructure_element
    else:
        return(html.P("no infrastructure information available"))


def get_card_availabledata_element(dff_selected):

    """
    Create an element containing information about the available data 

    Parses the infrastructure data to generate a list of available data at a facility.

    Parameters
    ----------
    dff_selected : data frame
        a single row of a data frame, containing information about the facility

    Returns
    -------
    HTML element
        A Dash HTML element with information about the facility

    """

    if not dff_selected["availabledata"].isnull().values.any():

        availabledata_list = create_Ul(dff_selected['availabledata'].squeeze())

        availabledata_element = [
            html.P("Available data:"),
            availabledata_list
        ]        
        return availabledata_element
    else:
        return(html.P("no information about data available"))



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
                        html.Img(src=app.get_asset_url('Logo_white_colourfulC_100H.png'),
                                 style={"width": "100%", },
                                 className="my-2"),
                        html.P(
                            "We're experts in finding and deploying new technologies for wind energy applications")
                    ]
                ),
                className="col-12 col-md-3"
                ),
            dbc.Col(
                [

                ],
                className="col-12 col-md-3"
            ),
            dbc.Col(
                [

                ],
                className="col-12 col-md-3"
            ),
            dbc.Col(
                [
                    html.H2("Contact"),
                    html.P(["TGU enviConnect", html.Br(),
                           "TTI GmbH", html.Br(),
                           "Nobelstrasse 15", html.Br(),
                           "70569 Stuttgart", html.Br(),
                           "Germany"])
                ],
                className="col-12 col-md-3"
            )
        ],
        className="h-md-20 pt-2 footer"
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
    subfooter : Dash HTML object

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
                                    html.A("Publisher", href="#"),
                                    html.A("Privacy Policy",
                                           href="",
                                           style={"margin-left": "10px"}
                                           ),                                  
                                ],
                                className="copyright"
                            ),
                            # copyright notice
                            html.Div(
                                [
                                    html.P("\u00A9 enviConnect 2022")
                                ],
                                className="copyright"
                            )
                        ],
                        className="sub-footer-inner"
                    )
                ],
                className="col-12"
            ),
        ],
        className="sub-footer"
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

            ],

        ),
        # title row
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H1("Wind Energy R&D Facilities Explorer (App)")
                    ],
                    width=12),
            ],
            className="title h-10 pt-2 mb-2",
        ),
        # content
        html.Div(
            [

                # map and table content row
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dcc.Graph(
                                    figure=create_facility_map(df),
                                    id="facility_map"
                                )
                            ],
                            className="col-12 col-lg-6 h-sm-60 h-md-33 h-lg-25"
                        ),
                        dbc.Col(
                            [
                                html.Div(
                                    create_sortable_facility_table(df)
                                )
                            ],
                            className="col-12 col-lg-6"
                        ),
                    ],
                    className="pb-2 h-sm-60 h-md-33 h-lg-25"
                ),
                # filter row
                dbc.Row(
                    [
                        dbc.Col(
                            filterIcon(),
                            className="col-12 col-md-1"
                        ),
                        dbc.Col(
                            [
                                dbc.Row(
                                    #get_filters(df)
                                    filters
                                )
                            ],
                            className="col-12 col-md-11"
                        )
                    ],
                    className="filter_row px-1 py-2 mx-0 my-2"
                ),
                # card row
                dbc.Row(
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            # title: should span whole card
                                            dbc.Col(
                                                [
                                                    html.H4(
                                                        className="card-title", id="card-title")
                                                ],
                                                className="col-12"
                                            ),
                                            # row for description
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            html.P(
                                                                className="card-text", id="card-desc")
                                                        ],
                                                        className="col-12 col-md-6"
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.Div(
                                                                className="card-text", id="card-infrastructure")
                                                        ],
                                                        className="col-12 col-md-3"
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            html.Div(
                                                                className="card-text", id="card-availabledata")
                                                        ],
                                                        className="col-12 col-md-3"
                                                    )
                                                ],
                                                className="col-12"
                                            )
                                        ]
                                    )
                                ]
                            )
                        ],
                        width=12
                    ),
                    className="pb-2"
                ),
            ],
            className="content",
            style={"min-height":"80vh"},
        ),
        # footer
        html.Div(
            [
                create_footer_row(),
            ],
            className="h-20 footer"
        ),
        # subfooter
        html.Div(
            [
                create_subfooter()
            ],
            className="h-10 sub-footer"
        ),
        # dcc.Store stores the intermediate value
        # dcc.Store(id='intermediate-value')
    ],
    fluid=True,
    className="dbc h-100",
    style={
        "min-height": "100vh"
    }
)


# --------------
# Update the map
# --------------
@app.callback(
    Output('facility_map', 'figure'),
    Input('country_selector', 'value'),
    Input('facilitytype_selector', 'value'),
    Input('infrastructure_selector', 'value'),
    Input('availabledata_selector', 'value')
)
def update_map(countries_selected="", facilitytypes_selected="", infrastructure_selected="", availabledata_selected=""):
    """
    Update the map when filter values change

    Parameters
    ----------
    countries_selected : list
        a list of the countries selected in the filters
    facilitytypes_selected : list
        a list of the facility types selected in the filters
    infrastructure_selected : list
        a list of the infrastructure selected in the filters
    availabledata_selected : list
        a list of the available data selected in the filters

    Returns
    -------
    fig : a plotly express figure object containing the map

    """

    dff = filter_facilities(
        df,
        countries_selected,
        facilitytypes_selected,
        infrastructure_selected,
        availabledata_selected
    )

    fig = create_facility_map(dff)

    return fig

@app.callback(
    [
        Output("card-title", "children"),
        Output("card-desc", "children"),
        Output("card-infrastructure", "children"),
        Output("card-availabledata", "children"),
        Output("sortable-facility-table", "selected_cells"),
        Output("sortable-facility-table", "active_cell"),
    ],
    [
       Input('facility_map', 'clickData'),
       Input('sortable-facility-table', 'active_cell')
   ]
)
def update_information_card(clickData, active_cell={}):
    """
    Create an card containing information about the selected facility 

    Wrapper. Identifies the facility that has been selected. Then generates an information block, list of infrastructure, and list of available data at that facility.

    Parameters
    ----------
    clickData : dictionary
        information about the location clicked on the map
    
    active_cell : dictionary
        information about the cell clicked on the table

    Returns
    -------
    HTML element
        A Dash element for the selected facility

    """


    # first check to see what triggered the callback

    if (clickData is None) and (not active_cell):
        card_title_element = html.H4(
            [
                html.I(className="fa-solid fa-circle-info"),
                " ",
                "Select a facility"
            ]
        )
        card_description_element = html.P(
            "Click on a site on the map or in the table to find out more")
        card_infrastructure_element = []
        card_availabledata_element = []
    else:
        if not (clickData is None):
            selected = clickData["points"][0]
            dff_selected = df[(df['lat'] == selected['lat']) & (
                df['lon'] == selected['lon'])] if selected else None

        if active_cell:
            dff_selected = df[df.index==active_cell['row_id']]

        card_title_element = get_card_facility_title_element(dff_selected)

        card_description_element = get_card_facility_description_element(
            dff_selected)

        card_infrastructure_element = get_card_infrastructure_element(
            dff_selected)

        card_availabledata_element = get_card_availabledata_element(
            dff_selected)

    # and clear the selections
    selected_cells=[]
    active_cell=None

    return card_title_element, card_description_element, card_infrastructure_element, card_availabledata_element, selected_cells, active_cell


@app.callback(
    Output('sortable-facility-table','data'),
    Input('country_selector','value'),
    Input('facilitytype_selector','value'),
    Input('infrastructure_selector','value'),
    Input('availabledata_selector','value'),
)
def get_filtered_facilities(countries_selected="", facilitytypes_selected="", infrastructure_selected="", availabledata_selected=""):

    """
    Filter the data

    Filters the data frame of facilities according to values selected in the drop-downs

    Parameters
    ----------



    Returns
    -------
    data frame : contains the facilities that match the filters

    """

    # get the table of facilities that match the filter values
    dff = filter_facilities(
        df,
        countries_selected,
        facilitytypes_selected,
        infrastructure_selected,
        availabledata_selected
        )
        
    df_table = dff[["name","country","type_property"]].copy()
    df_table["id"] =df_table.index

    df_table.rename(columns={"type_property":"type"}, inplace=True)

    #return dff.to_json(date_format='iso', orient='split'), df_table
    return df_table.to_dict('records')



if __name__ == '__main__':
    app.run_server(debug=True, use_reloader= False)
