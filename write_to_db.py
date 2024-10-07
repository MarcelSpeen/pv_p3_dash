from data_prep.data_helper import DataProcessor
import os
import pandas as pd


def change_year(timestamp):
    return timestamp.replace(year=2024)


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


# Example usage to get plant data
plant_data_paths = get_plant_file_paths('p3_plants')

for plant, paths in plant_data_paths.items():
    print(f"Starting with {plant}")
    # Load and process data for each plant
    data_processor = DataProcessor(paths['excel_files'], paths['csv_file'])

    # # Load and process inverter data (from Excel)
    data_processor.load_excel_files()
    df_inv = data_processor.resample_data()  # Resampled inverter data

    # Process helioscope data (from CSV)
    df_hs = data_processor.load_csv_file()
    helioscope_df = data_processor.process_csv(df_hs)


    # Save to PostgreSQL with plant-specific table names
    inv_table_name = f"{plant}_inv"  # Table for inverter data
    hs_table_name = f"{plant}_hs"  # Table for helioscope data
    hs_daily_name = f"{plant}_hs_daily"

    data_processor.save_to_postgres(df_inv, inv_table_name)
    data_processor.save_to_postgres(df_hs, hs_table_name)
    data_processor.save_to_postgres(helioscope_df, hs_daily_name)

#  TODO: add functionality to add 2 csv sites together like that was used for JET
#
# # Provide the file paths to your Excel files
# file_path1 = 'p3_plants/jet/jet_phase1.csv'
# file_path2 = 'p3_plants/jet/jet_phase2.csv'
#
# # Set 'Date and time' as the index
# # Read each Excel file into a separate DataFrame
#
# df_hs_p1 = pd.read_csv(file_path1)
# df_hs_p2 = pd.read_csv(file_path2)
#
# df_hs_list = [df_hs_p1, df_hs_p2]
#
# for df in df_hs_list:
#     df['timestamp'] = pd.to_datetime(df['timestamp'])
#     df.set_index('timestamp', inplace=True)
#
# # Sum the 'actual_dc_power' columns
# total_actual_dc_power = df_hs_p1['actual_dc_power'] + df_hs_p2['actual_dc_power']
#
# # Create a new dataframe with the summed values
# df_total_actual_dc_power = pd.DataFrame({'total_actual_dc_power': total_actual_dc_power})
#
# # Optionally, you can concatenate this dataframe with the original dataframes
# # For example, if you want to keep all the other columns intact
# df_hs = pd.concat([df_hs_p1, df_total_actual_dc_power], axis=1)
# df_hs
# # Reset the index to make 'timestamp' a regular column
# df_hs.reset_index(inplace=True)
