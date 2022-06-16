import requests
import numpy
from typing import List
import polyline
from math import sin, cos, sqrt, atan2, radians
import googlemaps
import datetime
import pandas as pd
import matplotlib.pyplot as plt

#client initiate gmaps client
api_key = ""
with open('google_maps_api.txt') as f:
        api_key = f.readlines()[0]
gmaps = googlemaps.Client(key=api_key)

"""This method returns a list of the fastest suggested routes.

    Args:
        A (String): Source location or name 
        B (String): Destination location or name 
        reported_points (list, optional): a list of reported road closure points. Defaults to [].
        n_search_points (int, optional): the number of waypoints you want google maps to search in. Defaults to 100.

    Returns:
        [Route]: a list of three Route object
    """    
    
def calc_fastest_routes(A,B,reported_points=[],n_search_points=100):

    #origin & first route
    try:
        routes = fetch_routes(A,B)
    except googlemaps.exceptions.ApiError as e:  # This is the correct syntax
        print("No route found from %s to %s" % A,B)
        return None
    
    # if no reported waypoints return first google alternative
    if len(reported_points) == 0:
        return routes
    
    #else look for ways to avoid 
    origin_x = routes[0].json_object['legs'][0]['start_location']['lng']
    origin_y = routes[0].json_object['legs'][0]['start_location']['lat']

    #waypoints
    wp_x,wp_y = get_searchable_waypoints(origin_x,origin_y) #src x & y
    
    all_routes_list = [] + routes
    valid_routes_list = [] + routes
    shortest_route = routes[0]
    print(shortest_route.duration)

    for i in range(0,n_search_points):
        waypoint = "%f,%f" % (wp_y[i],wp_x[i])
        try:
            #get the routes
            directions = gmaps.directions(A,B,waypoints=[waypoint])
            valid_routes_list += decode_json_routes(directions)
            all_routes_list += valid_routes_list
            
            #filter
            for p in reported_points:
                valid_routes_list = filter(lambda r: is_point_on_rout(p,r) == False,valid_routes_list)
            
            #set shortest
            valid_routes_list.sort(key=lambda r:r.duration)
            
            new_route = min([shortest_route,valid_routes_list[0]],key=lambda r:r.duration)
            if new_route.duration < shortest_route.duration:
                shortest_route = new_route
            
        except googlemaps.exceptions.ApiError as e:  
            continue

    #print
    return valid_routes_list[:3] #top 3

    #TODO: We still need to add the mode of transportation


"""Return the departure time to go from a source to destination by calculating it in traffic

    Args:
        A (String): Source location or name 
        B (String): Destination location or name
        preferred_arrival_time (date): the time that you want to reach

    Returns:
        (date,timedelta,int): returns a tuple containing the departure time, and the duration of the trip
    """
    
def get_departure_time(source,destination,preferred_arrival_time):
    
    #normal duration from a to b
    normal_duration = Route(gmaps.directions(source,destination, arrival_time=preferred_arrival_time)[0]).duration
    normal_departure_time = preferred_arrival_time - datetime.timedelta(seconds=normal_duration)
    
    #real duration
    real_duration = Route(gmaps.directions(source,destination,departure_time=normal_departure_time,traffic_model='pessimistic')[0]).duration
    real_departure_time = preferred_arrival_time - datetime.timedelta(seconds=real_duration)
    
    return (real_departure_time, real_duration)
    
    #TODO: We still need to provide the preferred route, add the mode of transportation



#################################################### HELPING METHODS ########################################################
#################################################### HELPING METHODS ########################################################
#################################################### HELPING METHODS ########################################################


class Route:
    
    def __init__(self,route_json):
        self.json_object = route_json
        self.duration = sum(map(lambda leg:leg['duration']['value'],route_json['legs']))
        
        #duration in traffic
        if "duration_in_traffic" in route_json['legs'][0]:
            self.duration_in_traffic = sum(map(lambda leg:leg['duration_in_traffic']['value'],route_json['legs']))
        
        #steps
        lst = list(map(lambda leg:leg['steps'],route_json['legs']))
        steps = []
        for a in lst:
            for aa in a:
                steps.append(aa)
        self.steps = steps
        
        #html steps
        self.html_steps = list(map(lambda step: step['html_instructions'] + "from: %s -> to:%s" % (step['start_location'],step['end_location']),self.steps))

        
        #points
        self.points = list(map(lambda step: (step['start_location']),self.steps))
        self.points.append(self.steps[-1]['end_location'])
        self.points = list(map(lambda p: (p['lat'],p['lng']),self.points))
        
        #polypoints
        pll_points = []
        for step in self.steps:
            pll = step['polyline']['points']
            pll_points = pll_points + polyline.decode(pll) 
    
        self.polypoints = pll_points
        
        #condenced points
        condenced_points = []
        for i in range(1,len(self.polypoints)):
            p1 = self.polypoints[i-1]
            p2 = self.polypoints[i]
            condenced_points += condense_points(p1,p2)
        self.condenced_points = condenced_points
        
        
## Functions

def breez_base_key():
    base = "https://api.breezometer.com/air-quality/v2/"
    api_key = "c6b0bd78b028449a8518d901751b680b"
    return (base,api_key)

def fetch_point_aq(lat,lon):
    (base,api_key) = breez_base_key()
    api = "current-conditions?lat=%f&lon=%f&features=pollutants_concentrations&key=%s" % (lat,lon,api_key)
    return requests.get(base+api).json()['data']

def average(lst):
    return sum(lst) / len(lst)

def gmaps_base_key():
    base = "https://maps.googleapis.com/maps/api/"
    api_key = api_key
    return (base,api_key)

def fetch_direction(A,B):
    (base,key) = gmaps_base_key()
    res = gmaps.directions(A,B,alternatives=True)
    return res

def decode_json_routes(routes_json):
    return list(map(lambda r:Route(r),routes_json))

def fetch_routes(a,b, departure_time=datetime.dateime.now(),traffic_model='pessimistic'):
    dirs = gmaps.directions(a,b,departure_time=departure_time, traffic_model= traffic_model)
    routes:List[Route] = decode_json_routes(dirs)
    return routes

def get_pm25(data):
    return data['pollutants']['pm25']['concentration']['value']

def get_routes(data):
    return data['routes']

def get_points(route):
    return list(map(lambda x:x['start_location'],route['legs'][0]['steps'])) + list(map(lambda x:x['end_location'],route['legs'][0]['steps']))

def get_durations(routes):
    return list(map(lambda x: x['legs'][0]['duration']['text'],routes))

def get_pm25_list(points):
    route_pm25 = []
    for p in points:
        lat = p['lat']
        lon = p['lng']
        data = fetch_point_aq(lat,lon)
        pm25 = get_pm25(data)
        route_pm25.append(pm25)
    
    return route_pm25

def pms_durations(A,B):
    gres = fetch_direction(A,B)
    routes = get_routes(gres)

    pm25_lists = []
    for route in routes:
        points = get_points(route)
        pm25_list = get_pm25_list(points=points)
        pm25_lists.append(pm25_list)

    averages = []
    for pm25_list in pm25_lists:
        avg = average(pm25_list)
        averages.append(avg)

    durations = get_durations(routes)

    return (averages,durations)

def distance_in_meters(p1,p2):
    from math import sin, cos, sqrt, atan2, radians
    R = 6373.0

    lat1 = radians(p1[0])
    lon1 = radians(p1[1])

    lat2 = radians(p2[0])
    lon2 = radians(p2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance * 1000

def getEquidistantPoints(p1, p2, parts):
    return zip(numpy.linspace(p1[0], p2[0], parts+1),
               numpy.linspace(p1[1], p2[1], parts+1))
    
def draw_routes(routes:List[Route],reported_points=[]):
    
    fig = plt.figure(figsize=(20,10))
    colors = ['ko','bo','go','co','mo','k*','b*','g*','c*','m*']
    
    for i,r in enumerate(routes):
        points = r.polypoints    
        for point in points:
            plt.plot(point[1],point[0],colors[i])
        
        #rep points
        for p in reported_points:
            plt.plot(p[1],p[0],'rx',markersize=10)
    
    plt.show()
        
def scatter(points, reported_points=[]):
    fig = plt.figure(figsize=(20,10))
    for point in points:
        plt.plot(point[1],point[0],'bo')
    
    for p in reported_points:
        plt.plot(p[1],p[0],'rx')

    plt.show()
    
def snap_points(points):
    snapped_points = []
    for p in points:
        lat = p[0]
        lon = p[1]
        url = "https://roads.googleapis.com/v1/snapToRoads?path=%f,%f&key=%s" % (lat,lon,api_key)
        response = requests.get(url)
        snapped_point = (response.json()['snappedPoints'][0]['location']['latitude'],response.json()['snappedPoints'][0]['location']['longitude'])
        snapped_points.append(snapped_point)
    return snapped_points

def condense_points(p1,p2):
    new_list = []
    distance = distance_in_meters(p1,p2)
    if distance > 10:
        new_list = [p1] + list(getEquidistantPoints(p1,p2,int(distance/10))) + [p2]
    else:
        new_list = [p1,p2]
    
    return new_list

def is_point_on_rout(point,route:Route):
    on_path = False
    points = route.condenced_points
    for p in points:
        if distance_in_meters(point,p) <= 10:
            on_path = True
            break
    return on_path

def get_searchable_waypoints(orignin_x,origin_y,n=100): 
    angle = numpy.linspace(0,8*2*numpy.pi, n)
    radius = numpy.linspace(0.000002,0.02,n)
    wp_x = radius * numpy.cos(angle) + orignin_x
    wp_y = radius * numpy.sin(angle) + origin_y
    
    return (wp_x,wp_y)

def read_file(filename):
    with open(filename) as f:
        lines = f.readlines()
        return lines
        
def days_hours_minutes(td):
    return td.days, td.seconds//3600, (td.seconds//60)%60

def depart_at(source,destination,preferred_arrival_time):
    dep_time, go_in = get_departure_time(source,destination,preferred_arrival_time)
    days, hours, minutes = days_hours_minutes(go_in)
    print("You need to depart at %s that is %s days %s hours %s minutes from now" % (dep_time.strftime("%H:%M on (%B, %d)"), days, hours, minutes))