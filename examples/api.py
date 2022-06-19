### EXERCISE 1 ###
"""
This API is called 'Open Notify' http://open-notify.org/
It gives access to data about the International Space NASA station!
This API DOES NOT require authentication.

TASK: Make a call to the API endpoint to get live information about astronauts in space

"""



import requests
# from pprint import pprint as pp
#
endpoint1 = 'http://api.open-notify.org/astros.json'  # this endpoint returns data about astronauts currently in space

response = requests.get(endpoint1) # making a call to the API

print(response.status_code)  # make sure that your connection status code is 200, which means success!
#
# data = response.json()  # lets see what data about people in space we get back from the API response
# pp(data)
#
#
# # let's extract data from the response and write it to a file
# # we need section 'people' from json, which is a list of dict, so...
# # we also need to extract name from each dict item in that list
#
# with open('file_handling_astronauts.txt', 'w') as text_file:
#     for item in data['people']:
#         text_file.write(item['name'] + '\n') # added new line character, so each name appears on a new line.


### EXERCISE 2 ###
"""
TASK: Make a call with a 'PAYLOAD' (special requirements) to the API endpoint
"""
# import requests
# from pprint import pprint as pp
#
# # this endpoint tells us timings when the international space station will pass over a **given location** on Earth
# endpoint2 = 'http://api.open-notify.org/iss-pass.json'
#
# # As an input the API expects a latitude/longitude pair for the location of our interst
# # Let's make a dictionary with these parameters, and then include them into our call to the API
# payload = { # these are coordinates for London
#     'lat': 51.507,
#     'lon': 0.1278
# }
# # payload = { # these are coordinates for New York
# #     'lat': 40.71,
# #     'lon': -74,
# # }
#
# response = requests.get(endpoint2, params=payload)
# print(response.status_code)
#
# data = response.json()
# pp(data)



### EXERCISE 3 ###
"""
TASK: Writing a log file to monitor the movement of ISS

Make a call to the API to get the current location for the International Space Station
See what data you get back
Convert the 'timestamp' from the response into readable date and time format
Write a log to the new file that captures time and ISS's location.
"""
# import requests
# from datetime import datetime
# from pprint import pprint as pp
#
# # this endpoint tells the current location for international space station
# endpoint3 = 'http://api.open-notify.org/iss-now.json'
#
# response = # YOUR CODE GOES HERE
#
# data = response.json()
# pp(data)
#
# timestamp = # YOUR CODE GOES HERE
# dt_object = # YOUR CODE GOES HERE TO CONVERT TIMESTAMP INTO READABLE FORMAT
#
# print("dt_object =", dt_object)
# print("type(dt_object) =", type(dt_object))
#
# msg = "At {dt} the ISS was passing the following location, latitude: {lat} and longitude: {lon}".format(
#     dt = dt_object,
#     lat = # add your code,
#     lon = # add your code
# )
#
# # Write a log record to a file
# # Run the program multiple times to get more records in the log
