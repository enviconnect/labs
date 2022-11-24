import plotly.express as px
import plotly.graph_objects as go

# set up Dash
# from jupyter_dash import JupyterDash

import dash
from dash import Dash, html, dcc, Input, Output
from dash import dash_table

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
# Register this page
# --------------------

dash.register_page(__name__)

# --------------------
# Get and prepare data
# --------------------

def prepare_data(data_source):

    # Open the file and load the file
    with open(data_source) as f:
        data = yaml.load(f, Loader=SafeLoader)


    
    # convert data to a datatable - easier later
    df_in = pd.DataFrame(data["features"])
    df_in.reset_index(inplace=True)

    # explode and join the dictionaries
    df_geom = pd.DataFrame(df_in.pop("geometry").values.tolist())
    df_geom.reset_index(inplace=True)

    df_properties = pd.DataFrame(df_in.pop("properties").values.tolist())
    df_properties.reset_index(inplace=True)
    # pop out the coordinates from the geometry
    df_coordinates = pd.DataFrame(
        df_geom.pop("coordinates").values.tolist(), columns=["lon", "lat", "elev"]
    )
    df_coordinates.reset_index(inplace=True)
    # join them
    df = df_geom.join(
        df_properties.set_index("index"), lsuffix="_geom", rsuffix="_property"
    )

    df = df.join(df_coordinates.set_index("index"))

    # information
    df_information = pd.DataFrame(df_in.pop("information"))
    df_information.reset_index(inplace=True)
    df = df.join(df_information.set_index("index"))

    # infrastructure is a column of lists
    df_infrastructure = pd.DataFrame(df_in.pop("infrastructure"))
    df_infrastructure.reset_index(inplace=True)

    df = df.join(df_infrastructure.set_index("index"))

    # data is a column of lists
    df_availabledata = pd.DataFrame(df_in.pop("availabledata"))
    df_availabledata.reset_index(inplace=True)

    df = df.join(df_availabledata.set_index("index"))

    return df


df = prepare_data("data/facilities.yaml")

#px.set_mapbox_access_token(open(".mapbox_token").read())

# -----------
# Filter data
# -----------


def get_countries(df_in):
    countries = sorted(df_in.country.dropna().unique())
    return countries


def get_countries_label_value_pairs(df_in):
    label_value_pairs = []
    for i in get_countries(df_in):
        label_value_pairs.append({"label": i, "value": i})

    return label_value_pairs


def get_facility_types(df_in):
    return sorted(df_in.type_property.dropna().unique())


def get_facility_types_label_value_pairs(df_in):
    label_value_pairs = []
    for i in get_facility_types(df_in):
        label_value_pairs.append({"label": i, "value": i})

    return label_value_pairs


def get_infrastructure_info(df_in):

    infrastructure_list = []
    for sublist in df_in.infrastructure.dropna():
        infrastructure_list.extend(sublist)

    infrastructure_list = list(set(infrastructure_list))
    infrastructure_list.sort(key=str.lower)

    return infrastructure_list


def get_infrastructure_label_value_pairs(df_in):

    label_value_pairs = []
    for i in get_infrastructure_info(df_in):
        label_value_pairs.append({"label": i, "value": i})

    return label_value_pairs


def get_availabledata(df_in):

    availabledata_list = []
    for sublist in df["availabledata"].dropna():
        availabledata_list.extend(sublist)

    availabledata_list = list(set(availabledata_list))
    availabledata_list.sort(key=str.lower)

    return availabledata_list


def get_availabledata_label_value_pairs(df_in):

    label_value_pairs = []
    for i in get_availabledata(df_in):
        label_value_pairs.append({"label": i, "value": i})

    return label_value_pairs


def create_selectors(df):

    countrySelector = dbc.Col(
        [
            dbc.Label("Country"),
            dcc.Dropdown(
                id="country_selector",
                options=get_countries_label_value_pairs(df),
                multi=True,
                value="",
            ),
        ],
        className="col-12 col-md-6 col-lg-3",
    )

    facilityTypeSelector = dbc.Col(
        [
            dbc.Label("Facility type"),
            dcc.Dropdown(
                id="facilitytype_selector",
                options=get_facility_types_label_value_pairs(df),
                multi=True,
                value="",
            ),
        ],
        className="col-12 col-md-6 col-lg-3",
    )

    infrastructureSelector = dbc.Col(
        [
            dbc.Label("Infrastructure"),
            dcc.Dropdown(
                id="infrastructure_selector",
                options=get_infrastructure_label_value_pairs(df),
                multi=True,
                value="",
            ),
        ],
        className="col-12 col-md-6 col-lg-3",
    )

    availabledataSelector = dbc.Col(
        [
            dbc.Label("Available data"),
            dcc.Dropdown(
                id="availabledata_selector",
                options=get_availabledata_label_value_pairs(df),
                multi=True,
                value="",
            ),
        ],
        className="col-12 col-md-6 col-lg-3",
    )

    filters = [
        countrySelector,
        facilityTypeSelector,
        infrastructureSelector,
        availabledataSelector,
    ]

    return filters


def filterIcon():
    """
    Define an icon for the filter row

    """
    filterIcon = [
        html.I(className="fa-solid fa-filter me-2"),
        html.B("Filter facilities"),
    ]
    return filterIcon


def filter_facilities(
    df_in,
    countries_selected="",
    facilitytypes_selected="",
    infrastructure_selected="",
    availabledata_selected="",
):
    """
    Find facilities that match the filter values

    """

    # get the indices where any of the countries match
    if not countries_selected:
        country_i = df_in.index
    else:
        country_i = df_in.index[df_in["country"].isin(countries_selected)]

    # get the indices where any of the facility types match
    if not facilitytypes_selected:
        facilitytype_i = df_in.index
    else:
        facilitytype_i = df_in.index[
            df_in["type_property"].isin(facilitytypes_selected)
        ]

    # get the indices where any of the infrastructure match
    if not infrastructure_selected:
        infrastructure_i = df_in.index
    else:
        # infrastructure_i = df_in.index
        df_infrastructure = df_in.dropna(subset=["infrastructure"], inplace=False)
        infrastructure_i = df_infrastructure.index[
            pd.DataFrame(df_infrastructure["infrastructure"].tolist())
            .isin(infrastructure_selected)
            .any(1)
            .values
        ]

    # get the indices where any of the available data match
    if not availabledata_selected:
        availabledata_i = df_in.index
    else:
        # availabledata_i = df_in.index
        df_availabledata = df_in.dropna(subset=["availabledata"], inplace=False)
        availabledata_i = df_availabledata.index[
            pd.DataFrame(df_availabledata["availabledata"].tolist())
            .isin(availabledata_selected)
            .any(1)
            .values
        ]

    # get the intersection of the indices
    dff_i = country_i.intersection(facilitytype_i).copy()
    dff_i = dff_i.intersection(infrastructure_i)
    dff_i = dff_i.intersection(availabledata_i)

    dff = df_in.loc[dff_i].copy()

    return dff


# -----------------
# Utility functions
# -----------------


def create_www_link(url):

    if any(pd.isna(url)):
        www_link = []
    else:
        www_link = html.A(
            [html.I(className="fa-solid fa-globe"), " link"],
            className="btn btn-outline-secondary mr-2",
            href="".join(url),
            target="_blank",
        )

    return www_link


def create_www_link_button(url, button_text=" link"):

    if not url.strip():
        return dbc.Button(
            [html.I(className="fa-solid fa-globe"), " ", button_text],
            href="#",
            target="_blank",
            color="primary",
            disabled=True,
            className="me-1 btn btn-outline-primary btn-sm",
        )
    else:
        return dbc.Button(
            [html.I(className="fa-solid fa-globe"), " ", button_text],
            href="".join(url),
            target="_blank",
            color="primary",
            active=True,
            className="me-1 btn btn-primary btn-sm",
        )


def create_googlemaps_link_button(lat, lon):

    if any(pd.isna([lat, lon])):
        return []
    else:
        url_str = (
            "https://www.google.com/maps/search/?api=1&query="
            + lat.apply(str)
            + "%2C"
            + lon.apply(str)
            + ""
        )
        return dbc.Button(
            [html.I(className="fa-solid fa-map-location-dot"), " Google maps"],
            href="".join(url_str),
            target="_blank",
            active=True,
            className="me-1 btn btn-primary btn-sm",
        )


# --------------
# Create the map
# --------------

def get_map_zoom(df_in):
    # establish the bounds of the map
    if len(df_in) >= 2:
        dlat = 1 + df_in["lat"].max() - df_in["lat"].min() - 1
        dlon = 1 + df_in["lon"].max() - df_in["lon"].min() - 1
        max_bound = max(abs(dlat), abs(dlon)) * 111
        map_zoom = math.floor(11.5 - np.log(max_bound))
    elif len(df_in) == 0:
        map_zoom = 1
    else:
        map_zoom = 5

    return map_zoom

def create_facility_map_plotly(df_map):
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

    map_zoom= get_map_zoom(df_map)

    fig = []
    
    fig = px.scatter_mapbox(
        df_map,
        lat="lat",
        lon="lon",
        hover_name="name",
        hover_data=dict(
            lat=False,
            lon=False,
        ),        
        zoom=map_zoom,
    )

    fig.update_layout(
        mapbox_style="open-street-map",
        hovermode="closest",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )
    
    fig.update_traces(marker=dict(size=7))
    fig.update()
    
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

    df_table["id"] = df_table.index

    df_table.rename(columns={"type_property": "type"}, inplace=True)

    # create a list of columns to display
    show_columns = ["name", "country", "type"]

    sortable_facility_table = (
        dash_table.DataTable(
            id="sortable-facility-table",
            columns=[
                {"name": i, "id": i, "deletable": False, "selectable": False}
                for i in show_columns  # df_table.columns
            ],
            data=df_table.to_dict("records"),
            # data = df_table.to_dict('index'),
            style_data={"whiteSpace": "normal", "height": "auto", "lineHeight": "15px"},
            style_cell_conditional=[
                {"if": {"column_id": "id"}, "width": "10%"},
                {"if": {"column_id": "name"}, "width": "30%"},
                {"if": {"column_id": "country"}, "width": "25%"},
                {"if": {"column_id": "type"}, "width": "30%"},
            ],
            style_as_list_view=True,
            style_cell={
                "padding": "5px",
                "border-bottom": "1px solid #E9E9E9",
                "border-top": "1px solid #E9E9E9",
            },
            style_header={
                "backgroundColor": "#E9E9E9",
                #'color': "#FFFFFF",
                "fontWeight": "bold",
                "border": "1px solid #E9E9E9",
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
            style_table={"overflow-y": "none", "border": "1px solid #E9E9E9"},
            page_current=0,
            page_size=7,
        ),
    )

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
            description_text = info_dict.get("description")
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
                        href="".join(info_dict.get("source")),
                    ),
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

    link_button_GoogleMaps = create_googlemaps_link_button(
        dff_selected["lat"], dff_selected["lon"]
    )

    card_content = dbc.Row(
        [
            dbc.Col(
                [
                    description_text_element,
                    description_source_element,
                    html.Div([link_button_home, link_button_GoogleMaps]),
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

    infrastructure_list = create_Ul(dff_selected['infrastructure'].squeeze())

    infrastructure_element = [
        html.P("Available infrastructure:"),
        infrastructure_list
    ]        
    return infrastructure_element


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

    availabledata_list = create_Ul(dff_selected['availabledata'].squeeze())

    availabledata_element = [
        html.P("Available data:"),
        availabledata_list
    ]        
    return availabledata_element
    

# -----------------------------
# Create the layout for this page
# -----------------------------

# Create a layout with two columns:
# 3 cols on the left for filters, 9 on the right for map & information
layout = dbc.Container(
    [
        # title row
        html.Div(
            [
            dbc.Row(
                [
                    dbc.Col(
                        [html.H1("Wind Energy R&D Facilities Explorer")],
                        width=12,
                    ),
                ],
                className="title h-10 pt-2 mx-0 mb-2",
            ),
            ]
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
                                    #figure=create_facility_map_plotly(df),                                  
                                    #figure={},
                                    id="facility_map"
                                )
                            ],
                            className="col-12 col-lg-6 h-sm-60 h-md-33 h-lg-25",
                        ),
                        dbc.Col(
                            [html.Div(create_sortable_facility_table(df))],
                            className="col-12 col-lg-6",
                        ),
                    ],
                    className="pb-2 h-sm-60 h-md-33 h-lg-25",
                ),
                # filter row
                dbc.Row(
                    [
                        dbc.Col(filterIcon(), className="col-12 col-md-1"),
                        dbc.Col(
                            [
                                dbc.Row(
                                    create_selectors(df)
                                )
                            ],
                            className="col-12 col-md-11",
                        ),
                    ],
                    className="filter_row px-1 py-2 mx-0 my-2",
                ),
                # tabs row
                dbc.Col(
                    [
                        html.H4(
                            [
                                html.I(className="fa-solid fa-circle-info"),
                                " ",
                                "Select a facility",
                            ],
                            id="tabs-title",
                        ),
                        dbc.Tabs(
                            [
                                dbc.Tab(
                                    label="Description",
                                    tab_id="tab-1",
                                    id="tab-desc",
                                    className="p-2 info-tab",
                                ),
                                dbc.Tab(
                                    label="Infrastructure",
                                    tab_id="tab-2",
                                    id="tab-infrastructure",
                                    className="p-2 info-tab",
                                ),
                                dbc.Tab(
                                    label="Available data",
                                    tab_id="tab-3",
                                    id="tab-availabledata",
                                    className="p-2 info-tab",
                                ),
                            ],
                            id="card-tabs",
                            active_tab="tab-1",
                        ),
                    ],
                    className="p-2 mb-2 info-tab-box",
                ),
            ],
            className="content",
            style={"min-height": "80vh"},
        ),
    ],
    fluid=True,
    className="dbc h-80",
    style={"min-height": "80vh"},
)


# ------------------------
# Update the map and table
# -------------------------
@dash.callback(
    [
    Output("facility_map", "figure"),
    Output("sortable-facility-table", "data"),
    ],
    [    
    Input("country_selector", "value"),
    Input("facilitytype_selector", "value"),
    Input("infrastructure_selector", "value"),
    Input("availabledata_selector", "value"),
    ]
)
def update_table_map(
    countries_selected="",
    facilitytypes_selected="",
    infrastructure_selected="",
    availabledata_selected="",
):
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
        availabledata_selected,
    )

    #update the map data
    fig = create_facility_map_plotly(dff)
    
    df_table = dff[["name", "country", "type_property"]].copy()
    df_table["id"] = df_table.index

    df_table.rename(columns={"type_property": "type"}, inplace=True)

    return fig, df_table.to_dict("records")


@dash.callback(
    [
        Output("tabs-title", "children"),
        Output("tab-desc", "children"),
        Output("tab-infrastructure", "children"),
        Output("tab-infrastructure", "disabled"),
        Output("tab-availabledata", "children"),
        Output("tab-availabledata", "disabled"),
        Output("sortable-facility-table", "selected_cells"),
        Output("sortable-facility-table", "active_cell"),
    ],
    [
        Input("facility_map", "clickData"),
        Input("sortable-facility-table", "active_cell"),
    ],
)
def update_information_tabs(clickData=None, active_cell={}):
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
        tabs_title_element = html.H4(
            [
                html.I(className="fa-solid fa-circle-info"),
                " ",
                "Facility information"
            ]
        )
        tab_description_element = html.P(
            "Click on a facility on the map or in the table to find out more")
        tab_infrastructure_element = []
        tab_infrastructure_disabled = True
        tab_availabledata_element = []
        tab_availabledata_disabled = True
    else:
        if not (clickData is None):
            selected = clickData["points"][0]
            dff_selected = df[(df['lat'] == selected['lat']) & (
                df['lon'] == selected['lon'])] if selected else None

        if active_cell:
            dff_selected = df[df.index==active_cell['row_id']]

        tabs_title_element = get_card_facility_title_element(dff_selected)

        tab_description_element = get_card_facility_description_element(
            dff_selected)

        if not dff_selected["infrastructure"].isnull().values.any():
            tab_infrastructure_element = get_card_infrastructure_element(
                dff_selected)
            tab_infrastructure_disabled = False
        else:
            tab_infrastructure_element = html.P("no information about infrastructure available")
            tab_infrastructure_disabled = False

        if not dff_selected["availabledata"].isnull().values.any():
            tab_availabledata_element = get_card_availabledata_element(
            dff_selected)
            tab_availabledata_disabled = False
        else:
            tab_availabledata_element = html.P("no information about data available")
            tab_availabledata_disabled = False

    # and clear the selections
    selected_cells=[]
    active_cell=None

    return tabs_title_element, tab_description_element, tab_infrastructure_element, tab_infrastructure_disabled, tab_availabledata_element, tab_availabledata_disabled, selected_cells, active_cell
