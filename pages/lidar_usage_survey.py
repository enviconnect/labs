import base64

# math routines
import math
from collections import Counter
from datetime import date
from io import BytesIO

# specific to this app
import country_converter as coco
import dash
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_loading_spinners
import gspread

# import numpy
import numpy as np

# import pandas (needed for the data table)
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# import pyyaml module
import yaml
from dash import Dash, Input, Output, State, dash_table, dcc, html
from dash.dependencies import ALL, Input, Output
from wordcloud import WordCloud

# set up Dash
# from jupyter_dash import JupyterDash


# ------------------------------------
# Register this page and add meta data
# ------------------------------------

dash.register_page(
    __name__,
    title="Wind lidar applications",
    name="Wind lidar applications",
    description="Interactive results of a survey about how wind lidar are used in the wind energy industry",
    path="/lidar_applications_survey",
    image="images/lidar_usage_survey.png",
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
            "Wind farm developer",
            "Wind farm owner",
            "Wind farm operator",
            "N/A",
        ]
    if category == "project_stage":
        return [
            "Site prospecting",
            "Pre construction",
            "Construction",
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
    if category == "lidar_type_rented_count":
        return [
            "n_gb_vp_rented",
            "n_gb_s_rented",
            "n_nm_fl_rented",
            "n_nm_s_rented",
            "n_bm_vp_rented",
            "n_vm_vp_rented",
            "n_vm_s_rented",
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
    # sa = gspread.service_account(
    #    filename=".secrets/lidars-per-mw-fae432341abd.json")
    # sheet = sa.open("lidar applications survey responses")
    # work_sheet = sheet.worksheet("Form responses 1")
    # df_in = pd.DataFrame(work_sheet.get_all_records())

    df_in = pd.read_pickle("data/lidar_usage_survey/lidar_usage_survey.pkl")

    return df_in


# df_in = fetch_form_responses()


def prepare_form_responses(df_in):
    # Rename the columns
    # map them using a dictionary (column names may change)
    df_in.rename(
        columns={
            "Your role in the deployment": "role",
            "Was the wind farm on land or offshore?": "land_offshore",
            "What stage in its lifecycle was the wind farm development at?": "project_stage",
            "What was the rated power of the wind farm?": "project_power",
            "What continent was the wind lidar deployment on?": "continent",
            "What country was the wind lidar deployment in?": "country_name",
            "What year did the wind lidar measurements start?": "year_started",
            "What was the goal of the measurements?": "measurement_goal",
            "How many, and what type of lidar were used? [Ground-based vertically-profiling lidar]": "n_gb_vp",
            "How many, and what type of lidar were used? [Ground-based scanning lidar]": "n_gb_s",
            "How many, and what type of lidar were used? [Nacelle-mounted forward-looking lidar]": "n_nm_fl",
            "How many, and what type of lidar were used? [Nacelle-mounted scanning lidar]": "n_nm_s",
            "How many, and what type of lidar were used? [Buoy-mounted vertically-profiling lidar]": "n_bm_vp",
            "How many, and what type of lidar were used? [Vessel-mounted vertically-profiling lidar]": "n_vm_vp",
            "How many, and what type of lidar were used? [Vessel-mounted scanning lidar]": "n_vm_s",
            "How many met towers did you use?": "n_mettowers",
            "What was the reason for using met towers?": "mettower_reasons",
            "How many, and what type of lidar were rented? [Ground-based vertically-profiling lidar]": "n_gb_vp_rented",
            "How many, and what type of lidar were rented? [Ground-based scanning lidar]": "n_gb_s_rented",
            "How many, and what type of lidar were rented? [Nacelle-mounted forward-looking lidar]": "n_nm_fl_rented",
            "How many, and what type of lidar were rented? [Nacelle-mounted scanning lidar]": "n_nm_s_rented",
            "How many, and what type of lidar were rented? [Buoy-mounted vertically-profiling lidar]": "n_bm_vp_rented",
            "How many, and what type of lidar were rented? [Vessel-mounted vertically-profiling lidar]": "n_vm_vp_rented",
            "How many, and what type of lidar were rented? [Vessel-mounted scanning lidar]": "n_vm_s_rented",
            "Is this real data?": "real_data",
            "Top 3 needs": "top_needs",
            "Top 3 challenges": "top_challenges",
            "Top 3 opportunities": "top_opportunities"},
        inplace=True,
    )

    # replace missing data in lidar columns with a zero
    lcols = default_category_order("lidar_type_count")
    # for col in lcols:
    # catch the empty value
    df_in[lcols] = df_in[lcols].replace("", 0.0).astype(float)
    # catch the "more than 5" response
    df_in[lcols] = df_in[lcols].replace("More than 5", 6.0).astype(float)

    # add an extra column with the total number of lidar
    df_in["n_lidar_project"] = float("nan")
    for index, row in df_in.iterrows():
        df_in.loc[index, "n_lidar_project"] = row[lcols].sum()

    # add an extra column with the total number of _rented_ lidar
    lrentedcols = default_category_order("lidar_type_rented_count")
    # for col in lrentedcols:
    # catch the empty value
    df_in[lrentedcols] = df_in[lrentedcols].replace("", 0.0).astype(float)
    # catch the "more than 5" response
    df_in[lrentedcols] = df_in[lrentedcols].replace(
        "More than 5", 6.0).astype(float)

    df_in["n_lidar_project_rented"] = float("nan")
    for index, row in df_in.iterrows():
        df_in.loc[index, "n_lidar_project_rented"] = row[lrentedcols].sum()

    # replace missing data in number columns with na
    float_cols = ["year_started", "project_power"]

    # for col in float_cols:
    df_in[float_cols] = df_in[float_cols].replace("", float("nan"))

    # replace missing data in text columns with "N/A"
    text_cols = [
        "role",
        "project_stage",
        "measurement_goal",
        "continent",
        "country_name",
        "land_offshore",
    ]

    # for col in text_cols:
    df_in[text_cols] = df_in[text_cols].replace("", "N/A").astype(str)

    # map english-language country names to codes
    # apply solution at
    # https://stackoverflow.com/questions/16253060/how-to-convert-country-names-to-iso-3166-1-alpha-2-values-using-python

    df_in["country_iso3"] = df_in.country_name

    df_in["country_iso3"] = coco.convert(
        names=df_in.country_name.tolist(), to="ISO3")

    # update the category values to show any "non default" values
    for index, row in df_in.iterrows():
        if row["role"] not in default_category_order("role"):
            # update df_in
            df_in.loc[index, "role"] = "Other: " + row["role"]
        if row["project_stage"] not in default_category_order("project_stage"):
            # update df_in
            df_in.loc[index, "project_stage"] = "Other: " + \
                row["project_stage"]
        if row["measurement_goal"] not in default_category_order(
                "measurement_goal"):
            # update df_in
            df_in.loc[index, "measurement_goal"] = "Other: " + \
                row["measurement_goal"]

    # convert text in real_data to True/False
    df_in = df_in.replace({'real_data': {'Yes': True, 'No': False}})

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
            "n_lidar_project_rented",
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
            # note that we add a dummy "count" variable to simplify some
            # plotting
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
                row.n_mettowers,
                ltype_code[index],
                ltype_short_name[index],
                ltype_long_name[index],
                row[n_ltype],
                row.n_lidar_project,
                row.n_lidar_project_rented,
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
        labels={"count": "Lidar deployments per country"},
        color_continuous_scale=[
            (0.0, "#cbf1f2"), (0.50, "#17A9AE"), (1.0, "black")],
    )

    # modify the presentation of the map
    fig.update_layout(
        geo=dict(
            projection_type="equirectangular",
            showocean=True,
            oceancolor="lightblue",
            showcoastlines=False,
            showland=True,
            landcolor="#8c510A",
            showcountries=True,
            countrywidth=0.0,
            countrycolor="#17A9AE",
            showlakes=False,
            showframe=False,
        ),
        coloraxis=dict(colorbar=dict(dtick=1,
                                     thickness=20)),
        coloraxis_showscale=True,
    )

    fig.update_coloraxes(
        colorbar_orientation="h",
        colorbar_x=0.5,
        colorbar_yanchor="top",
        colorbar_y=-0.05,
        colorbar_title_side="bottom",
    )

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

    # using solution from
    # https://stackoverflow.com/questions/72749285/changing-the-base-color-of-ploty-express-parallel-categories-diagram

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
                    "label": "Wind Farm Status",
                    "values": df_plot["project_stage"].tolist(),
                    "categoryorder": "array",
                    #    "categoryarray": project_stage_category_order,
                },
                {
                    "label": "Application",
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
    fig.update_traces(hoverinfo='skip')
    # fig_pa.update_traces(line_colorbar_orientation="h")
    # fig_pa.update_traces(line_colorbar_y=-0.3)
    # fig_pa.update_traces(line_colorbar_title={"text": "Project size (MW)"})

    fig.update_layout(margin=dict(t=20, b=0, l=60, r=20),
                      hovermode=False)

    fig = fig_styling(fig)

    return fig


# -----------------------------
# Plot the time series of projects
# -----------------------------
def fig_ts_p(df_plot, ymax=[]):

    # make sure that we only plot data where we know...
    # 1. if it is on, or offshore
    df_plot = df_plot[df_plot["land_offshore"].notna()]
    # 2. What year it took place
    df_plot = df_plot[df_plot["year_started"].notna()]

    if not ymax:
        ymax = round_up_to_base(df_plot.project_power.max(), 200) + 100

    fig = px.scatter(
        df_plot,
        x="year_started",
        y="project_power",
        facet_col_wrap=1,
        facet_col="land_offshore",
        facet_row_spacing=0.125,
        color="measurement_goal",
        # size="n_lidar_project",
        category_orders={
            "measurement_goal": actual_category_order(df_plot, "measurement_goal")
        },
        labels={
            "project_power": "Project power [MW]",
            "year_started": "Year measurement campaign started",
        },
    )

    fig.update_yaxes(
        range=[-20, ymax],
    )

    fig.update_layout(
        hovermode=False,
        legend=dict(title="Application"),
        margin=dict(t=30, b=0, l=0, r=0),
    )

    fig.update_traces(marker=dict(size=10,
                                  line=dict(width=1,
                                            color='DarkSlateGrey')))

    # Format facet labels
    fig.for_each_annotation(lambda a: a.update(text="<span style='font-weight: 500;'>" + a.text.split(
        "=")[-1] + "</span>", font=dict(family="Raleway", size=20, color="#000000"), ))

    fig = fig_styling(fig)

    return fig

# -----------------------------
# Get the number of lidars per campaign
# -----------------------------


def fig_n_lidars(df_plot):
    fig = px.bar(
        df_plot,
        x="n_lidar_project",
        y="count",
        color="measurement_goal",
        barmode="group",
        labels={
            "n_lidar_project": "Number of lidar used",
            "count": "Number of responses",
        },
    )

    fig.update_layout(
        bargap=0.30,
        bargroupgap=0.0,
        hovermode=False,
        legend=dict(title="Application"),
        margin=dict(t=30, b=0, l=0, r=0),
    )

    fig.update_xaxes(tickmode='linear')
    fig.update_yaxes(dtick=1)

    fig.update_traces(marker=dict(line=dict(width=1,
                                            color='DarkSlateGrey')))

    fig = fig_styling(fig)

    return fig

# -----------------------------
# Plot the number of rented lidar
# -----------------------------


def fig_lidar_rental(df_plot):

    xmax = max(df_plot["n_lidar_project"].max(),
               df_plot["n_lidar_project_rented"].max())

    fig = px.scatter(
        df_plot[df_plot["n_lidar_project"] > 0],
        x="n_lidar_project",
        y="n_lidar_project_rented",
        color="measurement_goal",
        labels={
            "n_lidar_project": "Total number of lidar used",
            "n_lidar_project_rented": "Number of rented lidar",
        },
    )

    fig.update_traces(marker=dict(size=10,
                                  line=dict(width=1,
                                            color='DarkSlateGrey')))

    fig.update_layout(
        hovermode=False,
        legend=dict(title="Application"),
        margin=dict(t=30, b=0, l=0, r=0),
    )

    fig.update_xaxes(dtick=1, range=[0, xmax+1])
    fig.update_yaxes(dtick=1, range=[-0.5, xmax+1])

    fig = fig_styling(fig)

    return fig

# -----------------------------
# plot the number of lidars per MW
# -----------------------------


def fig_lidars_per_MW(df_plot):

    fig = px.scatter(
        df_plot[df_plot["n_lidar_type"] > 0],
        y="lidar_type_short_name",
        x="lidars_per_MW",
        color="measurement_goal",
        facet_col="land_offshore",
        category_orders={
            "measurement_goal": actual_category_order(df_plot, "measurement_goal"),
            "lidar_type_short_name": default_category_order("lidar_type_short_name"),
        },
        labels={
            "lidars_per_MW": "Lidars used per MW of wind farm capacity",
            "lidar_type_short_name": "Lidar type",
        },
    )

    # Format facet labels
    fig.for_each_annotation(lambda a: a.update(text="<span style='font-weight: 500;'>" + a.text.split(
        "=")[-1] + "</span>", font=dict(family="Raleway", size=20, color="#000000"), ))

    fig.update_traces(marker=dict(size=10,
                                  line=dict(width=1,
                                            color='DarkSlateGrey')))

    fig.update_layout(
        # scattermode="group",
        # scattergap=0.75,
        hovermode=False,
        legend=dict(
            title="Application",
        ),
        margin=dict(t=30, b=0, l=0, r=0),
    )

    fig = fig_styling(fig)

    return fig

# -----------------------------
# Get the number of met towers per campaign
# -----------------------------


def fig_n_metttowers(df_plot):
    fig = px.bar(
        df_plot,
        x="n_mettowers",
        y="count",
        color="measurement_goal",
        barmode="group",
        labels={
            "n_mettowers": "Number of met towers used per campaign",
            "count": "Number of responses",
        },
    )

    fig.update_layout(
        bargap=0.30,
        bargroupgap=0.0,
        hovermode=False,
        legend=dict(title="Application"),
        margin=dict(t=30, b=0, l=0, r=0),
    )

    fig.update_xaxes(tickmode='linear')
    fig.update_yaxes(dtick=1)

    fig.update_traces(marker=dict(line=dict(width=1,
                                            color='DarkSlateGrey')))

    fig = fig_styling(fig)

    return fig


# -----------------------------
# Create word clouds
# -----------------------------
# https://community.plotly.com/t/wordcloud-in-dash/11407/25
# https://stackoverflow.com/questions/58286251/how-can-i-group-multi-word-terms-when-creating-a-python-wordcloud
#
def fig_word_cloud(word_list):

    flat_word_list = []
    for sublist in word_list:
        for item in sublist.split(", "):
            if len(item) > 0:
                # capitalize the first letter in a string and append
                flat_word_list.append(item[0].upper() + item[1:])

    wc = WordCloud(
        min_word_length=1,
        relative_scaling=1,
        mode="RGBA",
        height=300,
        width=600,
        background_color=None).generate_from_frequencies(
        Counter(flat_word_list))
    wc_img = wc.to_image()

    with BytesIO() as buffer:
        wc_img.save(buffer, 'png')
        fig = base64.b64encode(buffer.getvalue()).decode()

    return fig


# -----------------------------
# Apply theming to the figures
# -----------------------------


def fig_styling(fig):
    fig.update_layout(
        font_family="../assets/fonts/raleway-v28-latin-regular.ttf",
        font_color="#38325B",
        title_font_family="../assets/fonts/raleway-v28-latin-regular.ttf",
        title_font_color="#38325B",
        legend_title_font_color="#38325B",
    )
    return fig

# -----------------------------
# Create layout components, e.g. cards.
# -----------------------------


def title_text():
    title_text = html.H1(
        "Have you ever wondered how everyone else uses wind lidar?", className="title display-4")

    return title_text


def opening_text():
    opening_text = [
        html.P("We were curious as well, so we're doing a survey.",
               className="lead"),
    ]

    return opening_text


def closing_text():
    closing_text = [
        html.H4(
            "Share your experience",
            className="alert-heading"),
        html.P("If you found these results useful, please share how you are using wind lidar too. It'll take you less than 5 minutes."),
        dbc.Button(
            ["Add your experience to the survey"],
            href="".join(
                "https://forms.gle/ALAAa6KpztHH8Uh6A"
            ),
            target="_blank",
            disabled=False,
            className="btn",
            style={"background-color": "#CE1B4C", "border": "none"}
        ),
    ]

    return closing_text


def alert_card(use_real_only=True):
    if use_real_only:
        alert_card = []
    else:
        alert_card = dbc.Alert(
            [
                html.H4(
                    "Includes dummy data",
                    className="alert-heading"),
                html.P(
                    "This survey includes dummy data to help anonymize early answers. The dummy data will be removed once we have more than 10 survey responses."
                ),
            ],
            color="warning",
            className="g-4 mt-4 mb-0"
        )

    return alert_card


def response_count_card(df_in_clean):
    card = dbc.Card(
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
                            + " "
                            + "survey responses"
                        ],
                        className="card-title",
                    ),
                    html.P(
                        [
                            "So far we've got data about "
                            + str(
                                int(
                                    df_in_clean[
                                        "n_lidar_project"
                                    ].sum()
                                )
                            )
                            + " "
                            + "wind lidar, deployed in"
                        ]
                    ),
                    html.Ul(
                        children=[
                            html.Li(
                                str(
                                    len(
                                        df_in_clean.continent.unique()
                                    )
                                )
                                + " continents and"
                            ),
                            html.Li(
                                str(
                                    len(
                                        df_in_clean.country_name.unique()
                                    )
                                )
                                + " countries."
                            ),
                        ]
                    ),
                    html.P(
                        ["These results are updated automatically as people share their experience."]),
                    dbc.Button(
                        ["Add your experience - it'll take you less than 5 minutes"],
                        href="".join(
                            "https://forms.gle/ALAAa6KpztHH8Uh6A"
                        ),
                        target="_blank",
                        disabled=False,
                        className="btn col-12 col-lg-12 mx-auto",
                        style={"background-color": "#CE1B4C", "border": "none",
                               "box-shadow": "0 0.5rem 1.0rem rgba(0, 0, 0, 1.0) !important"}
                    ),

                ]
            )
        ]
    )

    return card


def response_map_card(df_in_clean):
    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4(
                        "Where are lidar used?",
                        className="card-title",
                    ),
                    dcc.Graph(
                        id="respondent_map",
                        figure=fig_map_responses(
                            df_in_clean
                        ),
                        style={
                            "height": "300px"},
                        responsive=True,
                    ),
                ]
            )
        ]
    )
    return card


def respondent_type_card(df_in_clean):
    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4(
                        "Who uses lidars for which application?",
                        className="card-title",
                    ),
                    dcc.Graph(
                        id="fig_pa",
                        figure=fig_pc_responses(
                            df_in_clean
                        ),
                        style={
                            "height": "300px"},
                        responsive=True,
                    ),
                ]
            )
        ]
    ),

    return card


def timeline_card(df_in_clean):
    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H2(
                        "Has wind lidar use changed over the years?",
                        className="card-title",
                    ),
                    # the
                    # figure
                    # itself
                    dcc.Graph(
                        figure=fig_ts_p(
                            df_in_clean,
                        ),
                        id="timeseries_power",
                        style={
                            "height": "500px"
                        },
                        responsive=True,
                    ),
                    html.Small(
                        [
                            html.I(
                                className="fa-solid fa-circle-info"
                            ),
                            " ",
                            "Double click on a data series in the legend - e.g. 'power performance testing' - to only show data for that application",
                        ]
                    ),
                ]
            )
        ]
    )

    return card


def lidars_per_campaign_card(df_in_clean):
    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H2(
                        "How many wind lidar are used per campaign?",
                        className="card-title",
                    ),
                    dcc.Graph(
                        figure=fig_n_lidars(
                            df_in_clean
                        ),
                        id="lidars_per_campaign",
                        style={
                            "height": "300px"
                        },
                        responsive=True,
                    ),
                ],
            ),
        ]
    )
    return card


def lidar_rental_card(df_in_clean):
    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H2(
                        "How many wind lidars are rented per campaign?",
                        className="card-title"
                    ),

                    dcc.Graph(
                        figure=fig_lidar_rental(
                            df_in_clean
                        ),
                        id="lidars_rented",
                        responsive=True,
                        style={
                            "height": "300px"
                        },
                    ),
                ],
            ),
        ]
    )
    return card


def masts_per_campaign_card(df_in_clean):
    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H2(
                        "Are wind lidar used with met masts?",
                        className="card-title",
                    ),

                    dcc.Graph(
                        figure=fig_n_metttowers(
                            df_in_clean
                        ),
                        id="towers_per_campaign",
                        responsive=True,
                        style={
                            "height": "300px"
                        },
                    ),
                ],
            ),
        ]
    )
    return card


def masts_reasons_card(df_in_clean):
    card = dbc.Card(
        [dbc.CardBody(
            [
                html.H2(
                    "Why use met towers?",
                    className="card-title",
                ),
                html.Img(
                    src="data:image/png;base64," + fig_word_cloud(
                        df_in_clean["mettower_reasons"]),
                    style={"max-width": "100%"},
                )
            ]
        ),
        ]
    )
    return card


def lidars_per_MW_card(df_long):
    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H2(
                        "Do bigger wind farms need more lidar?",
                        className="card-title",
                    ),
                    html.Small(
                        [
                            html.I(
                                className="fa-solid fa-circle-info"
                            ),
                            " ",
                            "This chart shows how many lidar are used compared to the size of the wind farm. For example, 3 lidars used on a 120 MW farm would be plotted as 0.025 lidars per MW.",
                        ]
                    ),
                    dcc.Graph(
                        figure=fig_lidars_per_MW(
                            df_long
                        ),
                        id="lidars_per_MW_land",
                        responsive=True,
                        style={
                            "height": "300px"
                        },
                    ),
                ],
            ),
        ]
    )

    return card


def lidar_needs_card(df_in_clean):
    card = dbc.Card(
        [dbc.CardBody(
            [
                html.H2(
                    "Top 3 needs from wind lidar",
                    className="card-title",
                ),
                html.Img(
                    src="data:image/png;base64," +
                    fig_word_cloud(
                        df_in_clean["top_needs"]),
                    style={"max-width": "100%"})
            ]
        )
        ],)
    return card


def lidar_challenges_card(df_in_clean):
    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H2(
                        "Top 3 challenges from wind lidar",
                        className="card-title",
                    ),
                    html.Img(
                        src="data:image/png;base64," +
                        fig_word_cloud(
                            df_in_clean["top_challenges"]),
                        style={"max-width": "100%"}
                    )
                ]
            ),
        ]
    )
    return card


def lidar_opportunities_card(df_in_clean):
    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H2(
                        "Top 3 opportunities from wind lidar",
                        className="card-title",
                    ),
                    html.Img(
                        src="data:image/png;base64," +
                        fig_word_cloud(
                            df_in_clean["top_opportunities"]),
                        style={"max-width": "100%"}
                    )
                ]
            ),
        ]
    )
    return card


def feedback_card():
    card = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4("Feedback and comments"),
                    html.P(
                        "This is a work in progress, and we welcome all feedback about the information we are collecting and how we are presenting it."),
                    html.P(["Please send any feedback to ",
                            html.A("andy.clifton@enviconnect.de",
                                   href="mailto:andy.clifton@enviconnect.de"),
                            "."])
                ]
            )
        ],
        className="g-4",
    )

    return card


def closing_card():
    card = dbc.Card(
        [
            dbc.CardBody(
                closing_text()
            )
        ],
        className="g-4 mt-4",
    )
    return card

# -----------------------------
# Create the layout for this page
# -----------------------------

def show_survey_results():

    # choose to show all data, or just "real" data
    use_real_only = True

    # read the google data each time the page is refreshed
    df_in = fetch_form_responses()
    if use_real_only:
        df_in = prepare_form_responses(df_in)
        df_in_clean = df_in[df_in["real_data"]]
    else:
        df_in_clean = prepare_form_responses(df_in)
    df_long = convert_form_responses_to_long(df_in_clean)

    # now generate the layout
    survey_layout = dbc.Container(
        [
            # title row
            dbc.Row(
                dbc.Col(
                    title_text(),
                )
            ),
            # content
            html.Div(
                [
                    # logging row
                    dbc.Row(
                        dbc.Col([html.Div(id="log")])
                    ),
                    # opening text
                    dbc.Row(
                        [
                            dbc.Col(
                                opening_text(),
                                className="col-12"
                            )
                        ]
                    ),
                    # survey results
                    dbc.Row(
                        [
                            # Number of responses
                            dbc.Col(
                                [
                                    response_count_card(df_in_clean),
                                    alert_card(use_real_only)
                                ],
                                class_name="col-12 col-lg-6 g-4",
                            ),
                            # Map of responses
                            dbc.Col(
                                response_map_card(df_in_clean),
                                class_name="col-12 col-lg-6 g-4",
                            ),
                            # Respondent types
                            dbc.Col(
                                respondent_type_card(df_in_clean),
                                class_name="col-12 col-lg-12 g-4",
                            ),
                            # time series of power
                            dbc.Col(
                                timeline_card(df_in_clean),
                                class_name="col-12 g-4",
                            ),
                            # Lidars per campaign
                            dbc.Col(
                                lidars_per_campaign_card(df_in_clean),
                                class_name="col-12 col-lg-6 g-4",
                            ),
                            # rental versus purchase
                            dbc.Col(
                                lidar_rental_card(df_in_clean),
                                class_name="col-12 col-lg-6 g-4",
                            ),
                            # Lidars per MW
                            dbc.Col(
                                lidars_per_MW_card(df_long),
                                class_name="col-12 g-4",
                            ),
                            # Met towers
                            dbc.Col(
                                masts_per_campaign_card(df_in_clean),
                                class_name="col-12 col-lg-6 g-4",
                            ),
                            # reason for using met towers
                            dbc.Col(
                                masts_reasons_card(df_in_clean),
                                className="col-12 col-lg-6 g-4",
                            ),
                            # Top 3 needs from lidar
                            dbc.Col(
                                lidar_needs_card(df_in_clean),
                                className="col-12 col-lg-6 g-4",
                            ),
                            # Top 3 challenges from lidar
                            dbc.Col(
                                lidar_challenges_card(df_in_clean),
                                className="col-12 col-lg-6 g-4",
                            ),
                            # Top 3 opportunities from lidar
                            dbc.Col(
                                lidar_opportunities_card(df_in_clean),
                                className="col-12 col-lg-6 g-4",
                            ),
                            # Feedback
                            dbc.Col(
                                [
                                    feedback_card(),
                                    closing_card(),
                                ],
                                className="col-12 col-lg-6 g-4",
                            ),
                        ],
                    )
                ],
                className="content g-4",
                style={"min-height": "80vh"},
            ),
        ],
        fluid=False,
        className="dbc h-80",
        style={"min-height": "80vh"},
    )

    return survey_layout

def layout():    

    layout = html.Div(
        children=[
            html.Div(
                id="div-loading",
                children=[
                    dash_loading_spinners.Pacman(
                        color="white",
                        fullscreen=True,
                        fullscreen_style={'background-color':"#117f82"},
                        id="loading-whole-app"
                    )
                ]
            ),
            html.Div(
                className="div-app",
                id="div-app",
                children=[  
                    # app layout here
                    show_survey_results()
                ]
            )
        ]
    )

    return layout


# -----------------------------
# Callbacks
# -----------------------------
@dash.callback(
        Output("div-loading", "children"),
        [
            Input("div-app", "loading_state")
        ],
        [
            State("div-loading", "children"),
        ]
    )
def hide_loading_after_startup(
        loading_state, 
        children
        ):
        if children:
            print("remove loading spinner!")
            return None
        print("spinner already gone!")
        
# See https://community.plotly.com/t/show-a-full-screen-loading-spinner-on-app-start-up-then-remove-it/60174/3