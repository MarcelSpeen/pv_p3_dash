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


# Example usage to get plant data
plant_data_paths = get_plant_file_paths('p3_plants')

for plant, paths in plant_data_paths.items():
    # Load and process data for each plant
    data_processor = DataProcessor(paths['excel_files'], paths['csv_file'])

    # Load and process inverter data (from Excel)
    data_processor.load_excel_files()
    df_inv = data_processor.resample_data()  # Resampled inverter data

    # Process helioscope data (from CSV)
    df_hs = data_processor.load_csv_file()
    # helioscope_df = data_processor.process_csv(df_hs)

    # # Optionally perform other grouping operations
    # grid, export, solar, solar_consumed = data_processor.group_by_date()
    # grid_day, grid_night = data_processor.group_day_night()

    # Save to PostgreSQL with plant-specific table names
    inv_table_name = f"{plant}_inv"  # Table for inverter data
    hs_table_name = f"{plant}_hs"  # Table for helioscope data

    data_processor.save_to_postgres(df_inv, inv_table_name)
    data_processor.save_to_postgres(df_hs, hs_table_name)

