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

# Assuming you have a function to get a PostgreSQL connection
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
            SELECT 
                DATE(timestamp) AS date,
                SUM(actual_dc_power) AS total_dc_power
            FROM {plant}_hs
            WHERE timestamp BETWEEN :start_date AND :end_date
            GROUP BY DATE(timestamp)
            ORDER BY DATE(timestamp);
        """)
        df_hs_daily = pd.read_sql(query_hs_daily, connection, params={'start_date': start_date, 'end_date': end_date})
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

        grid_day = df_inv.between_time('08:00:00','16:00:00')
        grid_night = df_inv[~df_inv.index.isin(grid_day.index)]
        grid_day = grid_day.groupby(grid_day.index.date).sum()
        grid_night = grid_night.groupby(grid_night.index.date).sum()
        print(df_inv_daily.head())
        # Create the consumption breakdown graph
        breakdown_graph = dcc.Graph(
            id=f'consumption-breakdown-graph-{plant}',
            figure={
                'data': [
                    go.Bar(x=grid_day.index, y=grid_day["Energy from grid"], name='Grid Consumed Day'),
                    go.Bar(x=grid_night.index, y=grid_night["Energy from grid"], name='Grid Consumed Night'),
                    go.Bar(x=df_inv_daily.index, y=df_inv_daily['total_energy_to_grid'], name='Export'),
                    go.Bar(x=df_inv_daily.index, y=df_inv_daily['total_pv_production'], name='PV Production'),
                    go.Bar(x=df_inv_daily.index, y=df_inv_daily['total_consumed_directly'], name='Solar Consumed'),
                    go.Scatter(x=df_hs.index, y=df_hs['actual_dc_power'], mode='lines', name='Helioscope Simulation')
                ],
                'layout': go.Layout(title=f'{plant} PV Performance', barmode='stack', xaxis={'range': [start_date, end_date]})
            }
        )
        # Add plant graphs to the container
        graphs.append(html.Div([
            html.H3(f'{plant} Plant'),
            energy_graph,
            breakdown_graph
        ]))


    return graphs

if __name__ == '__main__':
    app.run_server(debug=True)
