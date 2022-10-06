from flask import Flask, request, jsonify
import boto3
import json
from decimal import Decimal
from datetime import datetime, timedelta
import calendar
import time
import pytz
import googlemaps
from boto3.dynamodb.conditions import Key, Attr

import functions

application = app = Flask(__name__)

# gmaps = googlemaps.Client(key="AIzaSyBoBDraxeL4lK2Ds0fwqNRm-acp6_b1PzY")

# Geocoding an address and Look up an address with reverse geocoding
# geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')
# gmaps.reverse_geocode((40.714224, -73.961452))

now = datetime.now(pytz.timezone('US/Mountain'))
print("Mountain time now : ", now)

@app.route('/')
def index():
    print("Transportation app server")
    return "Hello World!"


@app.route('/user/settings/get', methods=['POST'])
def get_settings():
    res = db_get_settings(request.get_json())
    return res


@app.route('/user/settings/add', methods=['POST'])
def add_settings():
    # Get list of places by user_id
    res = db_add_settings(request.get_json())
    return res


@app.route('/user/token/add', methods=['POST'])
def add_user_token():
    # Get list of places by user_id
    res = db_add_user_token(request.get_json())
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
    res = db_get_upcoming_trips(request.get_json())
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
    res = db_get_emojis()
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
            'alert_time_bool': item.get("alert_time_bool"),
            'trip_duration': item.get("trip_duration"),
            'air_pollution': item.get("air_pollution"),
            'road_closure': item.get("road_closure"),
            'setup': item.get("setup"),
            'isLastTripRated': item.get("isLastTripRated"),
            'deleteRequest': item.get("deleteRequest")
        }
    )
    return response


def db_add_user_token(item):
    # Adding device token for each user
    table_name = "user_tokens"
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    # Generate an id
    new_id = round(time.time() * 1000)
    response = table.put_item(
        Item={
            'id': str(new_id),
            'user_id': str(item.get("user_id")),
            'token': item.get("token"),
        }
    )
    response['id'] = new_id
    return response


def db_add_place(item):
    table_name = "place"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    item = json.loads(json.dumps(item), parse_float=Decimal)

    # Duplicate location check for same user. Scan and filter with user_id and place_name
    fe = Attr('user_id').eq(str(item.get("user_id"))) & Attr('lat').eq(item.get("lat")) \
         & Attr('lon').eq(item.get("lon"))
    dup_response = table.scan(
        FilterExpression=fe
    )
    print(dup_response)
    c = dup_response['Count']
    new_id = None
    if c == 1:
        # Duplicate Entry
        new_id = str(dup_response['Items'][0]['id'])
        print("Duplicate id = ", new_id)
    else:
        new_id = item.get('id')
        print("Updating id = ", new_id)

    # If new, Timestamp in milliseconds to use as generated id, otherwise use provided id for update
    if new_id == "" or new_id is None:
        new_id = round(time.time() * 1000)

    response = table.put_item(
        Item={
            'id': str(new_id),
            'user_id': str(item.get("user_id")),
            'place_name': item.get("name"),
            'address': item.get("address"),
            'lat': item.get("lat"),
            'lon': item.get("lon"),
            'tags': item.get("tags"),
            'emoji': item.get("emoji")
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
    print(item.get("id"))
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
    #item = json.loads(json.dumps(item))
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
            'dst_id': item.get("dst_id"),
            'medium': item.get("medium"),
            'started': item.get("started"),
            'arrived': item.get("arrived"),
            'scheduled_arrival': item.get("scheduled_arrival"),
            'suggested_start_time': item.get("suggested_start_time"),
            'estimated_duration': item.get("estimated_duration"),
            'trip_status': item.get("trip_status"),
            'is_deleted': item.get("is_deleted"),
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
    place_id = str(item.get("id"))
    table_name = "place"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    response = table.delete_item(
        Key={
            'id': str(item.get("id"))
        }
    )

    # Delete related route-preferences too
    pref_table = dynamodb.Table("user_route_preference")
    pref_resp = pref_table.delete_item(
        Key={
            'dst': str(item.get("id"))
        }
    )

    # Soft delete related trips too
    del_resp = db_soft_delete_trip(place_id)
    print(del_resp)

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


def db_soft_delete_trip(place_id):
    table_name = "trip"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    fe = Attr('dst_id').eq(str(place_id))
    pe = "id"
    response = table.scan(
        FilterExpression=fe,
        ProjectionExpression=pe
    )
    rows = response['Items']

    print("Rows to be deleted: ", rows)
    # Run a series of updates
    for row in rows:
        trip_id = row.get("id")
        update_response = table.update_item(
            Key={
                'id': trip_id
            },
            UpdateExpression='SET is_deleted = :isDeleted',
            ExpressionAttributeValues={
                ':isDeleted': True
            }
        )
    return "Trips deleted"


def db_view_next_trip(item):
    # Connection and resources
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")

    # Get the params
    user_id = request.get_json().get("user_id")
    from_time = now
    from_time = from_time.strftime("%m-%d-%Y %H:%M:%S")

    # Generate the next trip only, the second argument is True when it's only next trip, False otherwise
    db_get_upcoming_trips(item)
    # Scan trip table
    fe = Attr('user_id').eq(str(user_id)) & Attr('scheduled_arrival').gte(from_time) & Attr('is_deleted').eq(False) \
         & (Attr('trip_status').eq("NOT_STARTED") | Attr('trip_status').eq("STARTED"))
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
    """fe = Attr('user_id').eq(str(item.get("user_id"))) & (Attr('trip_status').eq("STARTED"))
    resp = table.scan(
        FilterExpression=fe
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
        UpdateExpression='SET trip_status = :ts, arrived = :arrived, dst_lat = :dst_lat, dst_lon = :dst_lon, trip_feedback = :trip_feedback',
        ExpressionAttributeValues={
            ':arrived': item.get("arrived"),
            ':trip_feedback': item.get("trip_feedback"),
            ':dst_lat': item.get("dst_lat"),
            ':dst_lon': item.get("dst_lon"),
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


def db_get_upcoming_trips(item):
    # Get the params
    jsn = request.get_json()
    user_id = jsn.get("user_id")
    src = jsn.get("src")
    src_lat = jsn.get("src_lat")
    src_lon = jsn.get("src_lon")
    src_addr = jsn.get("src_addr")
    interval = jsn.get("interval")
    nextTrip, isBreak = False, False

    if interval == 0:
        interval = 8
        nextTrip = True

    # Connection and resources
    table_name = "user_route_preference"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    # Define time now and after the interval
    from_time = now
    to_time = from_time + timedelta(days=interval)
    from_time = from_time.strftime("%m-%d-%Y %H:%M:%S")
    to_time = to_time.strftime("%m-%d-%Y %H:%M:%S")

    # Generate trips first then show
    # Modifying code to generate all trips "interval" hours ahead and putting them into trips table
    # First scan the full table with the user_id
    fe = Key('user_id').eq(str(user_id))
    pe = "user_id, days_of_week, medium, dst"
    # Scan table with filters
    pref_response = table.scan(
        FilterExpression=fe,
        ProjectionExpression=pe
    )
    rows = pref_response['Items']

    dt = date_start = now.date()
    date_end = date_start + timedelta(days=interval)
    while dt <= date_end:
        day_name = calendar.day_name[dt.weekday()]
        for row in rows:
            dst = row['dst']
            medium = row['medium']
            user_id = row['user_id']
            schedule = row['days_of_week']
            times = ''
            times = schedule.get(day_name)
            # Call the add trip method with all the info

            data = {}
            res_src = src
            if src:
                res_src = db_get_place({"id": src})
                res_src = json.loads(res_src).get("Item")
            res_dst = db_get_place({"id": dst})
            res_dst = json.loads(res_dst).get("Item")

            data['src'] = res_src
            data['src_lat'] = src_lat
            data['src_lon'] = src_lon
            data['src_addr'] = src_addr
            data['dst_id'] = dst
            data['dst'] = res_dst
            data['medium'] = medium
            data['user_id'] = user_id
            data['trip_status'] = "NOT_STARTED"
            data['is_deleted'] = False
            # print(res_src, res_dst)
            if times is not None:
                for t in times:
                    tm = None
                    try:
                        tm = datetime.strptime(t, "%H:%M:%S").time()
                    except ValueError:
                        tm = datetime.strptime(t, "%H:%M").time()
                    dtcf = datetime.combine(dt, tm)
                    dtc = dtcf.strftime("%m-%d-%Y %H:%M:%S")
                    if dtc > now.strftime("%m-%d-%Y %H:%M:%S"):
                        data['scheduled_arrival'] = dtc
                        # Add Suggested_start_time, estimated_duration, on_time status, road_quality etc.
                        srcAddr, dstAddr = None, None
                        if res_src is not None and res_src.get('address') is not None:
                            srcAddr = res_src.get('address')
                        else:
                            srcAddr = src_addr
                        if res_dst is not None and res_dst.get('address') is not None:
                            dstAddr = res_dst.get('address')

                        preferred_arrival = datetime.strptime(dtc, '%m-%d-%Y %H:%M:%S')
                        # skip while API disabled
                        addTrip = False
                        if srcAddr and dstAddr and dtc > now.strftime("%m-%d-%Y %H:%M:%S"):
                            print("Preffered arrival = ", preferred_arrival)
                            res = functions.get_departure_time(srcAddr, dstAddr,
                                                               preferred_arrival)
                            data['suggested_start_time'] = res[0].strftime("%Y-%m-%d %H:%M:%S")
                            data['estimated_duration'] = res[1]
                            if data['suggested_start_time'] > now.strftime("%m-%d-%Y %H:%M:%S"):
                                addTrip = True
                            else:
                                addTrip = False

                        # Optimization needed: If trip not found in table create it
                        fe = Attr('user_id').eq(str(user_id)) & Attr('scheduled_arrival').eq(dtc) & Attr('dst_id').eq(
                            dst) & Attr('is_deleted').eq(False)
                        trip_table = dynamodb.Table("trip")
                        result = trip_table.scan(
                            FilterExpression=fe
                        )

                        # Add or update, get id from existing item
                        if result['Count'] > 0:
                            data['id'] = result['Items'][0].get('id')

                        # Dump to json and add/update
                        json_data = json.dumps(data)
                        if addTrip==True:
                            db_add_trip(data)

        dt = dt + timedelta(days=1)
    # Show the trips generated in the last block
    fe = Attr('user_id').eq(str(user_id)) & Attr('arrived').eq(None) & Attr('scheduled_arrival').gte(from_time) \
         & Attr('scheduled_arrival').lte(to_time) & Attr('is_deleted').eq(False)
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
    time_now_dt = now
    time_now = time_now_dt.strftime("%m-%d-%Y %H:%M:%S")

    # Add filter expression and projection expression
    fe = Attr('user_id').eq(str(uid)) & (
            Attr('scheduled_arrival').lte(time_now) | (Attr('trip_status').eq("COMPLETED")))
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
    # pe = "id, user_id, place_name, address, lat, lon, tags"
    # Scan table with filters
    response = table.scan(
        FilterExpression=fe
        # ,ProjectionExpression=pe
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
    """time_lower = now - timedelta(hours=12)
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
    print(src, dst, route_type)
    response = functions.calc_fastest_routes(src, dst, [], 0, route_type)
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
            'report_time': now.strftime("%m-%d-%Y %H:%M:%S")
        }
    )
    return response


def db_get_emojis():
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
    # app.run(host='0.0.0.0', port=8080)
    print('Server running with flask')
