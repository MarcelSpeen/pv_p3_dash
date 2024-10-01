import pandas as pd
from sqlalchemy import create_engine

class DataProcessor:
    def __init__(self, excel_paths, csv_path, day_start='08:00:00', day_end='16:00:00'):
        self.excel_paths = excel_paths
        self.csv_path = csv_path
        self.day_start = day_start
        self.day_end = day_end
        self.daytime_data = None
        self.nighttime_data = None
        self.df_combined = None
        self.db_url = "postgresql+psycopg2://marzol:12053@localhost:5432/postgres"
        self.engine = create_engine(self.db_url)

    def load_excel_files(self):
        dataframes = []
        for file_path in self.excel_paths:
            df = pd.read_excel(file_path)
            df.drop(0, inplace=True)
            df['timestamp'] = pd.to_datetime(df['Date and time'], format='%d.%m.%Y %H:%M')
            dataframes.append(df)
        self.df_combined = pd.concat(dataframes)
        self.df_combined.reset_index(drop=True, inplace=True)
        self.df_combined.set_index('timestamp', inplace=True)

    def resample_data(self):
        self.df_combined = self.df_combined.resample('h').sum()
        return self.df_combined

    def split_day_night_data(self):
        self.daytime_data = self.df_combined.between_time(self.day_start, self.day_end)
        self.nighttime_data = self.df_combined[~self.df_combined.index.isin(self.daytime_data.index)]


    def load_csv_file(self):
        df_hs_p1 = pd.read_csv(self.csv_path)
        df_hs_p1['timestamp'] = pd.to_datetime(df_hs_p1['timestamp'])
        df_hs_p1.set_index('timestamp', inplace=True)

        return df_hs_p1

    def process_csv(self, df_hs_p1):
        helioscope = df_hs_p1.groupby(df_hs_p1.index.date)['actual_dc_power'].sum()
        helioscope_df = helioscope.to_frame()
        helioscope_df.index = pd.to_datetime(helioscope_df.index)
        window_size = pd.Timedelta(days=12)
        helioscope_df['moving_avg'] = helioscope_df['actual_dc_power'].rolling(window=window_size).mean()
        return helioscope_df

    def save_to_postgres(self, df, table_name):
        """ Save a dataframe to a PostgreSQL table """
        if df is not None:
            try:
                df.to_sql(table_name, self.engine, if_exists='replace', index=True)
                print(f"Data saved to table '{table_name}' in PostgreSQL.")
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print("No data to save.")


