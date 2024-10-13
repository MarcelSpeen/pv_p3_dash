import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from sqlalchemy import create_engine, text
import pandas as pd
import os


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
    engine = create_engine('postgresql+psycopg2://postgres_p3_user:sApFc0gEg8G4cYfrCNbufctKuzJ0I9js@dpg-cs5v6ig8fa8c73ar9rf0-a.oregon-postgres.render.com:5432/postgres_p3')
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

    # Dynamically create graph containers for each plant
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
     Input('date-picker-range', 'end_date')]
)
def update_graphs(start_date, end_date):
    graphs = []

    for plant in plant_data_paths.keys():
        # Query data from PostgreSQL for each plant
        df_inv, df_inv_daily, df_hs, df_hs_daily = query_plant_data(engine, plant, start_date, end_date)

        # Debug the filtered data
        print(f"Start: {start_date}   End: {end_date}")
        # print(f"{plant} - Filtered Inv Data: {df_inv.head()}")
        print(f"{plant} - Filtered Inv Data: {df_inv_daily.head()}")
        # print(f"{plant} - Filtered Helioscope Data: {df_hs.head()}")
        print(f"{plant} - Filtered Inv Data: {df_hs_daily.head()}")

        # Create the energy production graph
        energy_graph = dcc.Graph(
            id=f'energy-graph-{plant}',
            figure={
                'data': [
                    go.Scatter(x=df_inv.index, y=df_inv['PV production'],mode='lines+markers',name='PV production', marker=dict(color='green')),
                    go.Scatter(x=df_hs.index, y=df_hs['actual_dc_power'],mode='lines+markers', name='Helioscope', marker=dict(color='red')),
                    go.Scatter(x=df_inv.index, y=df_inv['Consumption'],mode='lines+markers',name='Solar + Grid', marker=dict(color='purple')),
                    go.Scatter(x=df_inv.index, y=df_inv['Consumed directly'],mode='lines+markers',name='Solar Consumed',marker=dict(color='#FDDA0D')),
                    go.Scatter(x=df_inv.index, y=df_inv['Energy from grid'],mode='lines+markers',name='Grid', marker=dict(color='#F88379')),
                    go.Scatter(x=df_inv.index, y=df_inv['Energy to grid'],mode='lines+markers',name='Export', marker=dict(color='#AFE1AF')),
                ],
                'layout': go.Layout(title=f'{plant} Detailed PV Production', xaxis={'range': [start_date, end_date]})
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
            id=f'consumption-breakdown-graph-{plant}',
            figure={
                'data': [
                    go.Bar(x=df_inv_daily.index, y=df_inv_daily['total_consumed_directly'], name='Solar Consumed', marker=dict(color='#FDDA0D')),
                    go.Bar(x=df_inv_daily.index, y=df_inv_daily['total_energy_to_grid'], name='Export',
                           marker=dict(color='#AFE1AF'), visible='legendonly'),
                    go.Bar(x=grid_day.index, y=grid_day.values, name='Grid Consumed Day',marker=dict(color='#F88379')),
                    go.Bar(x=grid_night.index, y=grid_night.values, name='Grid Consumed Night',marker=dict(color='#6495ED')),
                    go.Scatter(x=df_hs_daily.index, y=df_hs_daily['moving_avg'], mode='lines', name='Helioscope Simulation',line=dict(color='red', width=3))
                ],
                'layout': go.Layout(title=f'{plant} PV Performance', barmode='stack', xaxis={'range': [start_date, end_date]})
            }
        )

        # Add plant graphs to the container
        graphs.append(html.Div([
            html.H3(f'{plant} Plant'),
            breakdown_graph,
            energy_graph
        ]))


    return graphs

if __name__ == '__main__':
    app.run_server(debug=True)