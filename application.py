from flask import Flask, request, jsonify
import boto3
import json
from decimal import Decimal
from datetime import datetime, timedelta
import calendar
import time
import googlemaps
from boto3.dynamodb.conditions import Key, Attr

application = app = Flask(__name__)

gmaps = googlemaps.Client(key="AIzaSyBoBDraxeL4lK2Ds0fwqNRm-acp6_b1PzY")

# Geocoding an address and Look up an address with reverse geocoding
# geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')
# gmaps.reverse_geocode((40.714224, -73.961452))

now = datetime.now()


@app.route('/')
def index():
    print("Got request in server")
    return "Hello World!"


@app.route('/place/all', methods=['GET'])
def get_places():
    # Get list of places by user_id
    res = db_get_places(request.get_json())
    return res


@app.route('/place', methods=['GET'])
def get_place():
    res = db_get_place(request.get_json())
    return res


@app.route('/place', methods=['POST'])
def add_place():
    """ This will do insert or update"""
    res = db_add_place(request.get_json())
    return res


@app.route('/updatePlace', methods=['POST'])
def update_place():
    """ Not needed currently"""
    res = db_update_place(request.get_json())
    return res


@app.route('/place/remove', methods=['POST'])
def remove_place():
    res = db_delete_place(request.get_json())
    return res


@app.route('/trip', methods=['GET'])
def get_trip():
    res = db_get_trip(request.get_json())
    return res


@app.route('/trip', methods=['POST'])
def add_trip():
    res = db_add_trip(request.get_json())
    return res


@app.route('/trip/remove', methods=['POST'])
def remove_trip():
    res = db_delete_trip(request.get_json())
    return res


@app.route('/trip/next', methods=['GET'])
def view_next_trip():
    # Get one next trip
    res = db_view_next_trip(request.get_json())
    return res


@app.route('/trip/start', methods=['POST'])
def start_trip():
    # Initiate this trip
    res = db_start_trip(request.get_json())
    return res


@app.route('/trip/end', methods=['POST'])
def end_trip():
    # End this trip
    res = db_end_trip(request.get_json())
    return res


@app.route('/trip/upcoming', methods=['GET'])
def view_upcoming_trips():
    # Get all the trips within certain days, that are planned in the preference table
    res = db_view_upcoming_trips(request.get_json())
    return res


@app.route('/trip/history', methods=['GET'])
def view_trip_history():
    user_id = request.get_json().get("user_id")
    res = db_view_trip_history(user_id)
    return res


@app.route('/addRoutePreference', methods=['POST'])
def add_route_pref():
    res = db_add_route_pref(request.get_json())
    return res


# Get the fastest and safest routes
@app.route('/routes', methods=['GET'])
def get_routes():
    res = db_get_routes(request.get_json())
    return res


def db_add_place(item):
    table_name = "place"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    item = json.loads(json.dumps(item), parse_float=Decimal)
    # Timestamp in milliseconds to use as generated id, otherwise use provided id for update
    new_id = item.get('id')
    if item.get('id') == "" or item.get('id') is None:
        new_id = round(time.time() * 1000)

    response = table.put_item(
        Item={
            'id': str(new_id),
            'user_id': item.get("user_id"),
            'place_name': item.get("name"),
            'address': item.get("address"),
            'lat': item.get("lat"),
            'lon': item.get("lon")
        }
    )
    print(response)
    return response


def db_get_place(item):
    table_name = "place"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    # Get the item with the key
    response = table.get_item(
        Key={
            'id': str(item.get("id"))
        }
    )
    response = json.dumps(response, default=default_json)
    return response


def default_json(t):
    return f'{t}'


def db_update_place(item):
    table_name = "place"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    item = json.loads(json.dumps(item), parse_float=Decimal)

    response = table.update_item(
        Key={
            'id': str(item.get("id"))
        },
        UpdateExpression='SET place_name = :new_name',
        ExpressionAttributeValues={
            ':new_name': item.get("name")
        }
    )
    return response


def db_get_trip(item):
    table_name = "trip"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    # Get the item with the key
    response = table.get_item(
        Key={
            'id': str(item.get("id"))
        }
    )

    return response


def db_add_trip(item):
    table_name = "trip"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    item = json.loads(json.dumps(item), parse_float=Decimal)
    # Timestamp in milliseconds to use as generated id, otherwise use provided id for update
    new_id = item.get('id')
    if item.get('id') == "" or item.get('id') is None:
        new_id = round(time.time() * 1000)
    response = table.put_item(
        Item={
            'id': str(new_id),
            'user_id': str(item.get("user_id")),
            'src': item.get("src"),
            'src_lat': item.get("src_lat"),
            'src_lon': item.get("src_lon"),
            'dst': item.get("dst"),
            'started': item.get("started"),
            'arrived': item.get("arrived"),
            'scheduled_arrival': item.get("scheduled_arrival"),
            'trip_status': item.get("trip_status"),
            'route': item.get("route"),
            'suggested_routes': item.get("suggested_routes"),
            'trip_feedback': item.get("trip_feedback")
        }
    )
    return response


def db_add_route_pref(item):
    table_name = "user_route_preference"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    response = table.put_item(
        Item={
            'user_id': item.get("user_id"),
            'dst': item.get("dst"),
            'medium': item.get("medium"),
            'days_of_week': item.get("days_of_week")
        }
    )
    return response


def db_delete_place(item):
    table_name = "place"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    response = table.delete_item(
        Key={
            'id': str(item.get("id"))
        }
    )
    return response


def db_delete_trip(item):
    """
    :param uid: user id
    :param tripid: id of the trip in table
    :return: delete the trip by tripid or trips by user id
    """
    table_name = "trip"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)
    print("in delete trip")
    response = table.delete_item(
        Item={
            'id': item.get("id")
        }
    )
    return response


def db_view_next_trip(item):
    # Connection and resources
    table_name = "user_route_preference"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")

    # Get the params
    user_id = request.get_json().get("user_id")
    from_time = datetime.now()
    from_time = from_time.strftime("%m-%d-%Y %H:%M:%S")

    fe = Attr('user_id').eq(user_id) and Attr('arrived').gte(from_time)
    # Scan table with filters
    trip_table = dynamodb.Table("trip")
    response = trip_table.scan(
        FilterExpression=fe,
        Limit=1
    )
    return response


def db_start_trip(item):
    table_name = "trip"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    item = json.loads(json.dumps(item), parse_float=Decimal)
    response = table.update_item(
        Key={
            'id': str(item.get("id"))
        },
        UpdateExpression='SET trip_status = :ts, started = :started, '
                         'src = :src, src_lat = :src_lat, src_lon = :src_lon',
        ExpressionAttributeValues={
            ':started': item.get("started"),
            ':src': item.get("src"),
            ':src_lat': item.get("src_lat"),
            ':src_lon': item.get("src_lon"),
            ':ts': "STARTED"
        }
    )
    return response


def db_end_trip(item):
    table_name = "trip"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    item = json.loads(json.dumps(item), parse_float=Decimal)
    response = table.update_item(
        Key={
            'id': str(item.get("id"))
        },
        UpdateExpression='SET trip_status = :ts, arrived = :arrived, trip_feedback = :trip_feedback',
        ExpressionAttributeValues={
            ':arrived': item.get("arrived"),
            ':trip_feedback': item.get("trip_feedback"),
            ':ts': "COMPLETED"
        }
    )
    return response


def db_view_upcoming_trips(item):
    # Get the params
    user_id = request.get_json().get("user_id")
    src = request.get_json().get("src")
    src_lat = request.get_json().get("src_lat")
    src_lon = request.get_json().get("src_lon")
    interval = request.get_json().get("interval")
    # Connection and resources
    table_name = "user_route_preference"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    # Define time now and after the interval
    from_time = datetime.now()
    to_time = from_time + timedelta(days=interval)
    from_time = from_time.strftime("%m-%d-%Y %H:%M:%S")
    to_time = to_time.strftime("%m-%d-%Y %H:%M:%S")

    # See if there are trips already generated then return, otherwise generate trips
    """print(from_time, to_time)
    fe = Attr('user_id').eq(str(user_id)) & Attr('arrived').eq(None) & Attr('scheduled_arrival').lte(to_time)
    # Scan table with filters
    trip_table = dynamodb.Table("trip")
    response = trip_table.scan(
        FilterExpression=fe
    )
    if len(response['Items']) != 0:
        return response """

    # Generate trips first then show
    # Get today's day name
    curr_date = datetime.today()
    day_name = calendar.day_name[curr_date.weekday()]
    print(day_name)

    # Modifying code to generate all trips "interval" hours ahead and putting them into trips table
    # First scan the full table with the user_id
    fe = Key('user_id').eq(str(user_id))
    pe = "user_id, days_of_week, medium, dst"
    # Scan table with filters
    pref_response = table.scan(
        FilterExpression=fe,
        ProjectionExpression=pe
        # ,ExpressionAttributeNames={'#time_of_day': 'days_of_week.'+day_name}
    )
    rows = pref_response['Items']

    dt = date_start = datetime.now().date()
    date_end = date_start + timedelta(days=interval)
    while dt < date_end:
        day_name = calendar.day_name[dt.weekday()]
        for row in rows:
            dst = row['dst']
            medium = row['medium']
            user_id = row['user_id']
            schedule = row['days_of_week']
            times = ''
            times = schedule.get(day_name)
            # print(dt, day_name, times)
            # Call the add trip method with all the info
            data = {}
            res = db_get_place({"id": src})
            #print(res)
            res_src = json.loads(res).get("Item")
            res = db_get_place({"id": dst})
            #print(res)
            res_dst = json.loads(res).get("Item")
            data['src'] = res_src
            data['src_lat'] = src_lat
            data['src_lon'] = src_lon
            data['dst'] = res_dst
            data['medium'] = medium
            data['user_id'] = user_id
            data['trip_status'] = "NOT_STARTED"
            if times is not None:
                for t in times:
                    tm = datetime.strptime(t, "%H:%M:%S").time()
                    dtc = datetime.combine(dt, tm)
                    dtc = dtc.strftime("%m-%d-%Y %H:%M:%S")
                    data['scheduled_arrival'] = dtc
                    json_data = json.dumps(data)

                    # Temporary modification: If trip not found in table create it
                    fe = Attr('user_id').eq(str(user_id)) & Attr('scheduled_arrival').eq(dtc) & Attr('dst').eq(res_dst)
                    trip_table = dynamodb.Table("trip")
                    result = trip_table.scan(
                        FilterExpression=fe
                    )
                    if len(result['Items']) == 0:
                        db_add_trip(data)
        dt = dt + timedelta(days=1)

    # Show the trips generated in the last block
    fe = Attr('user_id').eq(str(user_id)) & Attr('arrived').eq(None) & Attr('scheduled_arrival').lte(to_time)
    # Scan table with filters
    trip_table = dynamodb.Table("trip")
    response = trip_table.scan(
        FilterExpression=fe
    )
    # Add the "Go in" time here
    items = response["Items"]
    for item in items:
        dist = gmaps.distance_matrix(item.get('src').get('address'), item.get('dst').get('address'), "driving")
        go_in_str = dist.get('rows')[0].get('elements')[0].get('duration').get('text')
        item['duration'] = go_in_str
    response["Items"] = items

    return response


def db_view_trip_history(uid):
    """
    :param uid: user id
    :return: List of trips taken so far (complete and incomplete)
    """
    table_name = "trip"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    # Define time now and after the interval
    time_now_dt = datetime.now()
    time_now = time_now_dt.strftime("%m-%d-%Y %H:%M:%S")

    # Add filter expression and projection expression
    print("time now = ", time_now)
    fe = Attr('user_id').eq(str(uid)) & Attr('arrived').lte(time_now)
    pe = "id, user_id, src, dst, started, arrived, scheduled_arrival, route, suggested_routes, " \
         "trip_feedback, trip_status"
    # Scan table with filters
    response = table.scan(
        FilterExpression=fe,
        ProjectionExpression=pe
    )
    items = response["Items"]
    for item in items:
        if item.get("trip_status") == "NOT_STARTED" \
                and item.get("scheduled_arrival") > (time_now_dt-timedelta(hours=24)).strftime("%m-%d-%Y %H:%M:%S"):
            item['editable'] = "True"
        else:
            item['editable'] = "False"
    response["Items"] = items

    return response


def db_get_routes(item):
    src = item.get("src")
    dst = item.get("dst")
    mode = item.get("mode")
    response = ""
    response = gmaps.directions(src, dst, mode="transit", departure_time=now)
    items = response['Items']
    return response


def db_get_places(item):
    table_name = "place"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    # query
    """response = table.query(
        KeyConditionExpression=Key('user_id').eq(user_id)
    )   """
    # Define filters and projections
    fe = Attr('user_id').eq(item.get("user_id"))
    pe = "id, user_id, place_name, address, lat, lon, tags"
    # Scan table with filters
    response = table.scan(
        FilterExpression=fe,
        ProjectionExpression=pe
    )
    # items = response['Items']
    return response


if __name__ == "__main__":
    app.run(host='localhost', port=5001, debug=True)
    # app.run(host='0.0.0.0', port=80)
    print('Server running with flask')
