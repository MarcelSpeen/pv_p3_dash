import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np
import pandas as pd

from data_prep.data_helper import DataProcessor

# List of Excel file paths and CSV path
file_paths_b = [
    'p3_plants/boxer/Energy_Report_Boxer_Worcester_Monthly_report_2024_01.xlsx',
    'p3_plants/boxer/Energy_Report_Boxer_Worcester_Monthly_report_2024_02.xlsx',
    'p3_plants/boxer/Energy_Report_Boxer_Worcester_Monthly_report_2024_03.xlsx',
    'p3_plants/boxer/Energy_Report_Boxer_Worcester_Monthly_report_2024_04.xlsx',
    'p3_plants/boxer/Energy_Report_Boxer_Worcester_Monthly_report_2024_05.xlsx',
    'p3_plants/boxer/Energy_Report_Boxer_Worcester_Monthly_report_2024_06.xlsx',
    'p3_plants/boxer/Energy_Report_Boxer_Worcester_Monthly_report_2024_07.xlsx',
    'p3_plants/boxer/KEEROMVIEW__Boxer_Worcester_01082024-15082024.xlsx'
]
csv_path_b = 'p3_plants/boxer/boxer.csv'

# Create DataProcessor object
data_processor_b = DataProcessor(file_paths_b, csv_path_b)

# Load and process Excel files
data_processor_b.load_excel_files()
df_inv_b = data_processor_b.resample_data()
data_processor_b.split_day_night_data()

# Process CSV file
df_hs_p1_b = data_processor_b.load_csv_file()
helioscope_df_b = data_processor_b.process_csv(df_hs_p1_b)

# Grouping data
grid_b, export_b, solar_b, solar_consumed_b = data_processor_b.group_by_date()
grid_day_b, grid_night_b = data_processor_b.group_day_night()

# Create Dash app
app = dash.Dash(__name__)
server = app.server

# Define app layout
app.layout = html.Div([
    html.Div([
        html.H1("P3 PV Dashboard",
                style={'text-align': 'center', 'color': '#000000', 'font-family': 'Arial, sans-serif',
                       'margin-bottom': '20px', 'flex': '1'}),
        html.Img(src='/assets/logo.png',
                 style={'height': '50px', 'width': 'auto', 'display': 'block', 'margin-left': 'auto'}),
        html.Img(src='/assets/P3.png',
                 style={'height': '50px', 'width': 'auto', 'display': 'block', 'margin-left': 'auto'})
    ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'background-color': '#ffffff',
              'padding': '20px'}),
    html.Div(
        html.P("Select the date range to visualize data:",
               style={'text-align': 'center', 'font-family': 'Arial, sans-serif', 'margin-bottom': '10px',
                      'color': '#000000'}),
        style={'text-align': 'center', 'margin-bottom': '20px'}
    ),
    html.Div(
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=df_inv_b.index.min(),
            end_date=df_inv_b.index.max(),
            display_format='YYYY-MM-DD',
            style={'margin': '0 auto', 'width': '60%', 'display': 'block', 'font-family': 'Arial, sans-serif',
                   'background-color': '#ffffff', 'color': '#000000', 'border': 'none'}
        ),
        style={'text-align': 'center', 'margin-bottom': '20px'}
    ),
    html.Div([
        dcc.Graph(id='consumption-breakdown-graph-boxer',
                  style={'width': '100%', 'margin-bottom': '20px',
                         'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19)',
                         'border-radius': '10px', 'background-color': '#ffffff'}),
    ]),
    html.Div([
        dcc.Graph(id='energy-graph-boxer',
                  style={'width': '100%', 'margin-bottom': '20px',
                         'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19)',
                         'border-radius': '10px', 'background-color': '#ffffff'}),
    ]),
    html.Div([
        html.Footer(
            "Developed by VOCMax",
            style={'text-align': 'center', 'font-family': 'Arial, sans-serif', 'color': '#000000',
                   'margin-top': '20px', 'padding': '10px', 'background-color': '#ffffff', 'font-size': '12px'}
        )
    ])
], style={'background-color': '#ffffff', 'padding': '20px', 'font-family': 'Arial, sans-serif'})


# Define callback to update graphs based on selected dates
@app.callback(
    [Output('energy-graph-boxer', 'figure'),
     Output('consumption-breakdown-graph-boxer', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graph(start_date, end_date):

    # Update Energy Graph
    filtered_df_inv_plot_b = df_inv_b.loc[start_date:end_date]
    filtered_df_hs_plot_b = df_hs_p1_b.loc[start_date:end_date]

    export_b.index = pd.to_datetime(export_b.index)
    filtered_export_b = export_b.loc[start_date:end_date]

    solar_consumed_b.index = pd.to_datetime(solar_consumed_b.index)
    filtered_solar_consumed_b = solar_consumed_b.loc[start_date:end_date]

    helioscope_df_b.index = pd.to_datetime(helioscope_df_b.index)
    filtered_helioscope_b = helioscope_df_b.loc[start_date:end_date]

    grid_night_b.index = pd.to_datetime(grid_night_b.index)
    filtered_grid_night_b = grid_night_b.loc[start_date:end_date]

    grid_day_b.index = pd.to_datetime(grid_day_b.index)
    filtered_grid_day_b = grid_day_b.loc[start_date:end_date]

    # comparison_df.index = pd.to_datetime(comparison_df.index)
    # filtered_comparison_df = export.loc[start_date:end_date]

    trace1 = go.Scatter(x=filtered_df_inv_plot_b.index, y=filtered_df_inv_plot_b['PV production'], mode='lines+markers',
                        name='PV production', marker=dict(color='green'))
    trace2 = go.Scatter(x=filtered_df_hs_plot_b.index, y=filtered_df_hs_plot_b['actual_dc_power'],
                        mode='lines+markers', name='Helioscope', marker=dict(color='red'))
    trace3 = go.Scatter(x=filtered_df_inv_plot_b.index, y=filtered_df_inv_plot_b['Consumption'], mode='lines+markers',
                        name='Solar + Grid', marker=dict(color='purple'))
    trace4 = go.Scatter(x=filtered_df_inv_plot_b.index, y=filtered_df_inv_plot_b['Consumed directly'], mode='lines+markers',
                        name='Solar Consumed', marker=dict(color='#FDDA0D'))
    trace5 = go.Scatter(x=filtered_df_inv_plot_b.index, y=filtered_df_inv_plot_b['Energy from grid'], mode='lines+markers',
                        name='Grid', marker=dict(color='#F88379'))
    trace6 = go.Scatter(x=filtered_df_inv_plot_b.index, y=filtered_df_inv_plot_b['Energy to grid'], mode='lines+markers',
                        name='Export', marker=dict(color='#AFE1AF'))

    energy_layout = go.Layout(
        title='Boxer Detailed PV Production',
        xaxis=dict(tickfont=dict(color='#000000'), range=[start_date, end_date]),
        yaxis=dict(title='Energy Wh', tickfont=dict(color='#000000')),
        plot_bgcolor='#ffffff',  # Set plot background color to white
        paper_bgcolor='#ffffff',  # Set paper background color to white
        font=dict(color='#000000'),
        legend=dict(
            x=0.5,  # Adjust the horizontal position of the legend
            y=1,  # Adjust the vertical position of the legend
            orientation='h'  # Set the orientation of the legend to horizontal
        )
        # Set font color to black
    )
    energy_figure_boxer = {'data': [trace1, trace2, trace3, trace4, trace5, trace6],
                     'layout': energy_layout}

    # Update Consumption Breakdown Graph
    breakdown_fig_boxer = go.Figure()

    breakdown_fig_boxer.add_trace(go.Bar(
        x=filtered_solar_consumed_b.index,
        y=filtered_solar_consumed_b.values,
        name='Solar Consumed',
        marker=dict(color='#FDDA0D')
    ))

    breakdown_fig_boxer.add_trace(go.Bar(
        x=filtered_export_b.index,
        y=filtered_export_b.values,
        name='Export',
        marker=dict(color='#AFE1AF'),
        visible='legendonly'
    ))

    breakdown_fig_boxer.add_trace(go.Bar(
        x=filtered_grid_day_b.index,
        y=filtered_grid_day_b.values,
        name='Grid Consumed Day',
        marker=dict(color='#F88379')
    ))

    breakdown_fig_boxer.add_trace(go.Bar(
        x=filtered_grid_night_b.index,
        y=filtered_grid_night_b.values,
        name='Grid Consumed Night',
        marker=dict(color='#6495ED')
    ))

    breakdown_fig_boxer.add_trace(go.Scatter(
        x=filtered_helioscope_b.index,
        y=filtered_helioscope_b['moving_avg'],
        mode='lines',
        name='Helioscope',
        line=dict(color='red', width=3)
    ))


    breakdown_fig_boxer.update_layout(
        title='Boxer PV Performance',
        xaxis_title='Date',
        yaxis_title='Wh',
        barmode='stack',
        xaxis=dict(tickfont=dict(color='#000000'), range=[start_date, end_date]),
        yaxis=dict(tickfont=dict(color='#000000')),
        plot_bgcolor='#ffffff',  # Set plot background color to white
        paper_bgcolor='#ffffff',  # Set paper background color to white
        font=dict(color='#000000'),
        legend=dict(
            x=0.5,  # Adjust the horizontal position of the legend
            y=1,  # Adjust the vertical position of the legend
            orientation='h'  # Set the orientation of the legend to horizontal
        )
        # Set font color to black
    )

    return energy_figure_boxer, breakdown_fig_boxer


if __name__ == '__main__':
    app.run_server(debug=True)
