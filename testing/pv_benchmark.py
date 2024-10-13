import pandas as pd
import pvlib
from PySAM.Pvsamv1 import Pvsamv1
from PySAM.ResourceTools import SRW_to_sam

# Step 1: Define the location
location = pvlib.location.Location(latitude=-33.646, longitude=19.441, tz='Africa/Johannesburg', altitude=200)

# Step 2: Load the historical weather data (GHI, DHI) and process it
# Example data loading (assuming you have a CSV file)
# The CSV should have columns: 'timestamp', 'GHI', 'DHI', 'temperature', 'wind_speed'
weather_data = pd.read_csv('path_to_your_weather_data.csv', parse_dates=['timestamp'], index_col='timestamp')

# Calculate solar zenith, azimuth, and other components
solar_position = location.get_solarposition(weather_data.index)
dni = pvlib.irradiance.dni(weather_data['GHI'], weather_data['DHI'], solar_position['zenith'])
poa_irradiance = pvlib.irradiance.get_total_irradiance(
    surface_tilt=30,  # Assumed tilt angle
    surface_azimuth=180,  # Assumed facing south
    dni=dni,
    ghi=weather_data['GHI'],
    dhi=weather_data['DHI'],
    solar_zenith=solar_position['zenith'],
    solar_azimuth=solar_position['azimuth']
)

# Step 3: Prepare the data for PySAM
# Combine the POA and other weather variables into the PySAM format
weather_data['poa_irradiance'] = poa_irradiance['poa_global']
weather_data['temp_air'] = weather_data['temperature']
weather_data['wind_speed'] = weather_data['wind_speed']
# Create the PySAM-compatible SRW file
srw_file = 'weather_file.srw'
SRW_to_sam(weather_data, srw_file, location.latitude, location.longitude, location.altitude)

# Step 4: Set up the PySAM PV system model
pv_system = Pvsamv1.default("FlatPlatePVSingleOwner")
pv_system.SolarResource.solar_resource_file = srw_file

# System specifications (adjust these parameters as necessary)
pv_system.SystemDesign.system_capacity = 1000  # kW DC
pv_system.SystemDesign.dc_ac_ratio = 1.2
pv_system.SystemDesign.array_type = 0  # Fixed tilt
pv_system.SystemDesign.azimuth = 180
pv_system.SystemDesign.tilt = 30

# Inverter specifications
pv_system.Inverter.inverter_efficiency = 96  # %

# Step 5: Run the simulation
pv_system.execute()

# Step 6: Retrieve the hourly output power data
hourly_kw = pv_system.Outputs.gen  # Hourly AC output in kW

# Step 7: Create a DataFrame with the results
results = pd.DataFrame({
    'timestamp': weather_data.index,
    'hourly_kw': hourly_kw
})

# Save results to a CSV file
results.to_csv('hourly_kw_output.csv', index=False)

print("Simulation complete. Hourly kW values saved to 'hourly_kw_output.csv'.")
