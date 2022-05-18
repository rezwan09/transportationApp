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
URI: /place/all
Method: GET
Params: user_id (Integer)
Sample request:
{
    "user_id": 2
}

Sample response: 
{
    'Items': [{'user_id': Decimal('3'), 'place_name': 'Boulder', 'lon': Decimal('-102.139875'), 'address': 'Boulder, CO',
        'id': '1652841094075', 'lat': Decimal('45.565656')}], 
    'Count': 1, 
    'ScannedCount': 2, 
    'ResponseMetadata': 
        {
            'RequestId':'DJ0DH1QR9R4SEJN6NSKHL0MLD3VV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server',
            'date': 'Wed, 18 May 2022 02:32:43 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '196',
            'connection': 'keep-alive', 'x-amzn-requestid': 'DJ0DH1QR9R4SEJN6NSKHL0MLD3VV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32':
            '3611774563'}, 'RetryAttempts': 0
        }
    }

# Get a place by id
URI: /place
Method: GET
Params: 
    "id" (Integer)

Sample Request:
{
    "id": 1652580555398
}

Sample response:
{'Item': {'user_id': Decimal('3'), 'place_name': 'Boulder', 'lon': Decimal('-102.139875'), 'address': 'Boulder, CO', 'id': '1652580555398', 'lat': Decimal('45.565656')
    }, 'ResponseMetadata': {'RequestId': 'V2PDPDHL5PAROO0C6EKGLB56JJVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Wed,
            18 May 2022 03: 23: 52 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '166', 'connection': 'keep-alive', 'x-amzn-requestid': 'V2PDPDHL5PAROO0C6EKGLB56JJVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '3255661655'
        }, 'RetryAttempts': 0
    }
}

# Add a new place
URI: /place
Method: POST
Params: 
    "user_id" (Integer),
    "name": (String),
    "address": (String)
    "lat": (Float/Decimal),
    "lon":(Float/Decimal),
    "tags": (List of String)

Sample request: 
{
    "user_id":3,
    "name": "Broomfield",
    "address": "Broomfield, CO"
    "lat": 41.698452,
    "lon":-101.139875,
    "tags":["Work"]
}
Sample response:

{'ResponseMetadata': {'RequestId': '0PI0AQO4SO9OBOQI5HR9B5C12JVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Wed,
            18 May 2022 02: 31: 34 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '2', 'connection': 'keep-alive', 'x-amzn-requestid': '0PI0AQO4SO9OBOQI5HR9B5C12JVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '2745614147'
        }, 'RetryAttempts': 0
    }
}
    
# Delete a place
URI: /place/remove
Params: 
    "id" (Integer)

Sample request:
{
    "id": 1652580555398
}
Sample response:

{'ResponseMetadata': {'RequestId': '66SNB076169UR2V1QO6BFMB63FVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Wed,
            18 May 2022 03: 25: 54 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '2', 'connection': 'keep-alive', 'x-amzn-requestid': '66SNB076169UR2V1QO6BFMB63FVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '2745614147'
        }, 'RetryAttempts': 0
    }
}


#API: Trip
================

# Get a Trip
URI: /trip
Method: POST
Params: 
    "id": (Integer)

Sample Request: 
{
    "id": 1652730118403
}

Sample Response:

{'Item': {'src': '1', 'suggested_routes': ['1', '4', '3', '2'
        ], 'arrived': '05-13-2022 1: 40: 00', 'user_id': '2', 'dst': '2', 'route': ['1', '3', '2'
        ], 'id': '1652730118403', 'started': '05-13-2022 2: 30: 30', 'trip_feedback': 'Good'
    }, 'ResponseMetadata': {'RequestId': '6VCL4T5NRBMOJK6SL5E08DBOCRVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Wed,
            18 May 2022 03: 34: 23 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '305', 'connection': 'keep-alive', 'x-amzn-requestid': '6VCL4T5NRBMOJK6SL5E08DBOCRVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '3201770722'
        }, 'RetryAttempts': 0
    }
}

# Add a Trip
URI: /trip
Method: POST
Params: 
    "user_id" (Integer),
    "src" (String),
    "dst": (String),
    "started" (String),
    "arrived": (String),
    "route": (List of Places),
    "suggested_routes": (List of Places),
    "trip_feedback": (String)

Sample Request: 
{
    "user_id":2,
    "src":"1",
    "dst":"2",
    "started":"05-14-2022 2:56:30",
    "arrived":"05-14-2022 4:40:00",
    "route":["1","3","2"],
    "suggested_routes":["1","4","3","2"],
    "trip_feedback":"Good"
}

Sample response:

{'ResponseMetadata': {'RequestId': '0HTV909DLS8N2HIJ4I8L9432JBVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Thu,
            14 Apr 2022 19: 30: 50 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '2', 'connection': 'keep-alive', 'x-amzn-requestid': '0HTV909DLS8N2HIJ4I8L9432JBVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '2745614147'
        }, 'RetryAttempts': 0
    }
}

# Upcoming Trips 
URI: /trip/upcoming
Method: GET
Params:
    "user_id": 3
    "interval": 24

Sample Request:

{
    "user_id":1,
    "interval":24
}
Sample Response: 

{'Items': [
        {'days_of_week': {'Tuesday': '05-17-2022 20: 45: 00'
            }, 'medium': 'Bus', 'user_id': '1', 'dst': '3'
        }
    ], 'Count': 1, 'ScannedCount': 1, 'ResponseMetadata': {'RequestId': 'NIPEF8V85U959QH8GJ3F1SQCCBVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Wed,
            18 May 2022 03: 35: 37 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '158', 'connection': 'keep-alive', 'x-amzn-requestid': 'NIPEF8V85U959QH8GJ3F1SQCCBVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '2471550643'
        }, 'RetryAttempts': 0
    }
}


# Trips History 
URI: /trip/history
Method: GET
Params:
    "user_id": (Integer)

Sample Request:

{
    "user_id":2
}

Sample Response: 

{'Items': [
        {'src': '1', 'suggested_routes': ['1', '4', '3', '2'
            ], 'arrived': '05-13-2022 1: 40: 00', 'user_id': '2', 'dst': '2', 'route': ['1', '3', '2'
            ], 'id': '1652730118403', 'started': '05-13-2022 2: 30: 30', 'trip_feedback': 'Good'
        },
        {'src': '1', 'suggested_routes': ['1', '4', '3', '2'
            ], 'arrived': '05-14-2022 4: 40: 00', 'user_id': '2', 'dst': '2', 'route': ['1', '3', '2'
            ], 'id': '1652744905975', 'started': '05-14-2022 2: 56: 30', 'trip_feedback': 'Good'
        }
    ], 'Count': 2, 'ScannedCount': 2, 'ResponseMetadata': {'RequestId': 'OMQFIJVO9RF0C4B78RHCIS5H9RVV4KQNSO5AEMVJF66Q9ASUAAJG', 'HTTPStatusCode': 200, 'HTTPHeaders': {'server': 'Server', 'date': 'Wed,
            18 May 2022 03: 41: 16 GMT', 'content-type': 'application/x-amz-json-1.0', 'content-length': '632', 'connection': 'keep-alive', 'x-amzn-requestid': 'OMQFIJVO9RF0C4B78RHCIS5H9RVV4KQNSO5AEMVJF66Q9ASUAAJG', 'x-amz-crc32': '460525836'
        }, 'RetryAttempts': 0
    }
}