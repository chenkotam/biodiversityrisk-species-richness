'''
File: app.py
Project: Biodiversity - Visualize Species Count by Country/County

File Created: Tuesday, 15th April 2023 10:06:00 am

Author: Zhenhao Tan (zhenhao.tan@yale.edu)
-----
Last Modified: Tuesday, 18th April 2023 9:30:00 am
-----
Description: This file visualize the species count using plotly dash app. This
is deployed using render through the github commit. This file is generally the
same as 3_species_cnt_visualize.py
'''

import os
import pandas as pd
import numpy as np
import plotly.express as px
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc


PROJECT_PATH = '../'
df_county_all = pd.read_csv(os.path.join(PROJECT_PATH, "data/species_county_all.csv"))
df_county_marine = pd.read_csv(os.path.join(PROJECT_PATH, "data/species_county_marine.csv"))
df_county_terrestial = pd.read_csv(os.path.join(PROJECT_PATH, "data/species_county_terrestial.csv"))
df_county_freshwater = pd.read_csv(os.path.join(PROJECT_PATH, "data/species_county_freshwater.csv"))
df_county_all['US_County_FIPS'] = df_county_all['US_County_FIPS'].apply(lambda x: f"{x:05d}")
df_county_marine['US_County_FIPS'] = df_county_marine['US_County_FIPS'].apply(lambda x: f"{x:05d}")
df_county_terrestial['US_County_FIPS'] = df_county_terrestial['US_County_FIPS'].apply(lambda x: f"{x:05d}")
df_county_freshwater['US_County_FIPS'] = df_county_freshwater['US_County_FIPS'].apply(lambda x: f"{x:05d}")

# =================================================================================================
#  VISUALIZATION
# =================================================================================================

# Function to update the figure based on the selected _class and column to visualize
def update_figure(selected_classes, selected_column, selected_dataset, color_scale_min, color_scale_max):
    
    # For selected_dataset
    if selected_dataset == 'marine':
        df_county = df_county_marine
    if selected_dataset == 'terrestial':
        df_county = df_county_terrestial
    if selected_dataset == 'freshwater':
        df_county = df_county_freshwater
    if selected_dataset == 'all':
        df_county = df_county_all
    
    # For selected_classes
    if 'All' in selected_classes:
        selected_classes = df_county['_class'].unique().tolist()

    filtered_df = df_county[df_county['_class'].isin(selected_classes)]

    if selected_column == 'ratio':
        filtered_df['ratio'] = filtered_df['n_red'] / filtered_df['n_species']
        aggregated_df = filtered_df.groupby('US_County_FIPS')['ratio'].mean().reset_index()
    else:
        aggregated_df = filtered_df.groupby('US_County_FIPS')[selected_column].sum().reset_index()


    fig = px.choropleth(aggregated_df,
                        geojson='https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json',
                        locations='US_County_FIPS',
                        color=selected_column,
                        color_continuous_scale=["white", "gold", "red"], # "Viridis"
                        range_color=[color_scale_min, color_scale_max],
                        scope="usa",
                        labels={selected_column: selected_column.capitalize()},
                        hover_name='US_County_FIPS')
                        # hover_data=['_class'])
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig

# Define the initial _class and column to visualize
initial_class = 'All'
initial_column = 'n_species'
initial_dataset = 'all'

# Create the initial figure
fig = update_figure([initial_class], initial_column, initial_dataset, 0, 1)

# Initialize the Dash app
external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


# Define the app layout
app.layout = dbc.Container([
    html.H1("Species Richness"),
    dbc.Row([
        dbc.Col([
            html.Label("Classes:"),
            dcc.Checklist(
                id='class_checklist',
                options=[{'label': 'All', 'value': 'All'}] + [{'label': c, 'value': c} for c in df_county_all['_class'].unique()],
                value=[initial_class],
            ),
            html.Label("Color Scale Min:"),
            dcc.Input(id='color_scale_min', type='number', value=0),
            html.Label("Color Scale Max:"),
            dcc.Input(id='color_scale_max', type='number', value=1),
        ], width=4),
        dbc.Col([
            dbc.Row([
                dbc.Col(dbc.RadioItems(
                    id='column_radio',
                    options=[
                        {'label': 'No. Species', 'value': 'n_species'},
                        {'label': 'No. Threatened Species', 'value': 'n_red'},
                        {'label': 'Ratio', 'value': 'ratio'},
                    ],
                    value=initial_column,
                    inline=True
                )),
            ]),
            dbc.Row([
                dbc.Col(dcc.RadioItems(
                    id='dataset_radio',
                    options=[
                        {'label': 'All', 'value': 'all'},
                        {'label': 'Marine', 'value': 'marine'},
                        {'label': 'Terrestial', 'value': 'terrestial'},
                        {'label': 'Freshwater', 'value': 'freshwater'},
                    ],
                    value=initial_dataset,
                    inline=True,
                    labelStyle={'display': 'inline-block', 'margin-left': '20px'}
                )),
            ]),
            dcc.Graph(id='choropleth', figure=fig, style={'width': '70vw', 'height': '60vh'})
        ], width=6),
    ]),
], style={'marginLeft': '50px', 'marginTop': '20px'})


# Define the app callback
@app.callback(
    Output('choropleth', 'figure'),
    [Input('class_checklist', 'value'),
     Input('column_radio', 'value'),
     Input('dataset_radio', 'value'),
     Input('color_scale_min', 'value'),
     Input('color_scale_max', 'value')])
def update_choropleth(selected_classes, selected_column, selected_dataset, color_scale_min, color_scale_max):
    return update_figure(selected_classes, selected_column, selected_dataset, color_scale_min, color_scale_max)


@app.callback(
    [Output('color_scale_min', 'value'),
     Output('color_scale_max', 'value')],
    [Input('class_checklist', 'value'),
     Input('column_radio', 'value'),
     Input('dataset_radio', 'value')])
def update_color_scale_inputs(selected_classes, selected_column, selected_dataset):
    
    # For selected_dataset
    if selected_dataset == 'marine':
        df_county = df_county_marine
    if selected_dataset == 'terrestial':
        df_county = df_county_terrestial
    if selected_dataset == 'freshwater':
        df_county = df_county_freshwater
    if selected_dataset == 'all':
        df_county = df_county_all
    
    
    # For selected_classes
    if 'All' in selected_classes:
        selected_classes = df_county['_class'].unique().tolist()

    filtered_df = df_county[df_county['_class'].isin(selected_classes)]

    if selected_column == 'ratio':
        filtered_df['ratio'] = filtered_df['n_red'] / filtered_df['n_species']
        aggregated_df = filtered_df.groupby('US_County_FIPS')['ratio'].mean().reset_index()
    else:
        aggregated_df = filtered_df.groupby('US_County_FIPS')[selected_column].sum().reset_index()

    return aggregated_df[selected_column].min(), aggregated_df[selected_column].max()

    
# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
    
    
    
    
    
    
