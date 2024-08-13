import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np
import pandas as pd

# FRONIUS DATA IMPORT
# Provide the file paths to your Excel files
file_path1 = 'Energy_Report_JET_Worcester_Monthly_report_2024_01.xlsx'

# Read excel to dataframe
df_inv1 = pd.read_excel(file_path1)
df_inv1.drop(0, inplace=True)

# Provide the file paths to your Excel files
file_path2 = 'Energy_Report_JET_Worcester_Monthly_report_2024_02.xlsx'

# Read excel to dataframe
df_inv2 = pd.read_excel(file_path2)
df_inv2.drop(0, inplace=True)

# Provide the file paths to your Excel files
file_path3 = 'Energy_Report_JET_Worcester_Monthly_report_2024_03.xlsx'

# Read excel to dataframe
df_inv3 = pd.read_excel(file_path3)
df_inv3.drop(0, inplace=True)

# Provide the file paths to your Excel files
file_path4 = 'Energy_Report_JET_Worcester_Monthly_report_2024_04.xlsx'

# Read excel to dataframe
df_inv4 = pd.read_excel(file_path4)
df_inv4.drop(0, inplace=True)

# Provide the file paths to your Excel files
file_path5 = 'AUDENVIEW__JET_Worcester_01052024-30052024.xlsx'

# Read excel to dataframe
df_inv5 = pd.read_excel(file_path5)
df_inv5.drop(0, inplace=True)

# Convert 'Date and time' column to datetime format
df_inv1['timestamp'] = pd.to_datetime(df_inv1['Date and time'], format='%d.%m.%Y %H:%M')

# Convert 'Date and time' column to datetime format
df_inv2['timestamp'] = pd.to_datetime(df_inv2['Date and time'], format='%d.%m.%Y %H:%M')

# Convert 'Date and time' column to datetime format
df_inv3['timestamp'] = pd.to_datetime(df_inv3['Date and time'], format='%d.%m.%Y %H:%M')

# Convert 'Date and time' column to datetime format
df_inv4['timestamp'] = pd.to_datetime(df_inv4['Date and time'], format='%d.%m.%Y %H:%M')
#
# Convert 'Date and time' column to datetime format
df_inv5['timestamp'] = pd.to_datetime(df_inv5['Date and time'], format='%d.%m.%Y %H:%M')

# Concatenate the DataFrames vertically (along the rows)
df_inv = pd.concat([df_inv1, df_inv2, df_inv3, df_inv4, df_inv5])

# Reset the index after concatenation
df_inv.reset_index(drop=True, inplace=True)

# Set 'timestamp' as the index again
df_inv.set_index('timestamp', inplace=True)
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

# Create Dash app
app = dash.Dash(__name__)
server = app.server

# Define app layout
app.layout = html.Div([
    html.Div(
        html.H1("P3 PV Dashboard",
                style={'text-align': 'center', 'color': '#000000', 'font-family': 'Arial, sans-serif',
                       'margin-bottom': '20px'}),
        style={'background-color': '#ffffff', 'padding': '20px'}
    ),
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
        dcc.Graph(id='consumption-breakdown-graph',
                  style={'width': '100%', 'margin-bottom': '20px',
                         'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19)',
                         'border-radius': '10px', 'background-color': '#ffffff'}),
    ]),
    # html.Div([
    #     dcc.Graph(id='consumption-grid-solar-graph',
    #               style={'width': '100%', 'margin-bottom': '20px',
    #                      'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19)',
    #                      'border-radius': '10px', 'background-color': '#ffffff'})
    # ]),
    html.Div([
        dcc.Graph(id='energy-graph',
                  style={'width': '100%', 'margin-bottom': '20px',
                         'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19)',
                         'border-radius': '10px', 'background-color': '#ffffff'}),
    ])
    # html.Div([
    #     dcc.Graph(id='ghi-graph',
    #               style={'width': '100%', 'margin-bottom': '20px',
    #                      'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2), 0 6px 20px 0 rgba(0,0,0,0.19)',
    #                      'border-radius': '10px', 'background-color': '#ffffff'})
    # ])
], style={'background-color': '#ffffff', 'padding': '20px', 'font-family': 'Arial, sans-serif'})


# Define callback to update graphs based on selected dates
@app.callback(
    [Output('energy-graph', 'figure'),
     Output('consumption-breakdown-graph', 'figure')],
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
                        mode='lines+markers', name='Helioscope', marker=dict(color='orange'))
    trace3 = go.Scatter(x=filtered_df_inv_plot.index, y=filtered_df_inv_plot['Consumption'], mode='lines+markers',
                        name='Solar + Grid', marker=dict(color='yellow'))
    trace4 = go.Scatter(x=filtered_df_inv_plot.index, y=filtered_df_inv_plot['Consumed directly'], mode='lines+markers',
                        name='Solar', marker=dict(color='blue'))
    trace5 = go.Scatter(x=filtered_df_inv_plot.index, y=filtered_df_inv_plot['Energy from grid'], mode='lines+markers',
                        name='Grid', marker=dict(color='red'))
    trace6 = go.Scatter(x=filtered_df_inv_plot.index, y=filtered_df_inv_plot['Energy to grid'], mode='lines+markers',
                        name='Export', marker=dict(color='purple'))

    energy_layout = go.Layout(
        title='Jet PV',
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
    energy_figure = {'data': [trace1, trace2, trace3, trace4, trace5, trace6],
                     'layout': energy_layout}

    # Update Consumption Breakdown Graph
    breakdown_fig = go.Figure()

    breakdown_fig.add_trace(go.Bar(
        x=filtered_solar_consumed.index,
        y=filtered_solar_consumed.values,
        name='Solar Consumed',
        marker=dict(color='#FDDA0D')
    ))

    breakdown_fig.add_trace(go.Bar(
        x=filtered_export.index,
        y=filtered_export.values,
        name='Export',
        marker=dict(color='#AFE1AF'),
        visible='legendonly'
    ))

    breakdown_fig.add_trace(go.Bar(
        x=filtered_grid_day.index,
        y=filtered_grid_day.values,
        name='Grid Consumed Day',
        marker=dict(color='#F88379')
    ))

    breakdown_fig.add_trace(go.Bar(
        x=filtered_grid_night.index,
        y=filtered_grid_night.values,
        name='Grid Consumed Night',
        marker=dict(color='#6495ED')
    ))

    breakdown_fig.add_trace(go.Scatter(
        x=filtered_helioscope.index,
        y=filtered_helioscope['moving_avg'],
        mode='lines',
        name='Helioscope',
        line=dict(color='red', width=3)
    ))


    breakdown_fig.update_layout(
        title='PV Performance',
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

    return energy_figure, breakdown_fig


if __name__ == '__main__':
    app.run_server(debug=True)
