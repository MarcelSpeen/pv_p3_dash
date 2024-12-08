import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import PySAM.Pvwattsv8 as pvwatts
import numpy as np

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Fetch the weather data from OpenMeteo API
url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": -33.64,  # Latitude for Worcester, South Africa
    "longitude": 19.44,  # Longitude for Worcester, South Africa
    "start_date": "2024-09-27",
    "end_date": "2024-10-11",
    "hourly": ["temperature_2m", "wind_speed_10m", "shortwave_radiation", "diffuse_radiation", "direct_normal_irradiance"]
}
responses = openmeteo.weather_api(url, params=params)

# Process the response to extract hourly data
response = responses[0]
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_wind_speed_10m = hourly.Variables(1).ValuesAsNumpy()
hourly_shortwave_radiation = hourly.Variables(2).ValuesAsNumpy()
hourly_diffuse_radiation = hourly.Variables(3).ValuesAsNumpy()
hourly_direct_normal_irradiance = hourly.Variables(4).ValuesAsNumpy()

# Create a dataframe from the hourly data
hourly_data = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    ),
    "temperature_2m": hourly_temperature_2m,
    "wind_speed_10m": hourly_wind_speed_10m,
    "shortwave_radiation": hourly_shortwave_radiation,
    "diffuse_radiation": hourly_diffuse_radiation,
    "direct_normal_irradiance": hourly_direct_normal_irradiance
}
hourly_dataframe = pd.DataFrame(data=hourly_data)

# Clean the dataframe by filling or dropping NaN values
hourly_dataframe = hourly_dataframe.replace([np.inf, -np.inf], np.nan).dropna()

# Convert the cleaned dataframe to the format needed for PySAM
solar_resource_data = {
    'lat': -33.64,  # Latitude for Worcester, South Africa
    'lon': 19.44,   # Longitude for Worcester, South Africa
    'tz': 2,        # Timezone offset (UTC+2 for South Africa)
    'elev': 230,    # Elevation in meters (approximate for Worcester)
    'data': []
}

# Populate the 'data' list with the hourly data
for i, row in hourly_dataframe.iterrows():
    solar_resource_data['data'].append({
        'year': row['date'].year,
        'month': row['date'].month,
        'day': row['date'].day,
        'hour': row['date'].hour,
        'minute': row['date'].minute,
        'dn': row['direct_normal_irradiance'],  # DNI
        'df': row['diffuse_radiation'],         # DHI
        'gh': row['shortwave_radiation'],       # GHI
        'tdry': row['temperature_2m'],          # Temperature
        'wspd': row['wind_speed_10m']           # Wind Speed
    })

# Setup the PVWatts model
pv_system = pvwatts.default('PVWattsSingleOwner')

print(solar_resource_data)
# Configure the PV system
pv_system.SolarResource.solar_resource_data = solar_resource_data
pv_system.SystemDesign.system_capacity = 30  # 30 kW system
pv_system.SystemDesign.module_type = 0       # Standard module
pv_system.SystemDesign.array_type = 0        # Fixed - Open Rack
pv_system.SystemDesign.tilt = 15             # 15-degree tilt
pv_system.SystemDesign.azimuth = 190         # 180 (south) + 10 deg west of north

# Set system losses
pv_system.SystemDesign.losses = 14  # System losses as percentage

# Run the simulation
pv_system.execute()

# Extract the hourly AC power output in kW
hourly_ac_output = pv_system.Outputs.ac

# Create a dataframe to show the date and PV production
pv_production_df = pd.DataFrame({
    "date": hourly_dataframe["date"],
    "ac_power_kw": hourly_ac_output
})

# Display the date range of the simulation and PV production dataframe
print(f"PV production date range: {pv_production_df['date'].min()} to {pv_production_df['date'].max()}")
print(pv_production_df)
