import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import openmeteo_requests
import requests_cache
from retry_requests import retry
import PySAM.Pvwattsv8 as pvwattsq
import os

from sqlalchemy import create_engine, text


def get_plant_file_paths(base_dir):
    plant_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    plant_file_paths = {}

    for plant in plant_dirs:
        plant_path = os.path.join(base_dir, plant)
        excel_files = [os.path.join(plant_path, f) for f in os.listdir(plant_path) if f.endswith('.xlsx')]
        csv_file = [os.path.join(plant_path, f) for f in os.listdir(plant_path) if f.endswith('.csv')]
        plant_file_paths[plant] = {
            'excel_files': excel_files,
            'csv_file': csv_file[0] if csv_file else None
        }

    return plant_file_paths

# Database connection setup
def create_pg_engine():
    engine = create_engine('postgresql+psycopg2://marzol:12053@localhost:5432/postgres')
    return engine

# Function to query data for each plant
def query_plant_data(engine, plant, start_date, end_date):
    with engine.connect() as connection:
        # Query for inverter data
        query_inv_hourly = text(f"""
            SELECT *
            FROM {plant}_inv
            WHERE timestamp BETWEEN :start_date AND :end_date;
        """)
        df_inv = pd.read_sql(query_inv_hourly, connection, params={'start_date': start_date, 'end_date': end_date}, index_col='timestamp')
        df_inv.index = pd.to_datetime(df_inv.index)

        query_inv_daily = text(f"""
            SELECT 
                DATE(timestamp) AS date,
                SUM(CAST("Energy from grid" AS NUMERIC)) AS total_energy_from_grid,
                SUM(CAST("Energy to grid" AS NUMERIC)) AS total_energy_to_grid,
                SUM(CAST("PV production" AS NUMERIC)) AS total_pv_production,
                SUM(CAST("Consumed directly" AS NUMERIC)) AS total_consumed_directly
            FROM {plant}_inv
            WHERE timestamp BETWEEN :start_date AND :end_date
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp);
        """)
        df_inv_daily = pd.read_sql(query_inv_daily, connection, params={'start_date': start_date, 'end_date': end_date})
        df_inv_daily.set_index('date', inplace=True)

        # Query for helioscope data
        query_hs = text(f"""
            SELECT *
            FROM {plant}_hs
            WHERE timestamp BETWEEN :start_date AND :end_date;
        """)
        df_hs = pd.read_sql(query_hs, connection, params={'start_date': start_date, 'end_date': end_date}, index_col='timestamp')
        df_hs.index = pd.to_datetime(df_hs.index)

        # Query for daily helioscope data
        query_hs_daily = text(f"""
            SELECT *
            FROM {plant}_hs_daily
            WHERE index BETWEEN :start_date AND :end_date;
        """)
        df_hs_daily = pd.read_sql(query_hs_daily, connection, params={'start_date': start_date, 'end_date': end_date}, index_col='index')
        df_hs_daily.index = pd.to_datetime(df_hs_daily.index)

    return df_inv, df_inv_daily, df_hs, df_hs_daily


# Example usage get plants
plant_data_paths = get_plant_file_paths('p3_plants')
# Function to fetch and process weather data
# Setup the Open-Meteo API client with cache and retry on error
# cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
# retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
# openmeteo = openmeteo_requests.Client(session=retry_session)

# def fetch_weather_data(start_date, end_date):
#     url = "https://archive-api.open-meteo.com/v1/archive"
#     params = {
#         "latitude": -33.6421493,  # Latitude for Worcester, South Africa
#         "longitude": 19.4488646,  # Longitude for Worcester, South Africa
#         "start_date": start_date,
#         "end_date": end_date,
#         "hourly": ["temperature_2m", "wind_speed_10m", "shortwave_radiation", "diffuse_radiation", "direct_normal_irradiance"]
#     }
#     responses = openmeteo.weather_api(url, params=params)
#     response = responses[0]
#     hourly = response.Hourly()
#     hourly_data = {
#         "date": pd.date_range(
#             start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
#             end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
#             freq=pd.Timedelta(seconds=hourly.Interval()),
#             inclusive="left"
#         ),
#         "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
#         "wind_speed_10m": hourly.Variables(1).ValuesAsNumpy(),
#         "shortwave_radiation": hourly.Variables(2).ValuesAsNumpy(),
#         "diffuse_radiation": hourly.Variables(3).ValuesAsNumpy(),
#         "direct_normal_irradiance": hourly.Variables(4).ValuesAsNumpy()
#     }
#     hourly_dataframe = pd.DataFrame(data=hourly_data)
#     hourly_dataframe = hourly_dataframe.replace([np.inf, -np.inf], np.nan).dropna()
#     hourly_dataframe['minute'] = 0
#     return hourly_dataframe

# # Function to configure and run the PVWatts model
# def run_pvwatts_simulation(hourly_dataframe):
#     solar_resource_data = {
#         'lat': -33.64,  # Latitude for Worcester, South Africa
#         'lon': 19.44,   # Longitude for Worcester, South Africa
#         'tz': 2,        # Timezone offset (UTC+2 for South Africa)
#         'elev': 230,    # Elevation in meters (approximate for Worcester)
#         'year': hourly_dataframe['date'].dt.year.tolist(),
#         'month': hourly_dataframe['date'].dt.month.tolist(),
#         'day': hourly_dataframe['date'].dt.day.tolist(),
#         'hour': hourly_dataframe['date'].dt.hour.tolist(),
#         'minute': hourly_dataframe['minute'].tolist(),
#         'dn': hourly_dataframe['direct_normal_irradiance'].tolist(),  # DNI
#         'df': hourly_dataframe['diffuse_radiation'].tolist(),         # DHI
#         'gh': hourly_dataframe['shortwave_radiation'].tolist(),       # GHI
#         'tdry': hourly_dataframe['temperature_2m'].tolist(),          # Temperature
#         'wspd': hourly_dataframe['wind_speed_10m'].tolist()           # Wind Speed
#     }
#
#     pv_system = pvwatts.default('PVWattsSingleOwner')
#     print(solar_resource_data)
#     pv_system.SolarResource.solar_resource_data = solar_resource_data
#     pv_system.SystemDesign.system_capacity = 27  # 27 kW system
#     pv_system.SystemDesign.module_type = 0       # Standard module
#     pv_system.SystemDesign.array_type = 0        # Fixed - Open Rack
#     pv_system.SystemDesign.tilt = 11             # 11-degree tilt
#     pv_system.SystemDesign.azimuth = 329.07      # 329.07 degrees azimuth
#     pv_system.SystemDesign.losses = 14           # System losses as percentage
#
#     pv_system.execute()
#     hourly_ac_output = pv_system.Outputs.ac
#
#     pv_production_df = pd.DataFrame({
#         "date": hourly_dataframe["date"],
#         "ac_power_kw": hourly_ac_output
#     })
#
#     # # Convert the 'date' column to datetime and remove timezone if needed
#     pv_production_df['date'] = pd.to_datetime(pv_production_df['date'])
#
#     # Set the 'date' column as the index
#     pv_production_df.set_index('date', inplace=True)
#
#     # Optionally, format the index to the desired string format
#     pv_production_df.index = pv_production_df.index.strftime('%Y-%m-%d %H:%M:%S.%f')
#
#     pv_production_df['ac_power_kw']*1000
#     print("************************")
#     print(pv_production_df)
#     return pv_production_df


# Create Dash app
app = dash.Dash(__name__)
server = app.server

# Define app layout
app.layout = html.Div([
    html.Div([
        html.H1("P3 PV Dashboard", style={'text-align': 'center'}),
        html.Img(src='/assets/P3.png', style={'height': '50px', 'width': 'auto'})
    ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),

    html.Div([
        html.P("Select the date range to visualize data:", style={'text-align': 'center'}),
        dcc.DatePickerRange(
            id='date-picker-range',
            display_format='YYYY-MM-DD',
            style={'margin': '0 auto', 'width': '60%', 'display': 'block'}
        )
    ], style={'text-align': 'center'}),

    dcc.Dropdown(
        id='plant-selection-dropdown',
        options=[{'label': plant, 'value': plant} for plant in plant_data_paths.keys()],
        value='Plant1',  # Default value
        clearable=False
    ),
    dcc.Dropdown(
        id='graph-selection-dropdown',
        options=[
            {'label': 'Show Energy Graph', 'value': 'energy'},
            {'label': 'Show Breakdown Graph', 'value': 'breakdown'}
        ],
        value='breakdown',  # Default value
        clearable=False
    ),
    html.Div(id='plant-graphs-container'),

    html.Div([
        html.Footer("Developed by VOCMax", style={'text-align': 'center', 'font-size': '12px'})
    ])
], style={'background-color': '#ffffff', 'padding': '20px'})

# Create the database engine
engine = create_pg_engine()

@app.callback(
    Output('plant-graphs-container', 'children'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('plant-selection-dropdown', 'value'),
     Input('graph-selection-dropdown', 'value')]
)
def update_graphs(start_date, end_date, selected_plant, selected_graph):
    graphs = []
    # Fetch weather data and run PVWatts simulation
    # weather_data = fetch_weather_data(start_date, end_date)
    # pv_production_df = run_pvwatts_simulation(weather_data)
    # # Resample the DataFrame to get daily sums
    # daily_pv_production = pv_production_df.resample('D', on='date').sum().reset_index()

    # Query data from PostgreSQL for each plant
    df_inv, df_inv_daily, df_hs, df_hs_daily = query_plant_data(engine, selected_plant, start_date, end_date)

    # Debug the filtered data
    print(f"Start: {start_date}   End: {end_date}")
    # print(f"{plant} - Filtered Inv Data: {df_inv.head()}")
    print(f"{selected_plant} - Filtered Inv Data: {df_inv_daily.head()}")
    # print(f"{plant} - Filtered Helioscope Data: {df_hs.head()}")
    print(f"{selected_plant} - Filtered Inv Data: {df_hs_daily.head()}")

    # Create the energy production graph
    energy_graph = dcc.Graph(
        id=f'energy-graph-{selected_plant}',
        figure={
            'data': [
                go.Scatter(x=df_inv.index, y=df_inv['PV production'],mode='lines+markers',name='PV production', marker=dict(color='green')),
                go.Scatter(x=df_hs.index, y=df_hs['actual_dc_power'],mode='lines+markers', name='Helioscope', marker=dict(color='red')),
                go.Scatter(x=df_inv.index, y=df_inv['Consumption'],mode='lines+markers',name='Solar + Grid', marker=dict(color='purple')),
                go.Scatter(x=df_inv.index, y=df_inv['Consumed directly'],mode='lines+markers',name='Solar Consumed',marker=dict(color='#FDDA0D')),
                go.Scatter(x=df_inv.index, y=df_inv['Energy from grid'],mode='lines+markers',name='Grid', marker=dict(color='#F88379')),
                go.Scatter(x=df_inv.index, y=df_inv['Energy to grid'],mode='lines+markers',name='Export', marker=dict(color='#AFE1AF')),
                # go.Scatter(x=pv_production_df.index, y=pv_production_df['ac_power_kw'], mode='lines+markers', name='PySAM',
                #            marker=dict(color='#AFE1AZ'))
            ],
            'layout': go.Layout(title=f'{selected_plant} Detailed PV Production', xaxis={'range': [start_date, end_date]})
        }
    )
    daytime_data = df_inv.between_time('08:00:00','16:00:00')
    nighttime_data = df_inv[~df_inv.index.isin(daytime_data.index)]

    # Step 2: Convert 'Energy from grid' to numeric, forcing errors to NaN
    daytime_data['Energy from grid'] = pd.to_numeric(daytime_data['Energy from grid'], errors='coerce')
    nighttime_data['Energy from grid'] = pd.to_numeric(nighttime_data['Energy from grid'], errors='coerce')

    # Step 3: Optionally fill NaN values (if needed)
    # For example, fill NaNs with 0
    daytime_data['Energy from grid'].fillna(0, inplace=True)
    nighttime_data['Energy from grid'].fillna(0, inplace=True)

    # Now perform the resampling and grouping
    daytime_data = daytime_data.resample('h').sum()
    nighttime_data = nighttime_data.resample('h').sum()

    # Group by date and sum the 'Energy from grid'
    grid_day = daytime_data.groupby(daytime_data.index.date)['Energy from grid'].sum()
    grid_night = nighttime_data.groupby(nighttime_data.index.date)['Energy from grid'].sum()

    # Create the consumption breakdown graph
    breakdown_graph = dcc.Graph(
        id=f'consumption-breakdown-graph-{selected_plant}',
        figure={
            'data': [
                go.Bar(x=df_inv_daily.index, y=df_inv_daily['total_consumed_directly'], name='Solar Consumed', marker=dict(color='#FDDA0D')),
                go.Bar(x=df_inv_daily.index, y=df_inv_daily['total_energy_to_grid'], name='Export',
                       marker=dict(color='#AFE1AF'), visible='legendonly'),
                go.Bar(x=grid_day.index, y=grid_day.values, name='Grid Consumed Day',marker=dict(color='#F88379')),
                go.Bar(x=grid_night.index, y=grid_night.values, name='Grid Consumed Night',marker=dict(color='#6495ED')),
                go.Scatter(x=df_hs_daily.index, y=df_hs_daily['moving_avg'], mode='lines', name='Helioscope Simulation',line=dict(color='red', width=3)),
                # go.Scatter(x=daily_pv_production.index, y=daily_pv_production['ac_power_kw'], mode='lines', name='PySAM',line=dict(color='blue', width=3))

            ],
            'layout': go.Layout(title=f'{selected_plant} PV Performance', barmode='stack', xaxis={'range': [start_date, end_date]})
        }
    )

    # Determine which graph to display based on dropdown selection
    if selected_graph == 'energy':
        graphs.append(html.Div([
            html.H3(f'{selected_plant} Plant'),
            energy_graph
        ]))
    else:
        graphs.append(html.Div([
            html.H3(f'{selected_plant} Plant'),
            breakdown_graph
        ]))


    return graphs

if __name__ == '__main__':
    app.run_server(debug=True)