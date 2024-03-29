import plotly.express as px
import plotly.graph_objects as go

# set up Dash
# from jupyter_dash import JupyterDash

import dash
from dash import Dash, html, Input, Output, State
from dash import dcc
from dash import dash_table
from dash.dependencies import Input, Output, ALL

import dash_bootstrap_components as dbc

import dash_leaflet as dl

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

# ------------------------------------
# Register this page and add meta data
# ------------------------------------

dash.register_page(
    __name__,
    title="Wind energy R&D facilities explorer",
    name="Wind energy R&D facilities explorer",
    description="A searchable map and database of global wind energy R&D facilities",
    image="images/explorer.png",
)

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

    # infrastructure is a dictionary
    df_infrastructure = pd.json_normalize(df_in["infrastructure"])
    df_infrastructure.reset_index(inplace=True)
    df["infrastructure_desc"] = df_infrastructure.description
    df["infrastructure_list"] = df_infrastructure.generic
    df["infrastructure_specific"] = df_infrastructure.specific

    # data is a column of lists
    df_availabledata = pd.json_normalize(df_in["availabledata"])
    df_availabledata.reset_index(inplace=True)
    df["availabledata_desc"] = df_availabledata.description
    df["availabledata_list"] = df_availabledata.generic
    df["availabledata_specific"] = df_availabledata.specific
    df["availabledata_portal"] = df_availabledata.portal

    # create an index column - useful
    df.insert(0, column="facility_id", value=df.index.values)

    # and finally, sort all by name
    df.sort_values(by=["name"], inplace=True)

    return df


df = prepare_data("data/facilities/facilities.yaml")

# px.set_mapbox_access_token(open(".mapbox_token").read())

# -----------
# Filter data
# -----------


def get_countries(df_in):
    countries = sorted(df_in.country.dropna().unique(), key=str.lower)
    return countries


def get_countries_label_value_pairs(df_in):
    label_value_pairs = []
    for i in get_countries(df_in):
        label_value_pairs.append({"label": i, "value": i})

    return label_value_pairs


def get_facility_types(df_in):
    return sorted(df_in.type_property.dropna().unique(), key=str.lower)


def get_facility_types_label_value_pairs(df_in):
    label_value_pairs = []
    for i in get_facility_types(df_in):
        label_value_pairs.append({"label": i, "value": i})

    return label_value_pairs


def get_infrastructure_info(df_in):

    infrastructure_list = []
    for sublist in df_in.infrastructure_list.dropna():
        infrastructure_list.extend(sublist)

    infrastructure_list = list(set(infrastructure_list))
    infrastructure_list.sort(key=str.lower)

    return infrastructure_list


def get_infrastructure_label_value_pairs(df_in):

    label_value_pairs = []
    for i in get_infrastructure_info(df_in):
        label_value_pairs.append({"label": i, "value": i})

    return label_value_pairs


def get_availabledata_info(df_in):

    availabledata_list = []
    for sublist in df.availabledata_list.dropna():
        availabledata_list.extend(sublist)

    availabledata_list = list(set(availabledata_list))
    availabledata_list.sort(key=str.lower)

    return availabledata_list


def get_availabledata_label_value_pairs(df_in):

    label_value_pairs = []
    for i in get_availabledata_info(df_in):
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
                optionHeight=45,
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
                optionHeight=45,
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
                optionHeight=45,
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
                optionHeight=45,
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
    filter_icon_element = html.H4(
        [
            html.I(className="fa-solid fa-filter"),
            " ",
            "Filter facilities",
        ]
    )
    return filter_icon_element


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
        df_infrastructure = df_in.dropna(subset=["infrastructure_list"], inplace=False)
        infrastructure_i = df_infrastructure.index[
            pd.DataFrame(df_infrastructure["infrastructure_list"].tolist())
            .isin(infrastructure_selected)
            .any(1)
            .values
        ]

    # get the indices where any of the available data match
    if not availabledata_selected:
        availabledata_i = df_in.index
    else:
        # availabledata_i = df_in.index
        df_availabledata = df_in.dropna(subset=["availabledata_list"], inplace=False)
        availabledata_i = df_availabledata.index[
            pd.DataFrame(df_availabledata["availabledata_list"].tolist())
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


def create_www_link_button(
    url,
    button_text="link",
    icon_classes="fa-solid fa-globe",
    button_color="",
    button_classes="",
):

    if not url.strip():
        return dbc.Button(
            [html.I(className=icon_classes), " ", button_text],
            href="#",
            target="_blank",
            disabled=True,
            className="me-1 btn btn-outline-secondary px-sm-2 px-lg-2 py-sm-2  py-lg-1 mb-sm-2 mb-lg-1 btn-sm"
            + " "
            + button_classes,
        )
    else:
        return dbc.Button(
            [html.I(className=icon_classes), " ", button_text],
            href="".join(url),
            target="_blank",
            color=button_color,
            disabled=False,
            className="me-1 btn px-sm-2 px-lg-2 py-sm-2 py-lg-1 mb-sm-2 mb-lg-1 btn-sm"
            + " "
            + button_classes,
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

        return create_www_link_button(
            "".join(url_str),
            button_text="Google maps",
            icon_classes="fa-solid fa-map-location-dot",
            button_color="primary",
            button_classes="btn-sm",
        )


# --------------
# Create the map
# --------------


def get_map_zoom(df_in):
    # establish the bounds of the map

    # get all of the non-na coordinates
    df_pos = df_in.dropna(subset=["lat", "lon"])

    if len(df_pos) >= 2:
        dlat = 1 + df_pos["lat"].max() - df_pos["lat"].min() - 1
        dlon = 1 + df_pos["lon"].max() - df_pos["lon"].min() - 1
        max_bound = max(max(abs(dlat), 1.0), max(abs(dlon), 1.0)) * 111
        map_zoom = math.floor(11.5 - np.log(max_bound))
    elif len(df_pos) == 0:
        map_zoom = 1
    else:
        map_zoom = 6

    return map_zoom


def get_map_center(df_in):

    # get all of the non-na coordinates
    df_pos = df_in.dropna(subset=["lat", "lon"])

    if len(df_pos) >= 2:
        dlat = 1.0 + df_pos["lat"].max() - df_pos["lat"].min() - 1.0
        dlon = 1.0 + df_pos["lon"].max() - df_pos["lon"].min() - 1.0

        map_center = (
            df_pos["lat"].min() - 1.0 + dlat / 2.0,
            df_pos["lon"].min() - 1.0 + dlon / 2.0,
        )
    elif len(df_pos) == 1:
        map_center = (df_pos["lat"].min(), df_pos["lon"].min())
    else:
        map_center = (0.0, 0.0)

    return map_center


def get_icon(icon):
    def get_icon_url(icon):
        if icon == "data portal":
            return dash.get_asset_url("facility-icons/data-portal.png")
        elif icon == "met mast":
            return dash.get_asset_url("facility-icons/met-mast.png")
        elif icon == "marine and maritime research center":
            return dash.get_asset_url(
                "facility-icons/marine-maritime-research-center.png"
            )
        elif icon == "power systems research center":
            return dash.get_asset_url(
                "facility-icons/power-systems-research-center.png"
            )
        elif icon == "surface energy balance":
            return dash.get_asset_url("facility-icons/surface-energy-balance.png")
        elif icon == "vertical profiling lidar":
            return dash.get_asset_url("facility-icons/vertical-profiling-lidar.png")
        elif icon == "wind atlas":
            return dash.get_asset_url("facility-icons/wind-atlas.png")
        elif icon == "wind energy research center":
            return dash.get_asset_url("facility-icons/wind-energy-research-center.png")
        elif icon == "wind energy test site":
            return dash.get_asset_url("facility-icons/wind-energy-test-site.png")
        elif icon == "wind turbine":
            return dash.get_asset_url("facility-icons/wind-turbine.png")
        elif icon == "wind farm":
            return dash.get_asset_url("facility-icons/wind-farm.png")
        else:
            return dash.get_asset_url("facility-icons/default.png")

    # define the icon object
    icon = {
        "iconUrl": get_icon_url(icon),
        "shadowUrl": dash.get_asset_url("facility-icons/shadow.png"),
        "iconSize": [25, 41],  # size of the icon
        "shadowSize": [40, 25],  # size of the shadow
        "iconAnchor": [
            12,
            41,
        ],  # point of the icon which will correspond to marker's location
        "shadowAnchor": [40, 25],  # the same for the shadow
        "popupAnchor": [
            -3,
            -76,
        ],  # point from which the popup should open relative to the iconAnchor
    }

    return icon


def create_facility_map_leaflet(df_map, dff_selected):

    markers = []
    # map_children.append(dl.TileLayer())
    # based on https://lyz-code.github.io/blue-book/coding/python/dash_leaflet/#using-markers and https://github.com/mintproject/Dash/blob/master/leaflet.py

    # "on click" should use https://github.com/thedirtyfew/dash-leaflet/issues/5

    for index, facility in df_map.iterrows():
        position = (facility["lat"], facility["lon"])
        if not pd.isna([position]).any():
            markers.append(
                dl.Marker(
                    position=position,
                    icon=get_icon(facility["icon"]),
                    id={
                        "type": "facility",
                        # "row": facility["facility-id"],
                        "id": "marker.{}".format(facility["facility_id"]),
                    },
                    children=[
                        dl.Tooltip(
                            facility["name"],
                        ),
                        # dl.Popup(facility["name"],),
                    ],
                )
            )

    marker_cluster = dl.MarkerClusterGroup(id="markers", children=markers)

    map_zoom = get_map_zoom(df_map)
    map_center = get_map_center(df_map)

    attribution = '&copy; <a href="https://www.openstreetmap.org/about/" target="_blank">OpenStreetMap</a> '

    if dff_selected.empty:
        leaflet_map = dl.Map(
            [
                dl.TileLayer(attribution=attribution),
                marker_cluster,
            ],
            zoom=map_zoom,
            center=map_center,
        )

    else:
        for index, facility in dff_selected.iterrows():
            selected_marker = dl.CircleMarker(
                center=(facility["lat"], facility["lon"]),
                radius=10,
                color="#666",
                id={
                    "type": "facility",
                    # "row": facility["facility-id"],
                    "id": "marker.{}".format(facility["facility_id"]),
                },
                children=[
                    dl.Tooltip(
                        facility["name"],
                    ),
                    # dl.Popup(facility["name"],),
                ],
            )

        leaflet_map = dl.Map(
            [dl.TileLayer(attribution=attribution), marker_cluster, selected_marker],
            zoom=get_map_zoom(dff_selected),
            center=get_map_center(dff_selected),
        )

    return leaflet_map


def points_not_shown_warning():

    return html.I(
        [
            html.Small(
                [
                    "Facilities without a defined location - e.g., satellites or data portals - are only listed in the table."
                ]
            ),
        ],
        className="py-0 my-1",
    )


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

    df_table = df_in[["name", "country", "type_property", "facility_id"]].copy()

    df_table["id"] = df_table.facility_id

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

    title_element = html.Div(
        [
            html.H4(
                dff_selected["name"],
                style={
                    "display": "inline-block",
                    "float": "left",
                    "margin-right": "1em",
                },
            ),
            html.Span(
                dff_selected["type_property"],
                id="tabs-tags",
                className="badge rounded-pill text-bg-primary align-top",
                style={
                    "vertical-align": "top",
                    "font-size": "x-small",
                    "display": "inline-block",
                },
            ),
        ],
        style={"display": "inline-block"},
    )

    return title_element


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
            description_text_element = dcc.Markdown(
                description_text, dangerously_allow_html=True
            )
        else:
            description_text_element = []

        # check if it has a quote we want to use
        if info_dict.get("quote"):
            description_quote_element = dcc.Markdown(
                "> " + info_dict.get("quote") + "", dangerously_allow_html=True
            )
            if info_dict.get("quote"):
                description_source_element = html.Footer(
                    [
                        "from ",
                        html.A(
                            urlparse(info_dict.get("source")).netloc,
                            href="".join(info_dict.get("source")),
                            target="_blank",
                        ),
                    ],
                    className="blockquote-footer",
                )
            else:
                description_source_element = []
        else:
            description_quote_element = []
            description_source_element = []

        if info_dict.get("note"):
            description_note_element = html.P("N.B.: {}.".format(info_dict.get("note")))
        else:
            description_note_element = []

        # create links to go with it
        if info_dict.get("homepage"):
            link_button_home = create_www_link_button(
                info_dict["homepage"], button_text="Homepage", button_color="primary"
            )
        else:
            link_button_home = create_www_link_button(
                "", button_text="Homepage", button_color="primary"
            )

        if info_dict.get("eawe-pdf"):
            link_button_eawe_pdf = create_www_link_button(
                info_dict["eawe-pdf"],
                button_text="EAWE information",
                icon_classes="fa-solid fa-file-pdf",
                button_color="primary",
            )
        else:
            link_button_eawe_pdf = []

    else:
        description_text_element = html.P("No information found")
        description_quote_element = []
        description_source_element = []
        description_note_element = []
        link_button_home = create_www_link_button("", button_text="homepage")
        link_button_eawe_pdf = []

    link_button_GoogleMaps = create_googlemaps_link_button(
        dff_selected["lat"], dff_selected["lon"]
    )

    link_button_feedback = create_feedback_button()

    card_content = dbc.Row(
        [
            dbc.Col(
                [
                    description_text_element,
                    description_quote_element,
                    description_source_element,
                    description_note_element,
                    html.Div(
                        [
                            html.Div(
                                [
                                    link_button_home,
                                    link_button_eawe_pdf,
                                    link_button_GoogleMaps,
                                ]
                            ),
                            html.Div([link_button_feedback]),
                        ],
                        className="d-flex justify-content-between",
                    ),
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
            h.append(html.Li(dcc.Markdown(i, dangerously_allow_html=True)))
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

    infrastructure_list = create_Ul(dff_selected["infrastructure_specific"].squeeze())

    infrastructure_element = [html.P("Available infrastructure:"), infrastructure_list]
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

    availabledata_list = create_Ul(dff_selected["availabledata_specific"].squeeze())

    if dff_selected["availabledata_portal"].any():
        dataportal_button = create_www_link_button(
            dff_selected["availabledata_portal"].squeeze(),
            button_text="data portal",
            button_color="primary",
            icon_classes="fa-solid fa-database",
        )
    else:
        dataportal_button = []

    if dff_selected["availabledata_desc"].any():
        description_text = dff_selected["availabledata_desc"]
        description_text_element = dcc.Markdown(
            description_text, dangerously_allow_html=True
        )
    else:
        description_text_element = []

    availabledata_element = [
        description_text_element,
        html.P("Available data:"),
        availabledata_list,
        dataportal_button,
    ]

    return availabledata_element


def create_action_buttons():
    action_element = dbc.Row(
        [dbc.Col([create_feedback_button(), create_about_button()])], className="mb-2"
    )

    return action_element


def create_feedback_button():

    feedback_button = create_www_link_button(
        url="https://forms.office.com/e/DfjQ6yPuyQ",
        button_text="Send feedback",
        icon_classes="fa-regular fa-comment",
        button_color="primary",
    )

    return feedback_button


def create_about_button():
    about_button = dbc.Button(
        [html.I(className="fa-solid fa-circle-info"), " ", "About this app"],
        id="about-button",
        className="me-1 btn btn-sm px-sm-3 px-lg-2 py-sm-2 py-lg-1 mb-sm-2 mb-lg-1",
        color="primary",
        n_clicks=0,
    )

    return about_button


def create_about_element():
    about_element = dbc.Collapse(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.P("This app is for demonstration purposes only."),
                            html.H3("Data sources"),
                            html.P(
                                "The data sources used in this app are all in the public domain, and include:"
                            ),
                            dcc.Markdown(
                                [
                                    """
                                * Each facility's own web page
                                * European Academy of Wind Energy (EAWE)
                                * The Wind Resource Assessment Group's wiki on [groups.io](https://groups.io/g/wrag/wiki/13236)
                                """
                                ]
                            ),
                            html.P(
                                "These information sources have been acknowledged and listed where applicable."
                            ),
                            html.H3("Technical aspects"),
                            html.P(
                                [
                                    "This app is built using ",
                                    html.A(
                                        "Dash",
                                        href="https://dash.plotly.com/",
                                        target="_blank",
                                    ),
                                    ", an open source library for python used to create data visualisations. ",
                                ]
                            ),
                            html.P(
                                "The map is created using dash-leaflet, which is in turn uses the leaflet.js library and data from Open Street Map."
                            ),
                            html.P(
                                [
                                    "The website is hosted on ",
                                    html.A(
                                        "eu.pythonanywhere.com",
                                        href="https://eu.pythonanywhere.com",
                                        target="_blank",
                                    ),
                                    ".",
                                ]
                            ),
                            html.H3("An Open Source project"),
                            html.P(
                                [
                                    "The source code used for this website is available ",
                                    html.A(
                                        "on GitHub",
                                        href="https://github.com/enviconnect/labs",
                                        target="_blank",
                                    ),
                                    ".",
                                ]
                            ),
                            html.H3("Disclaimer"),
                            html.P(
                                "The information provided here is provided in good faith and is believed to be a reasonable representation of the facilities that are described. However, the information may be out of data or inaccurate for a variety of reasons including incorrect transcribing, incorrect information provided in sources, outdated information, changes in funding, and many other reasons. App users should therefore investigate any facilities themselves before making any decisions about the suitably of the facility for their needs. We take no responsibility for any inaccuracies or omissions or any losses or damages that may result from them."
                            ),
                        ],
                    ),
                ]
            ),
        ],
        id="about",
        is_open=False,
        className="px-1 py-2 mx-0 my-2 text-muted small",
    )

    return about_element


@dash.callback(
    Output("about", "is_open"),
    [Input("about-button", "n_clicks")],
    [State("about", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# -----------------------------
# Create the layout for this page
# -----------------------------

layout = dbc.Container(
    [
        # title row
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [html.H1("Wind Energy R&D Facilities and Data")],
                            width=12,
                        ),
                    ],
                    className="title h-10 pt-2 mb-2",
                ),
            ]
        ),
        # content
        html.Div(
            [
                # logging row
                dbc.Row(
                    dbc.Col([html.Div(id="log")]),
                ),
                # map and table content row
                dbc.Row(
                    [
                        # map and warning column
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                create_facility_map_leaflet(
                                                    df, pd.DataFrame()
                                                ),
                                            ],
                                            id="facility-map-leaflet",
                                            className="col-12",
                                        )
                                    ]
                                ),
                                dbc.Row(
                                    [points_not_shown_warning()],
                                    id="points-not-shown-warning",
                                    className="",
                                ),
                            ],
                            className="col-12 col-lg-6",
                        ),
                        # table column
                        dbc.Col(
                            [html.Div(create_sortable_facility_table(df))],
                            className="col-12 col-lg-6 mt-2 mt-lg-0",
                        ),
                    ],
                    className="pb-2 h-sm-33 h-md-33 h-lg-25",
                ),
                # filter row
                dbc.Row(
                    [
                        dbc.Col(filterIcon(), className="col-12 col-lg-2"),
                        dbc.Col(
                            [
                                dbc.Row(create_selectors(df)),
                                dbc.Alert(
                                    [
                                        html.I(className="fa-regular fa-face-frown"),
                                        " ",
                                        "No facilities found that match all filters.",
                                    ],
                                    color="warning",
                                    id="no-results-warning",
                                    className="my-1 py-1",
                                ),
                            ],
                            className="col-12 col-lg-10",
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
                                "Facility information",
                            ],
                            id="tabs-title",
                        ),
                        dbc.Tabs(
                            [
                                dbc.Tab(
                                    html.P(
                                        "Click on a facility on the map or in the table to find out more"
                                    ),
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
                    className="p-3 mb-2 info-tab-box",
                ),
                # button row
                create_action_buttons(),
                # info row
                create_about_element(),
                # dcc.Store stores intermediate values
                dcc.Store(id="selected-facility-store"),
                dcc.Store(
                    id="filtered-facilities-store", data=df.to_json(orient="records")
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


@dash.callback(
    Output("filtered-facilities-store", "data"),
    Output("no-results-warning", "is_open"),
    Input("country_selector", "value"),
    Input("facilitytype_selector", "value"),
    Input("infrastructure_selector", "value"),
    Input("availabledata_selector", "value"),
)
def get_filtered_facilities(
    countries_selected="",
    facilitytypes_selected="",
    infrastructure_selected="",
    availabledata_selected="",
):

    dff = filter_facilities(
        df,
        countries_selected,
        facilitytypes_selected,
        infrastructure_selected,
        availabledata_selected,
    )

    # check to see if there are any facilities
    no_results_warning = False

    if dff.empty:
        no_results_warning = True

    return dff.to_json(orient="records"), no_results_warning


@dash.callback(
    Output("sortable-facility-table", "data"),
    Input("filtered-facilities-store", "data"),
)
def update_table(jsonified_filtered_facilities):

    dff = pd.read_json(jsonified_filtered_facilities, orient="records")

    df_table = dff[["name", "country", "type_property", "facility_id"]].copy()
    df_table["id"] = df_table.facility_id

    df_table.rename(columns={"type_property": "type"}, inplace=True)

    return df_table.to_dict("records")


@dash.callback(
    Output("facility-map-leaflet", "children"),
    # Output('log','children'),
    Input("filtered-facilities-store", "data"),
    Input("selected-facility-store", "data"),
)
def update_map(jsonified_filtered_facilities, jsonified_selected_facility):
    # its possible this callback could be called before a filtering step has taken place.
    try:
        dff = pd.read_json(jsonified_filtered_facilities, orient="records")
    except:
        dff = df

    try:
        dff_selected = pd.read_json(jsonified_selected_facility, orient="records")
    except:
        dff_selected = pd.DataFrame()

    if not dff_selected.empty:
        log = dff_selected.name
    else:
        log = "no site selected"

    leaflet_map = create_facility_map_leaflet(dff, dff_selected)

    return leaflet_map  # , log


@dash.callback(
    Output("selected-facility-store", "data"),
    Output("sortable-facility-table", "selected_cells"),
    Output("sortable-facility-table", "active_cell"),
    Input({"id": ALL, "type": "facility"}, "n_clicks"),
    Input("sortable-facility-table", "active_cell"),
    Input("country_selector", "value"),
    Input("facilitytype_selector", "value"),
    Input("infrastructure_selector", "value"),
    Input("availabledata_selector", "value"),
)
def select_facility(
    n_clicks,
    active_cell,
    countries_selected="",
    facilitytypes_selected="",
    infrastructure_selected="",
    availabledata_selected="",
):

    # create default values; these may be overwritten
    dff_selected = pd.DataFrame(columns=df.columns)

    # first establish where the trigger came from

    trigger = dash.callback_context.triggered_id

    trigger_component = ""

    if isinstance(trigger, str):
        # active cell is associated with a string id
        log = "string"
        log = trigger
        if trigger == "sortable-facility-table":
            trigger_component = "sortable-facility-table"
    # elif isinstance(trigger,list):
    #    log = "list"
    elif isinstance(trigger, dict):
        log = "dict"
        trigger_component = "facility-map-leaflet"

    if trigger_component == "facility-map-leaflet":
        # then the trigger was the map
        log = "triggered by the map"
        if not any(n_clicks):
            log = "no clicks on map"
            return
        else:
            log = "clicks on map"
            # now get the selected marker
            clickedMarker = dash.callback_context.triggered_id
            row_id = clickedMarker["id"].rsplit(".", 1)[-1]
            dff_selected = df[df.facility_id == int(row_id)]
            log = "Clicked on marker.{}".format(row_id)

    if trigger_component == "sortable-facility-table":
        # then the trigger was the table
        log = "triggered by the table"
        # get the selected cell
        if active_cell:
            dff_selected = df[df.facility_id == active_cell["row_id"]]
        log = active_cell["row_id"]

    # and finally, clear the selections
    selected_cells = []
    active_cell_out = None

    # update the data store (works when empty, too)
    selected_facility_store = dff_selected.to_json(orient="records")

    return selected_facility_store, selected_cells, active_cell_out


@dash.callback(
    Output("tabs-title", "children"),
    Output("tab-desc", "children"),
    Output("tab-infrastructure", "children"),
    Output("tab-infrastructure", "disabled"),
    Output("tab-availabledata", "children"),
    Output("tab-availabledata", "disabled"),
    Output("card-tabs", "active_tab"),
    Input("selected-facility-store", "data"),
)
def update_information_tabs(jsonified_selected_facility):

    # set default values
    tabs_title_element = html.H4(
        [html.I(className="fa-solid fa-circle-info"), " ", "Facility information"]
    )
    tab_description_element = html.P(
        "Click on a facility on the map or in the table to find out more"
    )
    tab_infrastructure_element = []
    tab_infrastructure_disabled = True
    tab_availabledata_element = []
    tab_availabledata_disabled = True

    # reset the focus
    active_tab = "tab-1"

    if jsonified_selected_facility == "":
        dff_selected = pd.DataFrame()
    else:
        dff_selected = pd.read_json(jsonified_selected_facility, orient="records")

    if len(dff_selected) >= 1:
        tabs_title_element = get_card_facility_title_element(dff_selected)

        tab_description_element = get_card_facility_description_element(dff_selected)

        if not dff_selected["infrastructure_list"].isnull().values.any():
            tab_infrastructure_element = get_card_infrastructure_element(dff_selected)
            tab_infrastructure_disabled = False
        else:
            tab_infrastructure_element = html.P(
                "no information about infrastructure available"
            )
            tab_infrastructure_disabled = True

        if not dff_selected["availabledata_list"].isnull().values.any():
            tab_availabledata_element = get_card_availabledata_element(dff_selected)
            tab_availabledata_disabled = False
        else:
            tab_availabledata_element = html.P("no information about data available")
            tab_availabledata_disabled = True

    return (
        tabs_title_element,
        tab_description_element,
        tab_infrastructure_element,
        tab_infrastructure_disabled,
        tab_availabledata_element,
        tab_availabledata_disabled,
        active_tab,
    )
