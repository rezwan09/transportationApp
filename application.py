from flask import Flask, request, jsonify
import boto3
import json
from decimal import Decimal
from datetime import datetime
import calendar
from boto3.dynamodb.conditions import Key, Attr

application = app = Flask(__name__)


@app.route('/')
def index():
    print("Got request in server")
    return "Hello World!"


@app.route('/getPlaces', methods=['POST'])
def get_places():
    # Get list of places by user_id or name
    user_id = request.get_json().get("user_id")
    user_id = int(user_id)
    print("user id =", user_id)
    # Get list from dynamoDB and return
    res = db_get_places(user_id)
    return res


@app.route('/addPlace', methods=['POST'])
def add_place():
    res = db_add_place(request.get_json())
    return res


@app.route('/updatePlace', methods=['POST'])
def update_place():
    res = db_update_place(request.get_json())
    return res


@app.route('/removePlace', methods=['POST'])
def remove_place():
    user_id = str(request.get_json().get("user_id"))
    name = request.get_json().get("name")
    print(user_id, name)
    res = db_delete_place(user_id+name)
    return res


@app.route('/addTrip', methods=['POST'])
def add_trip():
    uid = request.get_json().get("uid")
    trip_id = request.get_json().get("tripid")
    src = request.get_json().get("src")
    dst = request.get_json().get("dst")
    started = request.get_json().get("started")
    arrived = request.get_json().get("arrived")
    route = request.get_json().get("route")
    suggested_routes = request.get_json().get("suggestedRoutes")
    trip_feedback = request.get_json().get("tripFeedback")
    print(uid, trip_id, src, dst, started, arrived, route, suggested_routes, trip_feedback)
    res = db_add_trip(uid, trip_id, src, dst, started, arrived, route, suggested_routes, trip_feedback)
    return res


@app.route('/viewNextTrip', methods=['POST'])
def view_next_trip():
    # Get next trip that's planned in the preference table
    user_id = request.get_json().get("user_id")
    res = db_view_next_trip(user_id)
    return res


@app.route('/viewFutureTrips', methods=['POST'])
def view_future_rips():
    uid = request.get_json().get("uid")
    # Get next trip that's planned in the preference table


@app.route('/viewTripHistory', methods=['POST'])
def view_trip_history():
    uid = request.get_json().get("uid")
    # Get next trip that's planned in the preference table


@app.route('/addRoutePreference', methods=['POST'])
def add_route_pref():
    user_id = request.get_json().get("user_id")
    destination_id = request.get_json().get("destination_id")
    medium = request.get_json().get("medium")
    days_of_week = request.get_json().get("days_of_week")
    print(user_id, destination_id, medium,days_of_week)
    res = db_add_route_pref(user_id, destination_id, medium, days_of_week)
    return res


@app.route('/removeTrip', methods=['POST'])
def remove_trip():
    uid = request.get_json().get("uid")
    tripid = request.get_json().get("tripid")
    print(uid, tripid)
    res = db_delete_trip(uid, tripid)
    return res


# DB call implementations---


def db_add_place(item):
    table_name = "place"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    item = json.loads(json.dumps(item), parse_float=Decimal)

    response = table.put_item(
        Item={
            'id': str(item.get("user_id"))+item.get("name"),
            'user_id': item.get("user_id"),
            'place_name': item.get("name"),
            'lat': item.get("lat"),
            'lon': item.get("lon")
        } 
    )
    print(response)
    return str(response)


def db_update_place(item):
    table_name = "place"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    item = json.loads(json.dumps(item), parse_float=Decimal)

    response = table.update_item(
        Key={
            'id': str(item.get("user_id")) + item.get("name")
        },
        UpdateExpression='SET place_name = :val',
        ExpressionAttributeValues={
            ':val': item.get("name")
        }
    )
    print(response)
    return str(response)


def db_add_trip(uid, trip_id, src, dst, started, arrived, route, suggested_routes, trip_feedback):
    table_name = "trip"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)
    print("Trip id is == ", trip_id)
    response = table.put_item(
        Item={
            'uid': uid,
            'tripid': trip_id,
            'src': src,
            'dst': dst,
            'started': arrived,
            'started': started,
            'route': route,
            'suggestedRoutes': suggested_routes,
            'tripFeeback': trip_feedback
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


def db_delete_place(key):
    table_name = "place"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    response = table.delete_item(
        Key={
            'id': key
        }
    )
    print(response)
    return str(response)


def db_delete_trip(uid, tripid):
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
            'uid': uid
        }
    )
    print(response)
    return str(response)


def db_view_next_trip(uid):
    """
    :param uid: user id
    :return: List of trips scheduled for today
    """
    table_name = "user_route_preference"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    # Define filters and projections
    now = datetime.now()
    date_time_now = now.strftime("%m-%d-%Y %H:%M:%S")
    curr_date = datetime.today()
    day_name = calendar.day_name[curr_date.weekday()]
    print(day_name)
    fe = Key('user_id').eq(uid) and Attr('days_of_week.'+day_name).gte(date_time_now)
    pe = "user_id, days_of_week, medium, dst"
    # Scan table with filters
    response = table.scan(
        FilterExpression=fe,
        ProjectionExpression=pe
    )

    items = response['Items']
    print("items = ", items)
    return str(items)


def db_get_places(user_id):
    table_name = "place"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    # query
    """response = table.query(
        KeyConditionExpression=Key('user_id').eq(user_id)
    )   """
    # Define filters and projections
    fe = Attr('user_id').eq(user_id)
    pe = "user_id, place_name, lat, lon, tags"
    # Scan table with filters
    response = table.scan(
        FilterExpression=fe,
        ProjectionExpression=pe
    )
    items = response['Items']
    print(items)
    return str(items)


if __name__ == "__main__":
    #app.run(host='localhost', port=5001, debug=True)
    app.run(host='0.0.0.0', port=80)
    print('Server running with flask')
