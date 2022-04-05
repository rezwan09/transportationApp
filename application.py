from flask import Flask, request, jsonify
import boto3
from boto3.dynamodb.conditions import Key

application = app = Flask(__name__)


@app.route('/')
def index():
    print("Got request in server")
    return "Hello World!"


@app.route('/getPlaces', methods=['POST'])
def get_places():
    # Get list of places by user_id or name
    user_id = request.form.get('user_id')
    name = request.form.get('name')
    print("user id =", user_id, "name = ", name)
    # Get list from dynamoDB and return
    res = db_get_places(user_id, name)
    return res


@app.route('/addPlace', methods=['POST'])
def add_place():
    user_id_str = request.get_json().get("user_id")
    user_id = int(user_id_str)
    name = request.get_json().get("name")
    lat = request.get_json().get("lat")
    lon = request.get_json().get("lon")
    tags = request.get_json().get("tags")
    print(user_id, name, lat, lon, tags)
    res = db_add_place(user_id, name, lat, lon, tags)
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


@app.route('/removePlace', methods=['POST'])
def remove_place():
    user_id_str = request.get_json().get("user_id")
    user_id = int(user_id_str)
    pid = request.get_json().get("pid")
    print(user_id, pid)
    res = db_delete_place(pid)
    return res


@app.route('/removeTrip', methods=['POST'])
def remove_trip():
    uid = request.get_json().get("uid")
    tripid = request.get_json().get("tripid")
    print(uid, tripid)
    res = db_delete_trip(uid, tripid)
    return res


def db_add_place(user_id, name, lat, lon, tags):
    table_name = "places"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    response = table.put_item(
        Item={
            'user_id': user_id,
            'name': name,
            'lat': lat,
            'lon': lon
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


def db_delete_place(pid):
    table_name = "places"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    response = table.delete_item(
        Item={
            'pid': pid
        }
    )
    print(response)
    return str(response)


def db_delete_trip(uid, tripid):
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


def db_get_places(user_id, name):
    table_name = "places"
    dynamodb_client = boto3.client('dynamodb', region_name="us-east-1")
    dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
    table = dynamodb.Table(table_name)

    #response = table.scan()
    response = table.query(
        KeyConditionExpression=Key('user_id').eq(user_id)
    )

    items = response['Items']
    print(items)
    return str(items)


if __name__ == "__main__":
    app.run(host='localhost', port=5001, debug=True)
    print('Server running with flask')
