
import requests
import json
from datetime import datetime
import pandas as pd
url = "https://intl.fusionsolar.huawei.com/thirdData/getKpiStationHour"


# Example datetime object (e.g., 2024-12-04 12:00:00)
dt_object = datetime(2024, 12, 2, 12, 0, 0)

# Convert datetime to timestamp in seconds and then to milliseconds
milliseconds = int(dt_object.timestamp() * 1000)

# Print the result
print(milliseconds)

payload = {
    "stationCodes":"NE=51668944",
    "collectTime":milliseconds
}
headers = {"Content-Type": "application/json",
           "XSRF-TOKEN": "n-5dryjwlj8aurqnnx1ihdmkdh1dryfy857slildjzvxths8g91j5cc8demqfwdgpffsmraq48fz052qg61haodg851es9pd6os96nlek6bxuqdien6k1fnz4888tcphc7"
           }


# Send POST request to the login endpoint
response = requests.post(url, json=payload, headers=headers)

# Extracting plant code and name from the response
response_data = response.json()
pretty_json = json.dumps(response_data, indent=4)
# print(pretty_json)

# Extract the relevant data
data = response_data['data']

# Convert the list of records to a list of dictionaries, including the conversion of collectTime to datetime
processed_data = []
for record in data:
    collect_time = record['collectTime']
    collect_time = datetime.utcfromtimestamp(collect_time / 1000)  # Convert milliseconds to datetime
    data_item_map = record['dataItemMap']

    # Construct the dictionary with the desired columns
    processed_data.append({
        "collectTime": collect_time,
        "dischargeCap": data_item_map.get("dischargeCap"),
        "radiation_intensity": data_item_map.get("radiation_intensity"),
        "inverter_power": data_item_map.get("inverter_power", 0.0),
        "inverterYield": data_item_map.get("inverterYield", 0.0),
        "power_profit": data_item_map.get("power_profit"),
        "theory_power": data_item_map.get("theory_power"),
        "PVYield": data_item_map.get("PVYield", 0.0),
        "ongrid_power": data_item_map.get("ongrid_power"),
        "chargeCap": data_item_map.get("chargeCap"),
        "selfProvide": data_item_map.get("selfProvide")
    })

# Convert the list of dictionaries to a pandas DataFrame
df = pd.DataFrame(processed_data)

#import pandas as pd
import plotly.graph_objects as go


# Initialize a figure
fig = go.Figure()

# Add a trace for each column (excluding 'collectTime')
columns_to_plot = [
    "dischargeCap", "radiation_intensity", "inverter_power",
    "inverterYield", "power_profit", "theory_power",
    "PVYield", "ongrid_power", "chargeCap", "selfProvide"
]

for column in columns_to_plot:
    fig.add_trace(go.Scatter(
        x=df["collectTime"],
        y=df[column],
        mode='lines+markers',
        name=column
    ))

# Update layout
fig.update_layout(
    title="Multiple Metrics Over Time",
    xaxis_title="Collect Time",
    yaxis_title="Values",
    legend_title="Metrics",
    template="plotly_dark"
)

# Show the plot
fig.show()

