import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go

from data_prep.data_helper import DataProcessor
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


# Example usage get plants
plant_data_paths = get_plant_file_paths('p3_plants')
print(plant_data_paths)
# Create Dash app
app = dash.Dash(__name__)
server = app.server

# Define app layout
app.layout = html.Div([
    html.Div([
        html.H1("P3 PV Dashboard", style={'text-align': 'center'}),
        html.Img(src='/assets/logo.png', style={'height': '50px', 'width': 'auto'}),
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


@app.callback(
    Output('plant-graphs-container', 'children'),
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graphs(start_date, end_date):
    graphs = []
    for plant, paths in plant_data_paths.items():
        # print(plant)
        # print(paths)
        # Load and process data for each plant
        data_processor = DataProcessor(paths['excel_files'], paths['csv_file'])
        data_processor.load_excel_files()
        df_inv = data_processor.resample_data()
        data_processor.split_day_night_data()
        df_hs = data_processor.load_csv_file()
        helioscope_df = data_processor.process_csv(df_hs)
        grid, export, solar, solar_consumed = data_processor.group_by_date()
        grid_day, grid_night = data_processor.group_day_night()

        # Filter data by selected date range
        filtered_df_inv = df_inv.loc[start_date:end_date]
        filtered_helioscope = helioscope_df.loc[start_date:end_date]
        # Debug the filtered data
        print(f"Start: {start_date}   End: {end_date}")
        print(f"{plant} - Filtered Inv Data: {filtered_df_inv.head()}")
        print(f"{plant} - Filtered Helioscope Data: {filtered_helioscope.head()}")

        energy_graph = dcc.Graph(
            id=f'energy-graph-{plant}',
            figure={
                'data': [
                    go.Scatter(x=filtered_df_inv.index, y=filtered_df_inv['PV production'], mode='lines+markers', name='PV production'),
                    go.Scatter(x=filtered_helioscope.index, y=filtered_helioscope['actual_dc_power'], mode='lines+markers', name='Helioscope')
                ],
                'layout': go.Layout(title=f'{plant} Detailed PV Production', xaxis={'range': [start_date, end_date]})
            }
        )

        breakdown_graph = dcc.Graph(
            id=f'consumption-breakdown-graph-{plant}',
            figure={
                'data': [
                    go.Bar(x=grid_day.index, y=grid_day.values, name='Grid Consumed Day'),
                    go.Bar(x=grid_night.index, y=grid_night.values, name='Grid Consumed Night'),
                    go.Scatter(x=filtered_helioscope.index, y=filtered_helioscope['moving_avg'], mode='lines', name='Helioscope')
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
