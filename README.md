#Commands for EC2 connection and file upload

upload: scp -i nsf_apps_keys.pem application.py ubuntu@ec2-3-89-24-162.compute-1.amazonaws.com:apps

# transportationApp

This app is designed to provide driving suggestions for the users based on environmental and traffic data.

API Documentation
------------------------
Base Url: localhost:5001

API: Places
------------------------

# Get list of places setup by the user 
URI: /getPlaces 
Params: user_id (Integer)
Sample request:
{
    "user_id": 2
}

Sample response: 
[
    {'lon': Decimal('-101.139875'), 'user_id': Decimal('3'), 'place_name': 'Broomfield', 'lat': Decimal('41.698452')
    },
    {'lon': Decimal('-107.139875'), 'user_id': Decimal('3'), 'place_name': 'Denver', 'lat': Decimal('35.698452')
    }
]



# Add a new place
URI: /addPlace
Params: 
    "user_id" (Integer),
    "name": (String),
    "lat": (Float/Decimal),
    "lon":(Float/Decimal),
    "tags": (List of String)

Sample request: 
{
    "user_id":3,
    "name": "Broomfield",
    "lat": 41.698452,
    "lon":-101.139875,
    "tags":["Work"]
}
Sample response:

{'ResponseMetadata': {'RequestId': 'KK15HGB2L1OUFUFT351HL1VH47VV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Thu,
            14 Apr 2022 10: 13: 22 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '2', 'connection': 'keep-alive', 'x-amzn-requestid': 'KK15HGB2L1OUFUFT351HL1VH47VV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '2745614147'
        }, 'RetryAttempts': 0
    }
}
    
# Delete a place
URI: /removePlace
Params: 
    "user_id" (Integer),
    "name": (String)

Sample request:
{
    "user_id": 3,
    "name": "Denver"
}
Sample response:

{'ResponseMetadata': {'RequestId': '0HTV909DLS8N2HIJ4I8L9432JBVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Thu,
            14 Apr 2022 19: 30: 50 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '2', 'connection': 'keep-alive', 'x-amzn-requestid': '0HTV909DLS8N2HIJ4I8L9432JBVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '2745614147'
        }, 'RetryAttempts': 0
    }
}

