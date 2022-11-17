#!/usr/bin/env python
# coding: utf-8

# In[1]:


import plotly.express as px
from jupyter_dash import JupyterDash
import dash
from dash import html, Input, Output
from dash import dcc
from dash import dash_table
import dash_defer_js_import as dji
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

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


# # Get Data

# In[2]:


# Grab some data
# Open the file and load the file
with open('data/facilities.yaml') as f:
    data = yaml.load(f, 
                     Loader=SafeLoader)

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


# # Checks

# In[3]:


# cell to check stuff

print(df)


# In[4]:


# Get the token for MapBox

px.set_mapbox_access_token(open(".mapbox_token").read())


# # Create data filters based on values in the data

# ## Get the list of countries in the data

# In[5]:


# Define some basic functions to get information from the data

def get_countries(df_in):
    return sorted(df_in.country.dropna().unique())            

def get_countries_label_value_pairs(df_in):
    label_value_pairs = []
    for i in get_countries(df_in):
        label_value_pairs.append({'label':i,
                               'value':i})
    
    return label_value_pairs


# ## Get the facility types

# In[6]:


def get_facility_types(df_in):
    return sorted(df_in.type_property.dropna().unique())            
 
def get_facility_types_label_value_pairs(df_in):
    label_value_pairs = []
    for i in get_facility_types(df_in):
        label_value_pairs.append({'label':i,
                               'value':i})
    
    return label_value_pairs


# ## Get the infrastructure on the site

# In[7]:


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


# ## Get the data available on the site

# In[8]:


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


# ## Define the filters

# In[9]:


# The App will filter using these characteristics:
# 1. Country
# 2. facility type
# 3. Infrastructure
# 4. Data
# each filter will be presented as a checklist

filterIcon = [
    html.I(className="fa-solid fa-filter me-2"),
                "Filter facilities",
]

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


# ## Filter the facilities using values from the dropdowns

# In[10]:


# testing



# In[11]:


# Build App
# for some ideas, see e.g.
# 1. https://towardsdatascience.com/3-easy-ways-to-make-your-dash-application-look-better-3e4cfefaf772
# and
# 2. https://github.com/charlotteamy/Dash-visualisation/blob/main/Dash_blog.py

# Define the app using an external stylesheet
# Use https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/ to find stylesheets

app = JupyterDash(__name__,
                  external_stylesheets=[
                      dbc.themes.SPACELAB,
                      dbc.icons.FONT_AWESOME
                  ]
                  )


# In[12]:


# Build App
# for some ideas, see e.g.
# 1. https://towardsdatascience.com/3-easy-ways-to-make-your-dash-application-look-better-3e4cfefaf772
# and
# 2. https://github.com/charlotteamy/Dash-visualisation/blob/main/Dash_blog.py

# Define the app using an external stylesheet
# Use https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/ to find stylesheets

app = JupyterDash(__name__,
                  external_stylesheets=[
                      dbc.themes.SPACELAB,
                      dbc.icons.FONT_AWESOME
                  ]
                  )


# In[13]:


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


# # Utility functions

# ## Turn a text url into an HTML link object

# In[14]:


def create_www_link(url):

    if any(pd.isna(url)):
        return []
    else:
        return html.A(
            [
                html.I(className="fa-solid fa-globe"),
                ' link'
            ],
            className = "btn btn-outline-secondary mr-2",
            href=''.join(url), target="_blank")


# ## Utility function to turn a url into a www link button

# In[15]:


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
            className="me-1"
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
            className="me-1"
        )


# ## Turn a url into a google maps link button

# In[16]:


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
            color="primary",            
            active=True,
            className="me-1"
            )


# # Define the App

# In[17]:


# Build App

# Define the app using an external stylesheet
# Use https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/ to find stylesheets

# https://hellodash.pythonanywhere.com/adding-themes/dcc-components
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.css"

app = JupyterDash(__name__,
                  external_stylesheets=[
                      dbc.themes.BOOTSTRAP, 
                      dbc_css,
                      dbc.icons.FONT_AWESOME
                  ]
                  )



# ## Create the map

# In[18]:


# create the map
def facility_map_fig(dff):

    # establish the bounds of the map
    if len(dff) >= 2:
        dlat = 1+dff["lat"].max()-dff["lat"].min()-1
        dlon = 1+dff["lon"].max()-dff["lon"].min()-1
        max_bound = max(abs(dlat), abs(dlon)) * 111
        map_zoom = math.floor(11.5 - np.log(max_bound))
    elif len(dff) == 0:
        map_zoom = 1
    else:
        map_zoom = 5

    fig = px.scatter_mapbox(
        dff,
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
    fig.update_traces(cluster=dict(enabled=True, size=2, step=3))

    return fig


# # Update the map

# In[19]:


# define the callback to update the map
@app.callback(
    Output('facility_map', 'figure'),
    Input('country_selector', 'value'),
    Input('facilitytype_selector', 'value'),
    Input('infrastructure_selector', 'value'),
    Input('availabledata_selector', 'value')
)
def update_map(countries_selected="", facilitytypes_selected="", infrastructure_selected="", availabledata_selected=""):

    dff = filter_facilities(
        df,
        countries_selected,
        facilitytypes_selected,
        infrastructure_selected,
        availabledata_selected
    )

    fig = facility_map_fig(dff)

    return fig


# # Create a sortable table

# In[20]:


def create_sortable_facility_table(df_in):

    df_table = df_in[["name", "country", "type_property"]]
    df_table.rename(columns={"type_property": "type"}, inplace=True)

    sortable_facility_table = dash_table.DataTable(
        id="sortable-facility-table",
        columns=[
            {"name": i, "id": i, "deletable": False, "selectable": False} for i in df_table.columns
        ],
        data=df_table.to_dict('records'),
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            'lineHeight': '15px'
        },
        style_cell_conditional=[
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


# # Generate an Information card for the selected facilty

# ## Get the card title

# In[21]:


def get_card_facility_title_element(dff_selected):

    return html.H4(dff_selected["name"])


# ## Build the description

# In[22]:


def get_card_facility_description_element(dff_selected):

    # return a description of a facility with a source (if given). Otherwise, just return a text block

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


# ## create an html list from a list

# In[23]:


def create_Ul(contents):
    h = []
    for i in contents:
        if isinstance(i, list):
            h.append(create_Ul(i))
        else:
            h.append(html.Li(i))
    return html.Ul(h) 


# ## Create a list of infrastructure at the facility

# In[24]:


def get_card_infrastructure_element(dff_selected):

    if not dff_selected["infrastructure"].isnull().values.any():

        infrastructure_list = create_Ul(dff_selected['infrastructure'].squeeze())

        infrastructure_element = [
            html.P("Available infrastructure:"),
            infrastructure_list
        ]        
        return infrastructure_element
    else:
        return(html.P("no infrastructure information available"))


# ## Create a list of infrastructure at the facility

# In[25]:


def get_card_availabledata_element(dff_selected):

    if not dff_selected["availabledata"].isnull().values.any():

        availabledata_list = create_Ul(dff_selected['availabledata'].squeeze())

        availabledata_element = [
            html.P("Available data:"),
            availabledata_list
        ]        
        return availabledata_element
    else:
        return(html.P("no information about data available"))


# In[26]:


@app.callback(
    [
        Output("card-title", "children"),
        Output("card-desc", "children"),
        Output("card-infrastructure", "children"),
        Output("card-availabledata", "children")
    ],
    Input('facility_map', 'clickData')
)
def update_information_card(clickData):

    if clickData is None:
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
        selected = clickData["points"][0]
        dff_selected = df[(df['lat'] == selected['lat']) & (
            df['lon'] == selected['lon'])] if selected else None

        card_title_element = get_card_facility_title_element(dff_selected)

        card_description_element = get_card_facility_description_element(
            dff_selected)

        card_infrastructure_element = get_card_infrastructure_element(
            dff_selected)

        card_availabledata_element = get_card_availabledata_element(
            dff_selected)

    return card_title_element, card_description_element, card_infrastructure_element, card_availabledata_element


# # Create the footer

# ## Create the basic layout
# 
# Create a 3-column footer. Columns will include:
# 1. About us
# 2. Links to useful informmation
# 3. Address, etc.

# In[27]:


def create_footer():

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
                width=3),
            dbc.Col(

            ),
            dbc.Col(

            ),
            dbc.Col(
                [
                    html.H2("Contact"),
                    html.P(["TGU enviConnect", html.Br(),
                           "TTI GmbH", html.Br(),
                           "Nobelstrasse 15", html.Br(),
                           "70569 Stuttgart", html.Br(),
                           "Germany"])
                ]
            )
        ],
        className="h-10 pt-2 footer"
    )

    return footer


# # Create a sub footer

# ## Create the basic layout
# 
# Creates a single row footer with links including:
# 1. Publisher
# 2. Privacy
# 3. Copyright and design notes

# In[28]:


def create_subfooter():

    subfooter = dbc.Row(
        [
            html.P("Subfooter")
        ],
        className="subfooter h-10"
    )

    return subfooter    


# # Create the overall App layout

# In[29]:


# Create an app with two columns:
# 3 cols on the left for filters, 9 on the right for map & information
app.layout = dbc.Container(
    [
        # nav bar
        # content
        html.Div(
            [
        # title row
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        html.H2("Wind Energy R&D Facilities Explorer")
                    ),
                    width=12),
            ],
            className="h-10 w-100 navbar navbar-expand-lg",
        ),
        # map and table content row
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            figure=facility_map_fig(df),
                            id="facility_map"
                        )
                    ],
                    className="col-12 col-lg-6",
                    style={
                        "height": "100%",
                    },
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
            className="pb-2"
        ),
        # filter row
        dbc.Row(
            [
                dbc.Col(
                    filterIcon,
                    width=1
                ),
                dbc.Col(
                    [
                        dbc.Row(
                            filters
                        )
                    ]
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
            className="content"
        ),
        # footer row
        create_footer(),
        # subfooter
        create_subfooter(),
        # dcc.Store stores the intermediate value
        dcc.Store(id='intermediate-value')
    ],
    fluid=False,
    className="dbc h-100",
    style={
        "background-color":"var(--color-4)",
        "min-height": "100vh"
    }
)


# # Filter data depending on the values of the filter buttons

# In[30]:


@app.callback(
    #Output('intermediate-value','data'),
    Output('sortable-facility-table','data'),
    Input('country_selector','value'),
    Input('facilitytype_selector','value'),
    Input('infrastructure_selector','value'),
    Input('availabledata_selector','value'),
)
def get_filtered_facilities(countries_selected="", facilitytypes_selected="", infrastructure_selected="", availabledata_selected=""):

    # get the table of facilities that match the filter values
    dff = filter_facilities(
        df,
        countries_selected,
        facilitytypes_selected,
        infrastructure_selected,
        availabledata_selected
        )
        
    df_table = dff[["name","country","type_property"]]
    df_table.rename(columns={"type_property":"type"}, inplace=True)

    #return dff.to_json(date_format='iso', orient='split'), df_table
    return df_table.to_dict('records')



# # Run App

# 

# In[31]:


# Run app as a separate tab
app.run_server(mode='external',debug=True,)

