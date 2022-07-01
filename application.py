from flask import Flask, request, jsonify
import boto3
import json
from decimal import Decimal
from datetime import datetime, timedelta
import calendar
import time
import googlemaps
from boto3.dynamodb.conditions import Key, Attr

import functions

application = app = Flask(__name__)

gmaps = googlemaps.Client(key="AIzaSyBoBDraxeL4lK2Ds0fwqNRm-acp6_b1PzY")

# Geocoding an address and Look up an address with reverse geocoding
# geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')
# gmaps.reverse_geocode((40.714224, -73.961452))

now = datetime.now()


@app.route('/')
def index():
    print("Transportation app server")
    return "Hello World!"


@app.route('/user/settings/get', methods=['POST'])
def get_settings():
    # Get list of places by user_id
    res = db_get_settings(request.get_json())
    return res


@app.route('/user/settings/add', methods=['POST'])
def add_settings():
    # Get list of places by user_id
    res = db_add_settings(request.get_json())
    return res


@app.route('/place/all', methods=['POST'])
def get_places():
    # Get list of places by user_id
    res = db_get_places(request.get_json())
    return res


@app.route('/place/get', methods=['POST'])
def get_place():
    res = db_get_place(request.get_json())
    return res


@app.route('/place/add', methods=['POST'])
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


@app.route('/trip/get', methods=['POST'])
def get_trip():
    res = db_get_trip(request.get_json())
    return res


@app.route('/trip/add', methods=['POST'])
def add_trip():
    res = db_add_trip(request.get_json())
    return res


@app.route('/trip/remove', methods=['POST'])
def remove_trip():
    res = db_delete_trip(request.get_json())
    return res


@app.route('/trip/next', methods=['POST'])
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


@app.route('/trip/feedback', methods=['POST'])
def add_trip_feedback():
    # End this trip
    res = db_add_feedback(request.get_json())
    return res


@app.route('/trip/upcoming', methods=['POST'])
def view_upcoming_trips():
    # Get all the trips within certain days, that are planned in the preference table
    res = db_view_upcoming_trips(request.get_json())
    return res


@app.route('/trip/history', methods=['POST'])
def view_trip_history():
    user_id = request.get_json().get("user_id")
    res = db_view_trip_history(user_id)
    return res


@app.route('/addRoutePreference', methods=['POST'])
def add_route_pref():
    res = db_add_route_pref(request.get_json())
    return res


@app.route('/getRoutePreference', methods=['POST'])
def get_route_pref():
    res = db_get_route_pref(request.get_json())
    return res


# Get the fastest and safest routes
@app.route('/routes', methods=['POST'])
def get_routes():
    res = db_get_routes(request.get_json())
    return res


# Get the fastest and safest routes
@app.route('/report', methods=['POST'])
def add_report():
    res = db_add_report(request.get_json())
    return res


@app.route('/emojis/get', methods=['POST'])
def get_emojis():
    # Get list of places by user_id
    res = db_get_emojis(request.get_json())
    return res


def db_get_settings(item):
    table_name = "user_settings"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    # Get the item with the key
    response = table.get_item(
        Key={
            'user_id': str(item.get("user_id"))
        }
    )
    response = json.dumps(response, default=default_json)
    return response


def db_add_settings(item):
    table_name = "user_settings"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    response = table.put_item(
        Item={
            'user_id': str(item.get("user_id")),
            'name': item.get("name"),
            'phone': item.get("phone"),
            'alert_time': item.get("alert_time"),
            'medium': item.get("medium"),
            'preferred_route': item.get("preferred_route"),


        }
    )
    return response


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
            'user_id': str(item.get("user_id")),
            'place_name': item.get("name"),
            'address': item.get("address"),
            'lat': item.get("lat"),
            'lon': item.get("lon"),
            'tags': item.get("tags")
        }
    )
    response['id'] = new_id
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
        UpdateExpression='SET place_name = :new_name, tags = :tags',
        ExpressionAttributeValues={
            ':new_name': item.get("name"),
            ':tags': item.get("tags")
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
            'src_addr': item.get("src_addr"),
            'dst': item.get("dst"),
            'medium': item.get("medium"),
            'started': item.get("started"),
            'arrived': item.get("arrived"),
            'scheduled_arrival': item.get("scheduled_arrival"),
            'suggested_start_time': item.get("suggested_start_time"),
            'estimated_duration': item.get("estimated_duration"),
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
            'user_id': str(item.get("user_id")),
            'dst': str(item.get("dst")),
            'medium': item.get("medium"),
            'days_of_week': item.get("days_of_week")
        }
    )
    return response


def db_get_route_pref(item):
    table_name = "user_route_preference"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)
    fe = Attr('user_id').eq(str(item.get("user_id"))) & Attr('dst').eq(str(item.get("dst")))
    response = table.scan(
        FilterExpression=fe
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
    response = table.delete_item(
        Item={
            'id': item.get("id")
        }
    )
    return response


def db_view_next_trip(item):
    # Connection and resources
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")

    # Get the params
    user_id = request.get_json().get("user_id")
    from_time = datetime.now()
    from_time = from_time.strftime("%m-%d-%Y %H:%M:%S")

    # Scan trip table
    fe = Attr('user_id').eq(str(user_id)) & Attr('scheduled_arrival').gte(from_time) \
         & Attr('trip_status').eq("NOT_STARTED")
    # Scan table with filters
    trip_table = dynamodb.Table("trip")
    response = trip_table.scan(
        FilterExpression=fe
    )

    # Find the trip with the lowest scheduled time
    if not response["Items"]:
        response["Count"] = 0
        response["Item"] = None
    else:
        lowest = response["Items"][0].get("scheduled_arrival")
        lowest_row = response["Items"][0]
        for row in response["Items"]:
            if row.get("scheduled_arrival") < lowest:
                lowest = row.get("scheduled_arrival")
                lowest_row = row
        response["Item"] = lowest_row
        response["Count"] = 1

    del response["Items"]
    return response


def db_start_trip(item):
    table_name = "trip"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    item = json.loads(json.dumps(item), parse_float=Decimal)

    # If trip id not present, return with error
    """ resp = table.get_item(
        Key={
            'id': str(item.get("id"))
        }
    ) """

    response = table.update_item(
        Key={
            'id': str(item.get("id"))
        },
        UpdateExpression='SET trip_status = :ts, started = :started, '
                         'src = :src, src_lat = :src_lat, src_lon = :src_lon, src_addr = :src_addr',
        ExpressionAttributeValues={
            ':started': item.get("started"),
            ':src': item.get("src"),
            ':src_lat': item.get("src_lat"),
            ':src_lon': item.get("src_lon"),
            ':src_addr': item.get("src_addr"),
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


def db_add_feedback(item):
    table_name = "trip"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    response = table.update_item(
        Key={
            'id': str(item.get("id"))
        },
        UpdateExpression='SET trip_feedback = :feedback',
        ExpressionAttributeValues={
            ':feedback': item.get("trip_feedback")
        }
    )
    return response


def db_view_upcoming_trips(item):
    # Get the params
    user_id = request.get_json().get("user_id")
    src = request.get_json().get("src")
    src_lat = request.get_json().get("src_lat")
    src_lon = request.get_json().get("src_lon")
    src_addr = request.get_json().get("src_addr")
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
            res_src = src
            if src:
                res = db_get_place({"id": src})
                res_src = json.loads(res).get("Item")
            res = db_get_place({"id": dst})
            res_dst = json.loads(res).get("Item")
            data['src'] = res_src
            data['src_lat'] = src_lat
            data['src_lon'] = src_lon
            data['src_addr'] = src_addr
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
                    # Add Suggested_start_time, estimated_duration, on_time status, road_quality etc.
                    srcAddr, dstAddr = None, None
                    if src is not None and res_src.get('address') is not None:
                        srcAddr = res_src.get('address')
                    else:
                        srcAddr = src_addr
                    if dst is not None and res_dst.get('address') is not None:
                        dstAddr = res_dst.get('address')

                    preferred_arrival = datetime.strptime(dtc, '%m-%d-%Y %H:%M:%S')
                    res = functions.get_departure_time(srcAddr, dstAddr,
                                                       preferred_arrival)
                    data['suggested_start_time'] = res[0].strftime("%Y-%m-%d %H:%M:%S")
                    data['estimated_duration'] = res[1]
                    json_data = json.dumps(data)
                    # Optimization needed: If trip not found in table create it
                    fe = Attr('user_id').eq(str(user_id)) & Attr('scheduled_arrival').eq(dtc) & Attr('dst').eq(res_dst)
                    trip_table = dynamodb.Table("trip")
                    result = trip_table.scan(
                        FilterExpression=fe
                    )
                    if len(result['Items']) == 0:
                        db_add_trip(data)
        dt = dt + timedelta(days=1)

    # Show the trips generated in the last block
    fe = Attr('user_id').eq(str(user_id)) & Attr('arrived').eq(None) & Attr('scheduled_arrival').gte(from_time) \
         & Attr('scheduled_arrival').lte(to_time)
    # Scan table with filters
    trip_table = dynamodb.Table("trip")
    response = trip_table.scan(
        FilterExpression=fe
    )

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
    fe = Attr('user_id').eq(str(uid)) & Attr('scheduled_arrival').lte(time_now)
    pe = "id, user_id, src, dst, started, arrived, scheduled_arrival, route, suggested_routes, " \
         "trip_feedback, trip_status"
    # Scan table with filters
    response = table.scan(
        FilterExpression=fe
        # ,ProjectionExpression=pe
    )
    items = response["Items"]
    for item in items:
        if item.get("trip_status") == "NOT_STARTED":
            item['missed'] = "True"
        else:
            item['missed'] = "False"

        if item.get("trip_status") == "NOT_STARTED" \
                and item.get("scheduled_arrival") > (time_now_dt - timedelta(hours=24)).strftime("%m-%d-%Y %H:%M:%S"):
            item['editable'] = "True"
        else:
            item['editable'] = "False"
    response["Items"] = items

    return response


def db_get_places(item):
    table_name = "place"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1", )
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    # Define filters and projections
    fe = Attr('user_id').eq(str(item.get("user_id")))
    pe = "id, user_id, place_name, address, lat, lon, tags"
    # Scan table with filters
    response = table.scan(
        FilterExpression=fe,
        ProjectionExpression=pe
    )

    # Append preferences for each destination place
    for row in response["Items"]:
        pref_table = dynamodb.Table("user_route_preference")
        fe_pref = Attr('user_id').eq(row.get("user_id")) & Attr('dst').eq(row.get("id"))
        pref_res = pref_table.scan(
            FilterExpression=fe_pref
        )
        row['route_preference'] = pref_res["Items"]
    return response


def db_get_routes(item):
    print("Showing routes")
    table_name = "trip_report"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1", )
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    # Get params
    src = item.get("src")
    dst = item.get("dst")
    route_type = item.get("route_type")
    medium = item.get("medium")

    # Get the eligible reported points from report table by time and location
    """time_lower = datetime.now() - timedelta(hours=12)
    time_lower = time_lower.strftime("%m-%d-%Y %H:%M:%S")
    fe = Attr('issue').eq("ROAD_CLOSURE") & Attr('report_time').gte(time_lower)
    pe = "lat, lon"
    report_res = table.scan(
        FilterExpression=fe,
        ProjectionExpression=pe
    )
    items = report_res["Items"]
    point_list = []
    for row in items:
        point = (str(row.get("lat")), str(row.get("lat")))
        point_list.append(point)
    print("Checkpoints = ", point_list) """
    response = functions.calc_fastest_routes(src, dst, [], 100, route_type)
    return response


def db_add_report(item):
    table_name = "trip_report"
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
            'issue': item.get("issue"),
            'description': item.get("description"),
            'lat': item.get("lat"),
            'lon': item.get("lon"),
            'report_time': datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        }
    )
    return response


def db_get_emojis(item):
    table_name = "emoji"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    # Get the item with the key
    response = table.scan(
    )
    return response


if __name__ == "__main__":
    app.run(host='localhost', port=5001, debug=True)
    # app.run(host='0.0.0.0', port=80)
    print('Server running with flask')
