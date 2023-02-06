import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

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

# specific to this app
import country_converter as coco
import gspread
from datetime import date


# ------------------------------------
# Register this page and add meta data
# ------------------------------------

dash.register_page(
    __name__,
    title="Wind lidar usage",
    name="Wind lidar usage",
    description="Interactive results of a survey about how wind lidar are used in the wind energy industry",
    path="/lidar_usage_survey2022",
    image="images/explorer.png",
)

# --------------------
# Utility functions
# --------------------

# Round up / down to nearest _x_
# https://stackoverflow.com/a/65725123/2514568
def round_up_to_base(x, base=10):
    return x + (base - x) % base


def round_down_to_base(x, base=10):
    return x - (x % base)


# --------------------
# Default categories
# --------------------
def default_category_order(category):
    if category == "role":
        return [
            "Consultant",
            "Project developer",
            "Project owner",
            "Project operator",
            "N/A",
        ]
    if category == "project_stage":
        return [
            "Site prospecting",
            "Pre construction",
            "Installation",
            "Commissioning",
            "Operational",
            "Repowering",
            "Decommissioning",
            "N/A",
        ]
    if category == "land_offshore":
        return ["On land", "Offshore", "N/A"]
    if category == "measurement_goal":
        return [
            "Site prospecting",
            "Wind resource assessment",
            "Power performance test",
            "Wind characterisation",
            "Power performance testing",
            "Wind turbine control",
            "Wind plant control",
            "N/A",
        ]
    if category == "lidar_type_count":
        return [
            "n_gb_vp",
            "n_gb_s",
            "n_nm_fl",
            "n_nm_s",
            "n_bm_vp",
            "n_vm_vp",
            "n_vm_s",
        ]
    if category == "lidar_type_code":
        return [
            "gb / vp",
            "gb / s",
            "nm / fl",
            "nm / s",
            "bm / vp",
            "vm / vp",
            "vm / s",
        ]
    if category == "lidar_type_short_name":
        return [
            "ground / profiling",
            "ground / scanning",
            "nacelle / forward-looking",
            "nacelle / scanning",
            "buoy / profiling",
            "vessel / profiling",
            "vessel / scanning",
        ]
    if category == "lidar_type_long_name":
        return [
            "Ground-based, vertically-profiling",
            "Ground-based, scanning",
            "Nacelle-mounted, forward-looking",
            "Nacelle-mounted, scanning",
            "Buoy-mounted, vertically-profiling",
            "Vessel-mounted, vertically-profiling",
            "Vessel-mounted, scanning",
        ]


# --------------------
# Get and prepare data
# --------------------


def fetch_form_responses():
    sa = gspread.service_account(filename=".secrets/lidars-per-mw-fae432341abd.json")
    sheet = sa.open("lidar-per-mw-survey responses")
    work_sheet = sheet.worksheet("Form responses 1")
    df_in = pd.DataFrame(work_sheet.get_all_records())

    return df_in


# df_in = fetch_form_responses()


def prepare_form_responses(df_in):
    # Rename the columns
    # map them using a dictionary (column names may change)
    df_in.rename(
        columns={
            "Your role in the project": "role",
            "Was the project on land or offshore?": "land_offshore",
            "What was the project stage?": "project_stage",
            "What was the rated power of the whole project?": "project_power",
            "What continent was the project on?": "continent",
            "What country was the project in?": "country_name",
            "When did wind lidar measurements start?": "year_started",
            "What was the goal of the measurements?": "measurement_goal",
            "How many, and what type of lidar were used? [Ground-based vertically-profiling lidar]": "n_gb_vp",
            "How many, and what type of lidar were used? [Ground-based scanning lidar]": "n_gb_s",
            "How many, and what type of lidar were used? [Nacelle-mounted forward-looking lidar]": "n_nm_fl",
            "How many, and what type of lidar were used? [Nacelle-mounted scanning lidar]": "n_nm_s",
            "How many, and what type of lidar were used? [Buoy-mounted vertically-profiling lidar]": "n_bm_vp",
            "How many, and what type of lidar were used? [Vessel-mounted vertically-profiling lidar]": "n_vm_vp",
            "How many, and what type of lidar were used? [Vessel-mounted scanning lidar]": "n_vm_s",
            "Did you also use meteorological (met) towers?": "used_mettowers",
        },
        inplace=True,
    )

    # replace missing data in lidar columns with a zero
    lcols = default_category_order("lidar_type_count")
    for col in lcols:
        df_in[col] = df_in[col].replace("", 0.0).astype(float)

    # add an extra column with the total number of lidar
    df_in["n_lidar_project"] = float("nan")
    for index, row in df_in.iterrows():
        df_in.loc[index, "n_lidar_project"] = row[lcols].sum()

    # replace missing data in number columns with na
    float_cols = ["year_started", "project_power"]

    for col in float_cols:
        df_in[col] = df_in[col].replace("", float("nan"))

    # replace missing data in text columns with "N/A"
    text_cols = [
        "role",
        "project_stage",
        "measurement_goal",
        "continent",
        "country_name",
        "land_offshore",
    ]

    for col in text_cols:
        df_in[col] = df_in[col].replace("", "N/A").astype(str)

    # map english-language country names to codes
    # apply solution at https://stackoverflow.com/questions/16253060/how-to-convert-country-names-to-iso-3166-1-alpha-2-values-using-python

    df_in["country_iso3"] = df_in.country_name

    df_in["country_iso3"] = coco.convert(names=df_in.country_name.tolist(), to="ISO3")

    # update the category values to show any "non default" values
    for index, row in df_in.iterrows():
        if row["role"] not in default_category_order("role"):
            # update df_in
            df_in.loc[index, "role"] = "Other: " + row["role"]
        if row["project_stage"] not in default_category_order("project_stage"):
            # update df_in
            df_in.loc[index, "project_stage"] = "Other: " + row["project_stage"]
        if row["measurement_goal"] not in default_category_order("measurement_goal"):
            # update df_in
            df_in.loc[index, "measurement_goal"] = "Other: " + row["measurement_goal"]

    # add a dummy count column to simplify some plotting
    df_in["count"] = 1.0

    return df_in


# df_in_clean = prepare_form_responses(df_in)

# ------------------
# Convert wide data to long data
# ------------------


def convert_form_responses_to_long(df_in):
    df_long = pd.DataFrame(
        columns=[
            "Timestamp",
            "land_offshore",
            "project_stage",
            "project_power",
            "continent",
            "country_name",
            "country_iso3",
            "year_started",
            "measurement_goal",
            "n_mettowers",
            "lidar_type_code",
            "lidar_type_short_name",
            "lidar_type_long",
            "n_lidar_type",
            "n_lidar_project",
            "count",
        ]
    )

    lcols = default_category_order("lidar_type_count")
    ltype_code = default_category_order("lidar_type_code")
    ltype_short_name = default_category_order("lidar_type_short_name")
    ltype_long_name = default_category_order("lidar_type_long_name")

    for index, row in df_in.iterrows():

        for index, n_ltype in enumerate(lcols):
            # get the data
            # note that we add a dummy "count" variable to simplify some plotting
            df_long.loc[len(df_long)] = [
                row.Timestamp,
                row.land_offshore,
                row.project_stage,
                row.project_power,
                row.continent,
                row.country_name,
                row.country_iso3,
                row.year_started,
                row.measurement_goal,
                row.used_mettowers,
                ltype_code[index],
                ltype_short_name[index],
                ltype_long_name[index],
                row[n_ltype],
                row.n_lidar_project,
                row.count,
            ]

    # add the number of devices per megawatt
    df_long["lidars_per_MW"] = df_long.n_lidar_type / df_long.project_power

    return df_long


# df_long = convert_form_responses_to_long(df_in_clean)

# --------------------
# Get categories that are present in the responses
# --------------------


def actual_category_order(df_in, category):
    # get a starting point for the orders
    actual_category_order = default_category_order(category)
    for category_used in df_in[category].unique().tolist():
        if category_used not in actual_category_order:
            actual_category_order.append(category_used)

    return actual_category_order


# ---------------------
# Create a map of the responses
# ---------------------


def fig_map_responses(df_plot):

    # get the sum of responses per country
    df_response_pivot = pd.pivot_table(
        df_plot, values="count", index="country_iso3", aggfunc=np.sum
    ).reset_index()

    # create the figure
    fig = px.choropleth(
        df_response_pivot,
        color="count",
        range_color=(1, df_response_pivot["count"].max() + 1),
        locationmode="ISO-3",
        locations="country_iso3",
        labels={"count": "Responses per country"},
        color_continuous_scale=[(0.00, "white"), (0.50, "#17A9AE"), (1.0, "black")],
    )

    # modify the presentation of the map
    fig.update_layout(
        geo=dict(
            showcoastlines=False,
            projection_type="equirectangular",
        ),
        coloraxis_showscale=True,
    )

    fig.update_coloraxes(
        colorbar_orientation="h",
        colorbar_x=0.5,
        colorbar_yanchor="top",
        colorbar_y=-0.05,
        colorbar_title_side="bottom",
    )
    fig.update_traces(marker_line_color="lightgray")

    # set up the colorbar (legend)

    # remove margins
    fig.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
    )

    fig = fig_styling(fig)

    return fig


# -----------------------------
# Create a parallel categories plot for the responses
# -----------------------------


def fig_pc_responses(df_plot):

    # using solution from https://stackoverflow.com/questions/72749285/changing-the-base-color-of-ploty-express-parallel-categories-diagram

    # implement using parcats to specify orders
    fig = go.Figure(
        go.Parcats(
            dimensions=[
                {
                    "label": "Respondent Role",
                    "values": df_plot["role"].tolist(),
                    "categoryorder": "array",
                    #    "categoryarray": role_category_order,
                },
                {
                    "label": "Project Stage",
                    "values": df_plot["project_stage"].tolist(),
                    "categoryorder": "array",
                    #    "categoryarray": project_stage_category_order,
                },
                {
                    "label": "Measurement Goal",
                    "values": df_plot["measurement_goal"],
                    "categoryorder": "array",
                    #    "categoryarray": measurement_goal_category_order,
                },
                {
                    "label": "On / offshore",
                    "values": df_plot["land_offshore"],
                    "categoryorder": "array",
                    "categoryarray": actual_category_order(df_plot, "land_offshore"),
                },
            ],
            line={
                "color": df_plot["count"],
                "colorscale": [[0, "white"], [1, "#17A9AE"]],
                # "showscale": True,
                # "cmin": 0,
                # "cmax": df_metadata["project_power"].max(),
                # "color": df_metadata["project_power"],
                "shape": "hspline",
            },
        )
    )

    # fig_pa.update(layout_coloraxis_showscale=True)
    # fig_pa.update_traces(line_colorbar_orientation="h")
    # fig_pa.update_traces(line_colorbar_y=-0.3)
    # fig_pa.update_traces(line_colorbar_title={"text": "Project size (MW)"})

    fig.update_layout(margin=dict(t=0, b=0, l=50, r=15))

    fig = fig_styling(fig)

    return fig


# -----------------------------
# Plot the time series of projects
# -----------------------------
def fig_ts_p(df_plot):
    fig = px.scatter(
        df_plot,
        x="year_started",
        y="project_power",
        color="measurement_goal",
        size="n_lidar_project",
        category_orders={
            "measurement_goal": actual_category_order(df_plot, "measurement_goal")
        },
    )

    fig.update_xaxes(
        title="Year started", range=[2004, round_up_to_base(date.today().year, 2)]
    )
    fig.update_yaxes(
        title="Project power (MW)",
        range=[0, round_up_to_base(df_plot.project_power.max(), 200)],
    )

    fig.update_layout(
        legend=dict(
            title="Measurement goal", yanchor="top", y=0.95, xanchor="left", x=0.05
        ),
        margin=dict(t=0, b=0, l=0, r=0),
    )

    fig = fig_styling(fig)

    return fig


# -----------------------------
# Get the number of lidars per MW
# -----------------------------
def fig_lidars_per_MW(df_plot):

    fig = px.scatter(
        df_plot[df_plot["n_lidar_type"] > 0],
        x="lidar_type_short_name",
        y="lidars_per_MW",
        range_y=[0, round_up_to_base(df_plot["lidars_per_MW"].max(), 0.05)],
        size="project_power",
        color="measurement_goal",
        category_orders={
            "measurement_goal": actual_category_order(df_plot, "measurement_goal"),
            "lidar_type_short_name": actual_category_order(
                df_plot, "lidar_type_short_name"
            ),
        },
        labels={
            "lidars_per_MW": "Lidars used per project MW",
            "lidar_type_short_name": "Lidar type",
        },
    )

    # fig.update_xaxes(title = "Lidar type")
    # fig.update_yaxes(title = "Lidars used per MW of project size")
    fig.update_layout(
        legend=dict(
            title="Measurement goal", yanchor="top", y=0.95, xanchor="right", x=0.95
        ),
        margin=dict(t=20, b=0, l=0, r=0),
        xaxis=dict(tickangle=90),
    )

    fig = fig_styling(fig)

    return fig


# -----------------------------
# Apply theming to the figures
# -----------------------------


def fig_styling(fig):
    fig.update_layout(
        font_family="../assets/fonts/raleway-v28-latin-regular.ttf",
        font_color="#38325B",
        title_font_family="../assets/fonts/montserrat-v25-latin-regular.ttf",
        title_font_color="#38325B",
        legend_title_font_color="#38325B",
    )
    return fig


# -----------------------------
# Create the layout for this page
# -----------------------------


def layout():

    # read the google data each time the page is refreshed
    df_in = fetch_form_responses()
    df_in_clean = prepare_form_responses(df_in)
    df_long = convert_form_responses_to_long(df_in_clean)

    # now generate the layout
    layout = dbc.Container(
        [
            # reload the data
            # title row
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [html.H1("Wind Lidar Usage Survey Results")], width=12
                            ),
                        ],
                        className="title h-10 pt-2 mb-2",
                    ),
                ]
            ),
            # Alerts
            html.Div(
                [
                    dbc.Alert(
                        [
                            html.H4("Demonstration only!", className="alert-heading"),
                            html.P(
                                "This is a work in progress and data are for demonstration purposes. The actual survey will open for responses in 2023. Results will be made available as they are collected."
                            ),
                        ],
                        color="warning",
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
                    # survey information row
                    dbc.Row(
                        [
                            # Number of responses
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.H4(
                                                        [
                                                            str(
                                                                len(
                                                                    df_in_clean.Timestamp.unique()
                                                                )
                                                            )
                                                            + " responses"
                                                        ],
                                                        className="card-title",
                                                    ),
                                                    html.Ul(
                                                        children=[
                                                            html.Li(
                                                                str(
                                                                    len(
                                                                        df_in_clean.continent.unique()
                                                                    )
                                                                )
                                                                + " continents"
                                                            ),
                                                            html.Li(
                                                                str(
                                                                    len(
                                                                        df_in_clean.country_name.unique()
                                                                    )
                                                                )
                                                                + " countries"
                                                            ),
                                                        ]
                                                    ),
                                                    dbc.Button(
                                                        [
                                                            html.I(
                                                                className="fa-solid fa-map-location-dot"
                                                            ),
                                                            " Add yours",
                                                        ],
                                                        href="".join(
                                                            "https://forms.gle/ALAAa6KpztHH8Uh6A"
                                                        ),
                                                        target="_blank",
                                                        color="primary",
                                                        disabled=False,
                                                        className="me-1 btn btn-primary btn-sm",
                                                    ),
                                                ]
                                            )
                                        ]
                                    )
                                ],
                                class_name="col-12 col-md-4 col-lg-2 pb-md-4 pb-4",
                            ),
                            # Map of responses
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.H4(
                                                        "Responses per country",
                                                        className="card-title",
                                                    ),
                                                    dcc.Graph(
                                                        id="respondent_map",
                                                        figure=fig_map_responses(
                                                            df_in_clean
                                                        ),
                                                        style={"height": "300px"},
                                                        responsive=True,
                                                    ),
                                                ]
                                            )
                                        ]
                                    )
                                ],
                                class_name="col-12 col-md-8 col-lg-4 pb-md-4 pb-4",
                            ),
                            # Respondent types
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.H4(
                                                        "Applications",
                                                        className="card-title",
                                                    ),
                                                    dcc.Graph(
                                                        id="fig_pa",
                                                        figure=fig_pc_responses(
                                                            df_in_clean
                                                        ),
                                                        style={"height": "300px"},
                                                        responsive=True,
                                                    ),
                                                ]
                                            )
                                        ]
                                    ),
                                ],
                                class_name="col-12 col-lg-6 pb-4",
                            ),
                            # time series of power
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    dbc.Row(
                                                        [
                                                            html.H2(
                                                                "Measurement campaigns",
                                                                className="card-title",
                                                            ),
                                                        ]
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    html.H5("On Land"),
                                                                    # the figure itself
                                                                    dcc.Graph(
                                                                        figure=fig_ts_p(
                                                                            df_in_clean[
                                                                                df_in_clean[
                                                                                    "land_offshore"
                                                                                ]
                                                                                == "On land"
                                                                            ]
                                                                        ),
                                                                        id="timeseries_power",
                                                                        responsive=True,
                                                                        style={
                                                                            "height": "300px"
                                                                        },
                                                                    ),
                                                                ],
                                                                class_name="col-12 col-lg-4",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    html.H5("Offshore"),
                                                                    # the figure itself
                                                                    dcc.Graph(
                                                                        figure=fig_ts_p(
                                                                            df_in_clean[
                                                                                df_in_clean[
                                                                                    "land_offshore"
                                                                                ]
                                                                                == "Offshore"
                                                                            ]
                                                                        ),
                                                                        id="timeseries_power",
                                                                        responsive=True,
                                                                        style={
                                                                            "height": "300px"
                                                                        },
                                                                    ),
                                                                ],
                                                                class_name="col-12 col-lg-4",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    html.H5("Unknown"),
                                                                    # the figure itself
                                                                    dcc.Graph(
                                                                        figure=fig_ts_p(
                                                                            df_in_clean[
                                                                                df_in_clean[
                                                                                    "land_offshore"
                                                                                ]
                                                                                == "N/A"
                                                                            ]
                                                                        ),
                                                                        id="timeseries_power",
                                                                        responsive=True,
                                                                        style={
                                                                            "height": "300px"
                                                                        },
                                                                    ),
                                                                ],
                                                                class_name="col-12 col-lg-4",
                                                            ),
                                                        ],
                                                    ),
                                                ],
                                            )
                                        ]
                                    )
                                ],
                                class_name="col-12 pb-4",
                            ),
                            # Lidars per MW
                            dbc.Col(
                                [
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.H2(
                                                        "Lidar usage rates",
                                                        className="card-title",
                                                    ),
                                                    dbc.Row(
                                                        [
                                                            dbc.Col(
                                                                [
                                                                    html.H5(
                                                                        "On land",
                                                                        className="card-title",
                                                                    ),
                                                                    dcc.Graph(
                                                                        figure=fig_lidars_per_MW(
                                                                            df_long[
                                                                                df_long[
                                                                                    "land_offshore"
                                                                                ]
                                                                                == "On land"
                                                                            ]
                                                                        ),
                                                                        id="lidars_per_MW_land",
                                                                        responsive=True,
                                                                        style={
                                                                            "height": "400px"
                                                                        },
                                                                    ),
                                                                ],
                                                                className="col-12 col-lg-4",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    html.H5(
                                                                        "Offshore",
                                                                        className="card-title",
                                                                    ),
                                                                    dcc.Graph(
                                                                        figure=fig_lidars_per_MW(
                                                                            df_long[
                                                                                df_long[
                                                                                    "land_offshore"
                                                                                ]
                                                                                == "Offshore"
                                                                            ]
                                                                        ),
                                                                        id="lidars_per_MW_offshore",
                                                                        responsive=True,
                                                                        style={
                                                                            "height": "400px"
                                                                        },
                                                                    ),
                                                                ],
                                                                className="col-12 col-lg-4",
                                                            ),
                                                            dbc.Col(
                                                                [
                                                                    html.H5(
                                                                        "Unknown",
                                                                        className="card-title",
                                                                    ),
                                                                    dcc.Graph(
                                                                        figure=fig_lidars_per_MW(
                                                                            df_long[
                                                                                df_long[
                                                                                    "land_offshore"
                                                                                ]
                                                                                == "N/A"
                                                                            ]
                                                                        ),
                                                                        id="lidars_per_MW_unknown",
                                                                        responsive=True,
                                                                        style={
                                                                            "height": "400px"
                                                                        },
                                                                    ),
                                                                ],
                                                                className="col-12 col-lg-4",
                                                            ),
                                                        ]
                                                    ),
                                                ],
                                            )
                                        ]
                                    ),
                                ],
                                class_name="col-12 pb-2",
                            ),
                        ],
                    ),
                ],
                className="content",
                style={"min-height": "80vh"},
            ),
        ],
        fluid=False,
        className="dbc h-80",
        style={"min-height": "80vh"},
    )

    return layout


# -----------------------------
# Callbacks
# -----------------------------
