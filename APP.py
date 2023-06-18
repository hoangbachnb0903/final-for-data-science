import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go



# Read the SpaceX launch data from a CSV file
spacex_df = pd.read_csv("spacex_launch_geo.csv")

# Create the Dash app
app = dash.Dash(__name__)
server = app.server

# Define unique launch sites for dropdown menu
launch_sites = spacex_df['Launch Site'].unique()
launch_site_options = [{'label': 'All Sites', 'value': 'All Sites'}] + [{'label': site, 'value': site} for site in launch_sites]

# Calculate payload range
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Define app layout
app.layout = html.Div(
    children=[
        html.H1('SpaceX Launch Records Dashboard', style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
        dcc.Dropdown(
            id='site-dropdown',
            options=launch_site_options,
            placeholder='Select a Launch Site',
            searchable=True,
            value='All Sites'
        ),
        html.Br(),
        dcc.Graph(id='success-pie-chart'),
        html.Br(),
        html.P("Payload range (Kg):"),
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            marks={i: f'{i} kg' for i in range(0, 10001, 1000)},
            value=[min_payload, max_payload]
        ),
        html.Div(dcc.Graph(id='success-payload-scatter-chart'))
    ]
)


@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def update_pie_chart(site_dropdown):
    if site_dropdown == 'All Sites':
        df = spacex_df[spacex_df['class'] == 1]
        title = 'Total Success Launches By all sites'
    else:
        df = spacex_df[spacex_df['Launch Site'] == site_dropdown]
        title = f'Total Success Launches for site {site_dropdown}'

    fig = go.Figure(data=go.Pie(labels=df['Launch Site'], hole=0.3))
    fig.update_layout(title=title)
    return fig


@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(site_dropdown, payload_range):
    low, high = payload_range
    if site_dropdown == 'All Sites':
        df = spacex_df[(spacex_df['Payload Mass (kg)'] > low) & (spacex_df['Payload Mass (kg)'] < high)]
        title = 'Payload Mass vs. Success for All Sites'
    else:
        df = spacex_df[(spacex_df['Launch Site'] == site_dropdown) & (spacex_df['Payload Mass (kg)'] > low) & (spacex_df['Payload Mass (kg)'] < high)]
        title = f'Payload Mass vs. Success for {site_dropdown}'

    fig = go.Figure(data=go.Scatter(
        x=df['Payload Mass (kg)'],
        y=df['class'],
        mode='markers',
        marker=dict(
            size=df['Payload Mass (kg)'],
            color=df['Booster Version'],
            showscale=True
        ),
        hovertext=df['Payload Mass (kg)']
    ))
    fig.update_layout(
        title=title,
        xaxis_title='Payload Mass (kg)',
        yaxis_title='Success',
        showlegend=False
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=False)

#%%
