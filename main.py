import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np
import pandas as pd

# List of file paths
file_paths = [
    'Energy_Report_JET_Worcester_Monthly_report_2024_01.xlsx',
    'Energy_Report_JET_Worcester_Monthly_report_2024_02.xlsx',
    'Energy_Report_JET_Worcester_Monthly_report_2024_03.xlsx',
    'Energy_Report_JET_Worcester_Monthly_report_2024_04.xlsx',
    'Energy_Report_JET_Worcester_Monthly_report_2024_05.xlsx',
    'Energy_Report_JET_Worcester_Monthly_report_2024_06.xlsx',
    'Energy_Report_JET_Worcester_Monthly_report_2024_07.xlsx',
    'AUDENVIEW__JET_Worcester_01082024-15082024.xlsx'
]

# Initialize an empty list to hold dataframes
dataframes = []

# Loop over file paths to read and process each file
for file_path in file_paths:
    # Read excel to dataframe
    df = pd.read_excel(file_path)
    df.drop(0, inplace=True)

    # Convert 'Date and time' column to datetime format
    df['timestamp'] = pd.to_datetime(df['Date and time'], format='%d.%m.%Y %H:%M')

    # Append the dataframe to the list
    dataframes.append(df)

# Concatenate the DataFrames vertically (along the rows)
df_inv = pd.concat(dataframes)

# Reset the index after concatenation
df_inv.reset_index(drop=True, inplace=True)

# Set 'timestamp' as the index again
df_inv.set_index('timestamp', inplace=True)

# Resample the data
df_inv = df_inv.resample('h').sum()
# Filter data for daytime (8 am to 4 pm)
daytime_data = df_inv.between_time('08:00:00', '16:00:00')

# Filter data for nighttime (4 pm to 8 am)
nighttime_data = df_inv[~df_inv.index.isin(daytime_data.index)]

# ------------------------------------------------------

# Define a function to change the   year
def change_year(timestamp):
    return timestamp.replace(year=2024)


# Provide the file paths to your Excel files
file_path1 = 'jet_phase1.csv'
file_path2 = 'jet_phase2.csv'

# Set 'Date and time' as the index
# Read each Excel file into a separate DataFrame

df_hs_p1 = pd.read_csv(file_path1)
df_hs_p2 = pd.read_csv(file_path2)

df_hs_list = [df_hs_p1, df_hs_p2]

for df in df_hs_list:
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)

# Sum the 'actual_dc_power' columns
total_actual_dc_power = df_hs_p1['actual_dc_power'] + df_hs_p2['actual_dc_power']

# Create a new dataframe with the summed values
df_total_actual_dc_power = pd.DataFrame({'total_actual_dc_power': total_actual_dc_power})

# Optionally, you can concatenate this dataframe with the original dataframes
# For example, if you want to keep all the other columns intact
df_hs = pd.concat([df_hs_p1, df_total_actual_dc_power], axis=1)

# Reset the index to make 'timestamp' a regular column
df_hs.reset_index(inplace=True)

# Apply the change_year function to the 'timestamp' column
df_hs['timestamp'] = df_hs['timestamp'].apply(change_year)

# Set 'timestamp' column back as the index
df_hs.set_index('timestamp', inplace=True)

grid = df_inv.groupby(df_inv.index.date)['Energy from grid'].sum()
export = df_inv.groupby(df_inv.index.date)['Energy to grid'].sum()
solar = df_inv.groupby(df_inv.index.date)['PV production'].sum()
solar_consumed = df_inv.groupby(df_inv.index.date)['Consumed directly'].sum()
helioscope = df_hs.groupby(df_hs.index.date)['total_actual_dc_power'].sum()
helioscope_df = helioscope.to_frame()
# Convert index to datetime if it's not already
helioscope_df.index = pd.to_datetime(helioscope_df.index)

# Define the window size (30 days)
window_size = pd.Timedelta(days=12)

# Calculate the moving average of the daily total_actual_dc_power
helioscope_df['moving_avg'] = helioscope_df['total_actual_dc_power'].rolling(window=window_size).mean()


grid_day = daytime_data.groupby(daytime_data.index.date)['Energy from grid'].sum()
grid_night = nighttime_data.groupby(nighttime_data.index.date)['Energy from grid'].sum()



# =====================================================

# List of file paths
file_paths_b = [
    'Energy_Report_Boxer_Worcester_Monthly_report_2024_01.xlsx',
    'Energy_Report_Boxer_Worcester_Monthly_report_2024_02.xlsx',
    'Energy_Report_Boxer_Worcester_Monthly_report_2024_03.xlsx',
    'Energy_Report_Boxer_Worcester_Monthly_report_2024_04.xlsx',
    'Energy_Report_Boxer_Worcester_Monthly_report_2024_05.xlsx',
    'Energy_Report_Boxer_Worcester_Monthly_report_2024_06.xlsx',
    'Energy_Report_Boxer_Worcester_Monthly_report_2024_07.xlsx',
    'KEEROMVIEW__Boxer_Worcester_01082024-15082024.xlsx'
]

# Initialize an empty list to hold dataframes
dataframes_b = []

# Loop over file paths to read and process each file
for file_path in file_paths_b:
    # Read excel to dataframe
    df = pd.read_excel(file_path)
    df.drop(0, inplace=True)

    # Convert 'Date and time' column to datetime format
    df['timestamp'] = pd.to_datetime(df['Date and time'], format='%d.%m.%Y %H:%M')

    # Append the dataframe to the list
    dataframes_b.append(df)

# Concatenate the DataFrames vertically (along the rows)
df_inv_b = pd.concat(dataframes_b)

# Reset the index after concatenation
df_inv_b.reset_index(drop=True, inplace=True)

# Set 'timestamp' as the index again
df_inv_b.set_index('timestamp', inplace=True)

# Resample the data
df_inv_b = df_inv_b.resample('h').sum()
# Filter data for daytime (8 am to 4 pm)
daytime_data_b = df_inv_b.between_time('08:00:00', '16:00:00')

# Filter data for nighttime (4 pm to 8 am)
nighttime_data_b = df_inv_b[~df_inv_b.index.isin(daytime_data_b.index)]

# ------------------------------------------------------

# Define a function to change the   year
def change_year(timestamp):
    return timestamp.replace(year=2024)


# Provide the file paths to your Excel files
file_path1_b = 'boxer.csv'

# Set 'Date and time' as the index
# Read each Excel file into a separate DataFrame

df_hs_p1_b = pd.read_csv(file_path1_b)
df_hs_p1_b['timestamp'] = pd.to_datetime(df_hs_p1_b['timestamp'])
df_hs_p1_b.set_index('timestamp', inplace=True)

# Reset the index to make 'timestamp' a regular column
df_hs_p1_b.reset_index(inplace=True)

# Apply the change_year function to the 'timestamp' column
df_hs_p1_b['timestamp'] = df_hs_p1_b['timestamp'].apply(change_year)

# Set 'timestamp' column back as the index
df_hs_p1_b.set_index('timestamp', inplace=True)

grid_b = df_inv_b.groupby(df_inv_b.index.date)['Energy from grid'].sum()
export_b = df_inv_b.groupby(df_inv_b.index.date)['Energy to grid'].sum()
solar_b = df_inv_b.groupby(df_inv_b.index.date)['PV production'].sum()
solar_consumed_b = df_inv_b.groupby(df_inv_b.index.date)['Consumed directly'].sum()
helioscope_b = df_hs_p1_b.groupby(df_hs_p1_b.index.date)['actual_dc_power'].sum()
helioscope_df_b = helioscope_b.to_frame()

# Convert index to datetime if it's not already
helioscope_df_b.index = pd.to_datetime(helioscope_df_b.index)

# Define the window size (30 days)
window_size = pd.Timedelta(days=12)

# Calculate the moving average of the daily total_actual_dc_power
helioscope_df_b['moving_avg'] = helioscope_df_b['actual_dc_power'].rolling(window=window_size).mean()

grid_day_b = daytime_data_b.groupby(daytime_data_b.index.date)['Energy from grid'].sum()
grid_night_b = nighttime_data_b.groupby(nighttime_data_b.index.date)['Energy from grid'].sum()

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
            start_date=df_inv.index.min(),
            end_date=df_inv.index.max(),
            display_format='YYYY-MM-DD',
            style={'margin': '0 auto', 'width': '60%', 'display': 'block', 'font-family': 'Arial, sans-serif',
                   'background-color': '#ffffff', 'color': '#000000', 'border': 'none'}
        ),
        style={'text-align': 'center', 'margin-bottom': '20px'}
    ),
    html.Div([
        dcc.Graph(id='consumption-breakdown-graph-jet',
                  style={'width': '100%', 'margin-bottom': '20px',
                         'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19)',
                         'border-radius': '10px', 'background-color': '#ffffff'}),
    ]),
    html.Div([
        dcc.Graph(id='energy-graph-jet',
                  style={'width': '100%', 'margin-bottom': '20px',
                         'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19)',
                         'border-radius': '10px', 'background-color': '#ffffff'}),
    ]),
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
    [Output('energy-graph-jet', 'figure'),
     Output('consumption-breakdown-graph-jet', 'figure'),
     Output('energy-graph-boxer', 'figure'),
     Output('consumption-breakdown-graph-boxer', 'figure')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graph(start_date, end_date):
    # Update Energy Graph

    filtered_df_inv_plot = df_inv.loc[start_date:end_date]
    filtered_df_hs_plot = df_hs.loc[start_date:end_date]

    export.index = pd.to_datetime(export.index)
    filtered_export = export.loc[start_date:end_date]

    solar_consumed.index = pd.to_datetime(solar_consumed.index)
    filtered_solar_consumed = solar_consumed.loc[start_date:end_date]

    helioscope_df.index = pd.to_datetime(helioscope.index)
    filtered_helioscope = helioscope_df.loc[start_date:end_date]

    grid_night.index = pd.to_datetime(grid_night.index)
    filtered_grid_night = grid_night.loc[start_date:end_date]

    grid_day.index = pd.to_datetime(grid_day.index)
    filtered_grid_day = grid_day.loc[start_date:end_date]

    # comparison_df.index = pd.to_datetime(comparison_df.index)
    # filtered_comparison_df = export.loc[start_date:end_date]

    trace1 = go.Scatter(x=filtered_df_inv_plot.index, y=filtered_df_inv_plot['PV production'], mode='lines+markers',
                        name='PV production', marker=dict(color='green'))
    trace2 = go.Scatter(x=filtered_df_hs_plot.index, y=filtered_df_hs_plot['total_actual_dc_power'],
                        mode='lines+markers', name='Helioscope', marker=dict(color='red'))
    trace3 = go.Scatter(x=filtered_df_inv_plot.index, y=filtered_df_inv_plot['Consumption'], mode='lines+markers',
                        name='Solar + Grid', marker=dict(color='purple'))
    trace4 = go.Scatter(x=filtered_df_inv_plot.index, y=filtered_df_inv_plot['Consumed directly'], mode='lines+markers',
                        name='Solar', marker=dict(color='#FDDA0D'))
    trace5 = go.Scatter(x=filtered_df_inv_plot.index, y=filtered_df_inv_plot['Energy from grid'], mode='lines+markers',
                        name='Grid', marker=dict(color='#F88379'))
    trace6 = go.Scatter(x=filtered_df_inv_plot.index, y=filtered_df_inv_plot['Energy to grid'], mode='lines+markers',
                        name='Export', marker=dict(color='#AFE1AF'))

    energy_layout = go.Layout(
        title='Jet Detailed PV Production',
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
    energy_figure_jet = {'data': [trace1, trace2, trace3, trace4, trace5, trace6],
                     'layout': energy_layout}

    # Update Consumption Breakdown Graph
    breakdown_fig_jet = go.Figure()

    breakdown_fig_jet.add_trace(go.Bar(
        x=filtered_solar_consumed.index,
        y=filtered_solar_consumed.values,
        name='Solar Consumed',
        marker=dict(color='#FDDA0D')
    ))

    breakdown_fig_jet.add_trace(go.Bar(
        x=filtered_export.index,
        y=filtered_export.values,
        name='Export',
        marker=dict(color='#AFE1AF'),
        visible='legendonly'
    ))

    breakdown_fig_jet.add_trace(go.Bar(
        x=filtered_grid_day.index,
        y=filtered_grid_day.values,
        name='Grid Consumed Day',
        marker=dict(color='#F88379')
    ))

    breakdown_fig_jet.add_trace(go.Bar(
        x=filtered_grid_night.index,
        y=filtered_grid_night.values,
        name='Grid Consumed Night',
        marker=dict(color='#6495ED')
    ))

    breakdown_fig_jet.add_trace(go.Scatter(
        x=filtered_helioscope.index,
        y=filtered_helioscope['moving_avg'],
        mode='lines',
        name='Helioscope',
        line=dict(color='red', width=3)
    ))


    breakdown_fig_jet.update_layout(
        title='JET PV Performance',
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

    # Update Energy Graph
    filtered_df_inv_plot_b = df_inv_b.loc[start_date:end_date]
    filtered_df_hs_plot_b = df_hs_p1_b.loc[start_date:end_date]

    export_b.index = pd.to_datetime(export.index)
    filtered_export_b = export.loc[start_date:end_date]

    solar_consumed_b.index = pd.to_datetime(solar_consumed.index)
    filtered_solar_consumed_b = solar_consumed.loc[start_date:end_date]

    helioscope_df_b.index = pd.to_datetime(helioscope_b.index)
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

    return energy_figure_jet, breakdown_fig_jet, energy_figure_boxer, breakdown_fig_boxer


if __name__ == '__main__':
    app.run_server(debug=True)
