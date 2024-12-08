
import requests

url = "https://intl.fusionsolar.huawei.com/thirdData/stations"

payload = {
  "pageNo": 1
  # "gridConnectedStartTime":1664718569000,
  # "gridConnectedEndTime":1667396969000
}
headers = {"Content-Type": "application/json",
           "XSRF-TOKEN": "n-vyjtdiqpvytdo8mm04k52mti84ar9j8bfyfy1fo8jvbv45mmdjo9enkbg95f8ahinz2r9ilefytiql07hdc5479h882nqleruohe3shc6q2oqmry8b1galtfk7ftdgns"
           }


# Send POST request to the login endpoint
response = requests.post(url, json=payload, headers=headers)
print("Raw Response:", response.text)
# Extracting plant code and name from the response
response_data = response.json()
plant_info = [(plant['plantCode'], plant['plantName']) for plant in response_data['data']['list']]
print(plant_info)


# response = requests.post(login_url, json=payload, headers=headers)
#
# # Check if login is successful
# if response.status_code == 200:
#     # Extract the XSRF-TOKEN from cookies or headers
#     xsrf_token = response.cookies.get('XSRF-TOKEN')  # You may also check response.headers for XSRF-TOKEN
#
#     # Verify that the token exists
#     if xsrf_token:
#         print("XSRF-TOKEN:", xsrf_token)
#
#         # Use the token in subsequent API requests
#         subsequent_url = "https://intl.fusionsolar.huawei.com/rest/openapi/v1/queryPlantList"
#         headers.update({
#             "Authorization": f"Bearer {token}",  # Use the access token from the login response
#             "XSRF-TOKEN": xsrf_token  # Include the XSRF-TOKEN in the headers
#         })
#
#         # Send request to retrieve plant list
#         response = requests.get(subsequent_url, headers=headers)
#
#         if response.status_code == 200:
#             print("Plant List:", response.json())
#         else:
#             print(f"Error: {response.status_code}, {response.text}")
#     else:
#         print("XSRF-TOKEN not found in the response.")
# else:
#     print(f"Login failed: {response.status_code}, {response.text}")
#
# # Ensure you have a valid token from the login process
# token = "your_access_token"  # Replace with your actual token
#
# url = "https://eu5.fusionsolar.huawei.com/rest/openapi/v1/queryPlantList"
# headers = {
#     "Authorization": f"Bearer {token}",
#     "Content-Type": "application/json"
# }
#
# # Optional: You can add parameters, such as the page or filter parameters
# params = {
#     "pageNo": 1,  # Page number for pagination (optional)
#     "pageSize": 10  # Number of results per page (optional)
# }
#
# # Send GET request
# response = requests.get(url, headers=headers, params=params)
#
# # Check if the request was successful
# if response.status_code == 200:
#     plant_list = response.json()
#     print("Plant List:", plant_list)
# else:
#     print(f"Error: {response.status_code}, {response.text}")


