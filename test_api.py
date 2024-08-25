# Access data:
# accessKeyId: FKIA761F374A554F4F34945ED10BDCB971A8
# accessKeyValue: 1d3d27dd-d45f-4742-978c-54aceaf578dc
# accessKeyExpiration: 2024-11-18T23:59:59Z
import pandas as pd
import requests
import json

# Access data
ACCESS_KEY_ID = "FKIA761F374A554F4F34945ED10BDCB971A8"
ACCESS_KEY_VALUE = "1d3d27dd-d45f-4742-978c-54aceaf578dc"

# API URL with query parameters
url = "https://api.solarweb.com/swqapi/pvsystems/4d73d7f5-2957-4c38-b45e-747367165caf/histdata"
params = {
    "from": "2024-08-20T10:00:00Z",
    "to": "2024-08-21T10:00:00Z"
}

# Headers
headers = {
    "accept": "application/json",
    "AccessKeyId": ACCESS_KEY_ID,
    "AccessKeyValue": ACCESS_KEY_VALUE
}

# Sending GET request
response = requests.get(url, headers=headers, params=params)
data = response.json()
# Access the "data" field
# print(data["data"])
pretty_json = json.dumps(data, indent=4)
print(pretty_json)

records = []

# Extract relevant data
for entry in data['data']:
    log_datetime = entry['logDateTime']
    log_duration = entry['logDuration']
    channels_dict = {channel['channelName']: channel['value'] for channel in entry['channels']}

    # Create a record with the required fields
    record = {
        'logDateTime': log_datetime,
        'logDuration': log_duration,
        'EnergySelfConsumption': channels_dict.get('EnergySelfConsumption', None)*3600/log_duration,
        'EnergyFeedIn': channels_dict.get('EnergyFeedIn', None)*3600/log_duration,
        'EnergyPurchased': channels_dict.get('EnergyPurchased', None)*3600/log_duration,
        'EnergyOutput': channels_dict.get('EnergyOutput', None)*3600/log_duration,
        'EnergySelfConsumptionTotal': channels_dict.get('EnergySelfConsumptionTotal', None)*3600/log_duration,
        'EnergyConsumptionTotal': channels_dict.get('EnergyConsumptionTotal', None)*3600/log_duration,
        'EnergyProductionTotal': channels_dict.get('EnergyProductionTotal', None)*3600/log_duration,
        # Example of how to include one specific value
    }

    # Add the record to the list
    records.append(record)

# Convert the list of records into a DataFrame
df = pd.DataFrame(records)

# Print the DataFrame
print(df)





#
# # Output the "data" list
# print(data)
# # Handling the response
# if response.status_code == 200:
#     data = response.json()
#     print("Data received:")
#     # pretty_json = json.dumps(data, indent=4)
#     # print(pretty_json[])
#     print(response["data"])
#
# else:
#     print(f"Request failed with status code {response.status_code}: {response.text}")
# #
# # Extracting data and transforming it into a DataFrame
# rows = []
# for entry in data["data"]:
#     log_datetime = entry["logDateTime"]
#     log_duration = entry["logDuration"]
#
#     for channel in entry["channels"]:
#         row = {
#             "logDateTime": log_datetime,
#             "logDuration": log_duration,
#             "channelName": channel["channelName"],
#             "channelType": channel["channelType"],
#             "unit": channel["unit"],
#             "value": channel["value"]
#         }
#         rows.append(row)
#
# # Create DataFrame
# df = pd.DataFrame(rows)
# #
# # # Power [W] = Energy [Wh] * 3600 / logDuration [s]
# #
# # # 6.5.3 Determine PV Energy and Load Energy
# # # PV Energy = EnergySelfConsumption + EnergyFeedIn + EnergyBattCharge
# # # Load Energy = EnergySelfConsumption + EnergyPurchased + EnergyBattDischarged
# print(df.columns)

