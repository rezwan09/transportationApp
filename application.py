from flask import Flask, request, jsonify
import boto3
import json
from decimal import Decimal
from datetime import datetime, timedelta
import calendar
import time
import googlemaps
from boto3.dynamodb.conditions import Key, Attr

application = TransportationApp = Flask(__name__)

gmaps = googlemaps.Client(key="AIzaSyBS6SMCbOMepaibpG71IjXDulkVlOLM8p8")

# Geocoding an address
#geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')

# Look up an address with reverse geocoding
#reverse_geocode_result = gmaps.reverse_geocode((40.714224, -73.961452))
#print("Geocode === ", geocode_result)
# Request directions via public transit
now = datetime.now()
"""directions_result = gmaps.directions("Sydney Town Hall",
                                     "Parramatta, NSW",
                                     mode="transit",
                                     departure_time=now) """


@TransportationApp.route('/')
def index():
    print("Got request in server")
    return "Hello World!"


@TransportationApp.route('/place/all', methods=['GET'])
def get_places():
    # Get list of places by user_id
    res = db_get_places(request.get_json())
    return res


@TransportationApp.route('/place', methods=['GET'])
def get_place():
    res = db_get_place(request.get_json())
    return res


@TransportationApp.route('/place', methods=['POST'])
def add_place():
    """ This will do insert or update"""
    res = db_add_place(request.get_json())
    return res


@TransportationApp.route('/updatePlace', methods=['POST'])
def update_place():
    """ Not needed currently"""
    res = db_update_place(request.get_json())
    return res


@TransportationApp.route('/place/remove', methods=['POST'])
def remove_place():
    res = db_delete_place(request.get_json())
    return res


@TransportationApp.route('/trip', methods=['GET'])
def get_trip():
    res = db_get_trip(request.get_json())
    return res


@TransportationApp.route('/trip', methods=['POST'])
def add_trip():
    res = db_add_trip(request.get_json())
    return res


@TransportationApp.route('/trip/remove', methods=['POST'])
def remove_trip():
    res = db_delete_trip(request.get_json())
    return res


@TransportationApp.route('/trips/upcoming', methods=['GET'])
def view_upcoming_trips():
    # Get next trip that's planned in the preference table
    user_id = request.get_json().get("user_id")
    interval = request.get_json().get("interval")
    res = db_view_upcoming_trips(user_id, interval)
    return res


@TransportationApp.route('/trips/history', methods=['GET'])
def view_trip_history():
    user_id = request.get_json().get("user_id")
    res = db_view_trip_history(user_id)
    return res


@TransportationApp.route('/addRoutePreference', methods=['POST'])
def add_route_pref():
    user_id = request.get_json().get("user_id")
    destination_id = request.get_json().get("destination_id")
    medium = request.get_json().get("medium")
    days_of_week = request.get_json().get("days_of_week")
    print(user_id, destination_id, medium, days_of_week)
    res = db_add_route_pref(user_id, destination_id, medium, days_of_week)
    return res


# Get the fastest and safest routes
@TransportationApp.route('/routes', methods=['POST'])
def get_routes():
    res = db_get_routes(request.get_json())
    return res



# DB call implementations---


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
    return str(response)


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
    items = response['Items']
    print(items)
    return str(items)


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
    print(response)
    return str(response)


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
    items = response['Items']
    print(items)
    return str(items)


def db_add_trip(item):
    table_name = "trip"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    # Timestamp in milliseconds to use as generated id, otherwise use provided id for update
    new_id = item.get('id')
    if item.get('id') == "" or item.get('id') is None:
        new_id = round(time.time() * 1000)
    response = table.put_item(
        Item={
            'id': str(new_id),
            'user_id': str(item.get("user_id")),
            'src': item.get("src"),
            'dst': item.get("dst"),
            'started': item.get("started"),
            'arrived': item.get("arrived"),
            'route': item.get("route"),
            'suggested_routes': item.get("suggested_routes"),
            'trip_feedback': item.get("trip_feedback")
        }
    )
    print(response)
    return str(response)


def db_add_route_pref(user_id, destination_id, medium, days_of_week):
    table_name = "user_route_preference"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)
    print("User id is == ", user_id)
    response = table.put_item(
        Item={
            'user_id': user_id,
            'dst': destination_id,
            'medium': medium,
            'days_of_week': days_of_week
        }
    )
    print(response)
    return str(response)


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
    print(response)
    return str(response)


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
    print(response)
    return str(response)


def db_view_upcoming_trips(uid, interval):
    """
    :param interval: Hours from now
    :param uid: user id
    :return: List of trips scheduled for today
    """
    table_name = "user_route_preference"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    # Define time now and after the interval
    from_time = datetime.now()
    to_time = from_time + timedelta(hours=interval)
    from_time = from_time.strftime("%m-%d-%Y %H:%M:%S")
    to_time = to_time.strftime("%m-%d-%Y %H:%M:%S")
    # Get today's day name
    curr_date = datetime.today()
    day_name = calendar.day_name[curr_date.weekday()]
    print(day_name)
    fe = Key('user_id').eq(uid) and Attr('days_of_week.' + day_name).gte(from_time) and Attr('days_of_week.' + day_name).lte(to_time)
    pe = "user_id, days_of_week, medium, dst"
    # Scan table with filters
    response = table.scan(
        FilterExpression=fe,
        ProjectionExpression=pe
    )

    items = response['Items']
    print("items = ", items)
    return str(items)


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
    time_now = datetime.now()
    time_now = time_now.strftime("%m-%d-%Y %H:%M:%S")

    # Add filter expression and projection expression
    print("time now = ", time_now)
    fe = Key('user_id').eq(str(uid)) and Attr('started').lte(time_now)
    pe = "id, user_id, src, dst, started, arrived, route, suggested_routes, trip_feedback"
    # Scan table with filters
    response = table.scan(
        FilterExpression=fe,
        ProjectionExpression=pe
    )

    items = response['Items']
    print("items = ", items)
    return str(items)


def db_get_routes(item):
    src = item.get("src")
    dst = item.get("dst")
    mode = item.get("mode")
    response = ""
    response = gmaps.directions(src, dst, mode="transit", departure_time=now)
    items = response['Items']
    print("items = ", items)
    return str(items)


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
    items = response['Items']
    print(items)
    return str(items)


if __name__ == "__main__":
    TransportationApp.run(host='localhost', port=5001, debug=True)
    # app.run(host='0.0.0.0', port=80)
    print('Server running with flask')
