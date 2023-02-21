from operator import le
from unittest import mock
import requests
import numpy as np
from typing import List
import polyline
from math import sin, cos, sqrt, atan2, radians
import googlemaps
import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import json
import pytz
import geopy
import geopy.distance
import plotly.express as px



#client initiate gmaps client
api_key = open('google_maps_api.txt').readlines()[0]
brez_api = open('breezometer_api.txt').readlines()[0]
cotrip_api_key = open('cotrip_api_key.txt').readlines()[0] 
plotly_key = open('plotly_key.txt').readlines()[0] 
openweather_key = open('openWeather_api.txt').readlines()[0]
gmaps = googlemaps.Client(key=api_key)   
    
def calc_fastest_routes(A,B,reported_points=[],n_search_points=10, preference='fastest', medium="driving"):
    
    '''This method returns a list of the fastest suggested routes.

    Args:
        A (String): Source location or name 
        B (String): Destination location or name 
        reported_points ([(float,float)], optional): a list of reported road closure points in (flaot,float) format. Defaults to [].
        n_search_points (int, optional): the number of waypoints you want google maps to search in. Defaults to 100.
        preference (String): Either 'fastest' or 'safest'. The first will return a list of the fastest three routes and the second will return the one with least air pollution.
    Returns:
        [Route]: up to three Google Maps Route object in JSON format. 
    '''
    
    routes_dict = {}

    #origin & first route
    try:
        routes = fetch_routes(A,B, medium=medium)
    except googlemaps.exceptions.ApiError as e:  # This is the correct syntax
        print("No route found from %s to %s" % (A,B))
        return None
    
    # if no reported waypoints return first google alternative
    valid_routes = routes
    if len(reported_points) != 0:
        valid_routes = get_valid_routes(A,B,routes,reported_points,n_search_points)
    
    # keep to top 3
    if len(valid_routes) > 3:
        valid_routes = valid_routes[:3]
    
    # fastest & cleanest
    fastest_routes = valid_routes #top 3

    #calc the air quality for the fastest route
    avg_aq, _ = pms_durations_from(fastest_routes[:1])
    avg_aq = avg_aq[0]
    fastest_routes[0].json_object["avg_aq"] = avg_aq
    
    if preference.lower() == 'safest':
        cleanest_route = get_cleanest(fastest_routes)
        return cleanest_route.json_object
    else: # pref is fastest
        return fastest_routes[0].json_object


def get_departure_time(source,destination,preferred_arrival_time, medium="driving"):
    
    '''Return the departure time to go from a source to destination by calculating it in traffic

    Args:
        A (String): Source location or name 
        B (String): Destination location or name
        preferred_arrival_time (date): the time that you want to reach
        medium(String): (Small Case) "driving", "bicycling", "transit" or "walking"

    Returns:
        (date,timedelta,int): returns a tuple containing the departure time, and the duration of the trip
    '''
    
    # Log params
    print("In 'get_departure_time' : ", "source = ", source, " destination = ", destination, " preferred_arrival_time = ", preferred_arrival_time)
    # MT time
    now_svr = datetime.datetime.now()
    now_mt = datetime.datetime.now(pytz.timezone('US/Mountain'))
    #print("Svr time = ", now_svr, " MT time = ", now_mt)
    # Find the offset in hours
    offset_sec = now_mt.utcoffset().total_seconds()
    offset_sec = abs(offset_sec)
    #print("Offset in sec = ", offset_sec)
    # The following line should be commented out when running on local server
    preferred_arrival_time = preferred_arrival_time + timedelta(seconds=offset_sec)

    #normal duration from a to b
    normal_duration = Route(gmaps.directions(source,destination, arrival_time=preferred_arrival_time, mode=medium)[0]).duration
    normal_departure_time = preferred_arrival_time - datetime.timedelta(seconds=normal_duration)

    #real duration
    if normal_departure_time >= datetime.datetime.now() or medium != "driving":
        real_duration = Route(gmaps.directions(source,destination,departure_time=normal_departure_time,traffic_model='pessimistic', mode=medium)[0]).duration
        real_departure_time = preferred_arrival_time - datetime.timedelta(seconds=real_duration)
        real_departure_time = real_departure_time - timedelta(seconds=offset_sec)
        return (real_departure_time, real_duration)
    else:
        alt_duration = Route(gmaps.directions(source, destination, departure_time=datetime.datetime.now(), traffic_model='pessimistic', mode=medium)[0]).duration
        alt_departure_time = preferred_arrival_time - datetime.timedelta(seconds=alt_duration)
        alt_departure_time = alt_departure_time - timedelta(seconds=offset_sec)
        return (alt_departure_time, alt_duration)
        
def get_slack_info_message_content(src,dst,info_object=None,types=["plannedEvents","incidents","roadConditions","weatherStations","airQuality"],filepath=None,previous_air_points=[]):

    '''
    Gets the info needed to generate the slack message to the user
    
    Params:
    src((float,float)): latitude and longitude of the source
    dst((float,float)): latitude and longitude of the destination
    types([str]): a list of the event type to be returned from the following strings ["plannedEvents","incidents","roadConditions","weatherStations","airQuality"]
    
    Returns (dict):
    a dictionary of the info needed to formate the slack message
    -   Avg air quality 
    -   Air Quality Label from 
    -   Road condition {"road_name":"condition"}
    -   Avg temperatur
    -   Temperature face from (https://www.pinterest.com/pin/232990980697006763/)
    -   Min temperature 
    -   Max temperature 
    -   Wind speed
    -   Wind direction
    -   Visibility
    -   Image Bytes
    '''
    
    #get all requested info
    if info_object == None:
        info_object = get_info(src,dst,types=types,previous_air_points=previous_air_points)
    
    #empty object to prep
    return_object = dict()
    
    # -   Avg air quality / label 
    if "airQuality" in info_object:
        avg_aq = info_object["airQuality"]["avg_air_quality"]
        return_object["avg_air_quality"] = avg_aq
        return_object["air_qualit_label"] = get_air_quality_label(float(avg_aq))
    
    # -   Roads condition
    if "roadConditions" in info_object:
        road_conditions = {}
        for road in info_object["roadConditions"]:
            road_name = road["route_name"]
            curren_conds = road["current_conditions"]
            if len(curren_conds) > 0:
                whole_word = curren_conds[0]["conditionDescription"]
                if "-" in whole_word:
                    cond_label = whole_word[whole_word.find("-")+1:]
                    road_conditions[road_name] = cond_label
        return_object["road_conditions"] = road_conditions
    
    # -   Avg temperature
    # -   Min temperature 
    # -   Max temperature 
    # -   Wind speed
    # -   Wind direction
    # -   Visibility
    if "weatherStations" in info_object:
        ws = info_object["weatherStations"]
       
        #values
        return_object["temp"] = ws["temp"]
        return_object["wind_speed"] = ws["wind_speed"]
        return_object["wind_deg"] = ws["wind_deg"]
        return_object["visibility"] = ws["visibility"]
        return_object["uvi"] = ws["uvi"]
        
        # labels
        return_object["wind_label"] = get_wind_label(return_object["wind_speed"])
        return_object["temp_label"] = get_temp_label(return_object["temp"])
        return_object["visibility_label"] = get_visibility_label(return_object["visibility"])
        return_object["uvi_label"] = get_uvi_label(return_object["uvi"])

        
    # - gerenate and save image locally
    air_quality_points = info_object["airQuality"]["points"] if ("airQuality" in info_object and "points" in info_object["airQuality"]) else []
    planned_events = info_object["plannedEvents"] if "plannedEvents" in info_object else []
    incidents = info_object["incidents"] if "incidents" in info_object else []
    routes_points = get_all_possible_routes(src[0],src[1],dst[0],dst[1],condence=True)
    generate_map_image(src,dst,routes_points,air_quality_points,planned_events,incidents, filepath)
    
    return return_object


#################################################### HELPING METHODS ########################################################
#################################################### HELPING METHODS ########################################################
#################################################### HELPING METHODS ########################################################

def get_cached_air_quality(lat,lon,previous_points):
    
    '''
    lat(float): xxx
    lon(float): xxx
    previous_points(list(dic)): [{lat:xx,lon:xx,pm:xx}]
    returns the value of pm 2.5 for the nearest point
    '''
    
    # read all previous stored
    if previous_points == []:
        return None
    
    # get from previous points within 200m
    for p in previous_points:
        if distance(p,[lat,lon]) < 200:
            return p["pm"]
    
    #return none
    return None

def condence_rout_points(route_points):
    #condenced points
    condenced_points = []
    for i in range(1,len(route_points)):
        p1 = route_points[i-1]
        p2 = route_points[i]
        condenced_points += condense_points(p1,p2)
    return condenced_points

def ftoc(f):
    return (f - 32) * 5/9

def get_temp_label(temp_value, deg="f"):
    '''
    temp_value(float): in celcius or fehre
    deg(str): f or c (default f)
    From https://www.researchgate.net/figure/The-comfort-sensation-scale-of-the-physiological-equivalent-temperature-PET_tbl2_258160671
    '''    
    
    if type(temp_value) == str:
        temp_value = float(temp_value)
    
    # if in f convert to c
    if deg == "f":
        temp_value = ftoc(temp_value)
    
    if temp_value <= 4:
        return "Very Cold"
    elif temp_value <= 8:
        return "Cold"
    elif temp_value <= 13:
        return "Cool"
    elif temp_value <= 18:
        return "Slightly Cool"
    elif temp_value <= 23:
        return "Comfortable/Neutral"
    elif temp_value <= 29:
        return "Slightly Warm"
    elif temp_value <= 35:
        return "Warm"
    elif temp_value <= 41:
        return "Hot"
    
    return "Very Hot"

def get_visibility_label(visibility_value):
    
    
    '''
    From https://www.semanticscholar.org/paper/Visual-Improvement-For-Dense-Foggy-%26-Hazy-Weather-%2C-Nirala/97401b46b4d241a1b7a20e1cddf40ce0f3f4b98f
    visibility_value(float): ditance in meters
    '''
    
    if visibility_value < 50:
        return "Dense fog"
    elif visibility_value < 200:
        return "Thick fog"
    elif visibility_value < 500:
        return "Moderate fog"
    elif visibility_value < 1000:
        return "Ligh fog"
    elif visibility_value < 2000:
        return "Thin fog"
    elif visibility_value < 4000:
        return "Haze"
    elif visibility_value < 10000:
        return "Light haze"
    elif visibility_value < 20000:
        return "Clear"
    elif visibility_value < 50000:
        return "Very Clear"
    elif visibility_value < 277000:
        return "Exceptionally Clear"
    
    return "Pure air"

def get_uvi_label(uiv_value):
    '''
    From here https://www.epa.gov/enviro/uv-index-description
    uiv_value(float): the value of uv
    '''
    
    if uiv_value < 2:
        return "Safe"
    if uiv_value < 6:
        return "Take Precautions"
    
    return "Protection needed"

def get_wind_label(avg_speed):
    if avg_speed == "" or avg_speed == None:
        return ""
    elif avg_speed < 1:
        return "Calm"
    elif avg_speed <= 3:
        return "Light Air"
    elif avg_speed <= 7:
        return "Light Breez"
    elif avg_speed <= 12:
        return "Gentle Breeze"
    elif avg_speed <= 18:
        return "Moderate Breeze	"
    elif avg_speed <= 24:
        return "Fresh Breeze"
    elif avg_speed <= 31:
        return "Strong Breeze"
    elif avg_speed <= 38:
        return "Near Gale"
    elif avg_speed <= 46:
        return "Gale"
    elif avg_speed <= 54:
        return "Storm"
    elif avg_speed <= 64:
        return "Light Breez"
    elif avg_speed <= 72:
        return "Violent Storm"
    else:
        return "Hurricane"
    

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
        
        # average pm2.4
        self.avg_aq = 0
        
        
## Functions

def get_valid_routes(A,B,routes:List[Route],reported_points,n_search_points=100):
    
    #else look for ways to avoid 
    origin_x = routes[0].json_object['legs'][0]['start_location']['lng']
    origin_y = routes[0].json_object['legs'][0]['start_location']['lat']

    #waypoints
    wp_x,wp_y = get_searchable_waypoints(origin_x,origin_y) #src x & y
    
    all_routes_list = [] + routes
    valid_routes_list = [] + routes
    shortest_route = routes[0]

    for i in range(0,n_search_points):
        waypoint = "%f,%f" % (wp_y[i],wp_x[i])
        try:
            #get the routes
            directions = gmaps.directions(A,B,waypoints=[waypoint])
            valid_routes_list += decode_json_routes(directions)
            all_routes_list += valid_routes_list
            
            #filter
            for p in reported_points:
                valid_routes_list = list(filter(lambda r: is_point_on_rout(p,r) == False,valid_routes_list))
            
            #set shortest
            valid_routes_list.sort(key=lambda r:r.duration)
            
            new_route = min([shortest_route,valid_routes_list[0]],key=lambda r:r.duration)
            if new_route.duration < shortest_route.duration:
                shortest_route = new_route
            
        except googlemaps.exceptions.ApiError as e:
            continue
    
    #return valid routes list
    return valid_routes_list

def breez_base_key():
    base = "https://api.breezometer.com/air-quality/v2/"
    api_key = brez_api
    return (base,api_key)

def fetch_point_aq(lat,lon):
    (base,api_key) = breez_base_key()
    api = "current-conditions?lat=%f&lon=%f&features=pollutants_concentrations&key=%s" % (lat,lon,api_key)
    res = requests.get(base+api).json()    
    return res['data']

def average(lst):
    return sum(lst) / len(lst)

def gmaps_base_key():
    base = "https://maps.googleapis.com/maps/api/"
    api_key #= api_key
    return (base,api_key)

def fetch_direction(A,B):
    res = gmaps.directions(A,B,alternatives=True)
    return res

def decode_json_routes(routes_json):
    return list(map(lambda r:Route(r),routes_json))

def fetch_routes(a,b, departure_time=None,traffic_model='pessimistic', medium="DRIVING"):
    if departure_time == None:
        dirs = gmaps.directions(a,b, alternatives=True, mode=medium)
    else:
        dirs = gmaps.directions(a,b,departure_time=departure_time, traffic_model= traffic_model,alternatives=True)
    routes:List[Route] = decode_json_routes(dirs)
    return routes

def get_pm25(data):
    return data['pollutants']['pm25']['concentration']['value']

def get_routes(data):
    return data['routes']

def get_points(route):
    return list(map(lambda x:x['start_location'],route['legs'][0]['steps'])) + list(map(lambda x:x['end_location'],route['legs'][0]['steps']))

def get_points_from(route:Route):
    return list(map(lambda x:x['start_location'],route.steps)) + list(map(lambda x:x['end_location'],route.steps))

def get_n_points_from(route:Route):
    all_points = list(map(lambda x:x['start_location'],route.steps))

def get_durations(routes):
    return list(map(lambda x: x['legs'][0]['duration']['text'],routes))

def get_durations_from(routes:List[Route]):
    return list(map(lambda x: x.duration,routes))

def get_pm25_list(points):
    route_pm25 = []
    for p in points:
        lat = p['lat']
        lon = p['lng']
        data = fetch_point_aq(lat,lon)
        pm25 = get_pm25(data)
        route_pm25.append(pm25)
    
    return route_pm25

def pms_durations_from(routes:List[Route]):
    
    #get points
    points_lists = []
    for route in routes:
        points = get_points_from(route)
        points_lists.append(points)
    
    #reduce points
    reduced = reduce_points(points_lists)
    
    #pm25
    pm25_lists = []
    for points in reduced:
        pm25_list = get_pm25_list(points=points)
        pm25_lists.append(pm25_list)

    #calc avg
    averages = []
    for pm25_list in pm25_lists:
        avg = average(pm25_list)
        averages.append(avg)

    #calc dur
    durations = get_durations_from(routes)
    
    return (averages,durations)

def get_cleanest(routes:List[Route]):    
    
    if len(routes) < 2:
        return routes[0]
    
    avgs, durs = pms_durations_from(routes[1:]) #TODO:PUT DURATION IN THE FORMULA
    
    avgs.insert(0,routes[0].avg_aq)
    
    min_i = 0
    for i in range(1,len(routes)):
        if avgs[min_i] > avgs[i]:
            min_i = i
    
    # append 
    cleanest = routes[min_i]
    cleanest.json_object["avg_aq"] = avgs[min_i]
    
    return cleanest

def pms_durations(A,B):
    routes = fetch_direction(A,B)
    return pms_durations(routes)

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
    return zip(np.linspace(p1[0], p2[0], parts+1),
               np.linspace(p1[1], p2[1], parts+1))
    
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
        url = "https://roads.googleapis.com/v1/snapToRoads?path=%f,%f&key=AIzaSyCPn4Pny_cpmP3FE3c7ecQoDNaxsubEOZ0" % (lat,lon)
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
    angle = np.linspace(0,8*2*np.pi, n)
    radius = np.linspace(0.000002,0.02,n)
    wp_x = radius * np.cos(angle) + orignin_x
    wp_y = radius * np.sin(angle) + origin_y
    
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
    

#common points
def find_common_points(points_lists):
    
    '''
    finds common points from a list of lists
    returns: a list of the common points
    '''
    
    common_points = []
    for p in points_lists[0]:
        common = True
        for i in range(1,len(points_lists)):
            if p not in points_lists[i]:
                common = False
        if common:
            common_points.append(p)
    return common_points


#remove from each list what is in common
def remove_common(points_lists, common):
    
    '''
    removes common points from a list of list
    returns: a list of lists with common points removed
    '''
    
    for pl in points_lists:
        for p in pl:
            if p in common:
                pl.remove(p)
    return points_lists
            
#reduce to 5 points max

def reduce_to(new_list,n=5):
    
    '''
    common points from a list of list
    returns: a list of lists with common points removed
    '''
    
    length = len(new_list)
    
    if length <= n:
        return new_list
    
    small_list = new_list.copy()
    #more than 5
    remove_n = length - 5
    chunk = int(length/3)
    i = 0 
    while i < remove_n:
        if chunk > len(small_list):
            del small_list[chunk]
        i += 1

    return small_list


def reduce_points(points_list, n=5):
    
    '''
    reduce the number of points from a list of lists to 5 points
    returns a list of list of the reduced number of points
    '''
    common_points = find_common_points(points_list)
    removed_common = remove_common(points_list, common_points)
    reduced_lists = []
    for lst in removed_common:
        ptlst = reduce_to(lst,n)
        reduced_lists.append(ptlst)
    return reduced_lists

#helping funcs
def distance(p1,p2):
    '''
    Returns the distance between two coordinates in meters
    p1((float,float))*: tuple of latitidue and longitude for the first point
    p2((float,float))*: tuple of latitidue and longitude for the second point
    returns (float): distance in meters
    '''
    return geopy.distance.geodesic(p1, p2).m

def draw_circle(src_p,dst_p,threashhold=50):
    '''
    Returns a circle center and radius between two points
    src_p((float,float))*: tuple of latitidue and longitude for the source point
    dst_p((float,float))*: tuple of latitidue and longitude for the destination point
    threashhold(float): an extra distance that will expand outside the circle in both directions in (m)
    returns((float,float),float): a tuple of center and radius
    '''
    center_lat = (src_p[0] + dst_p[0]) / 2
    center_lon = (src_p[1] + dst_p[1]) / 2
    radius = distance(src_p,dst_p)/2 + threashhold
    
    return ((center_lat,center_lon),radius)
    
def in_circle(point,center,radius):
    '''
    Returns if a point is in a circle or not
    point((float,float)): the test point
    center((float,float)): center of circle
    radius(float): the radius of the circle
    returns(bool): True or False
    '''
    return distance(center,point) < radius

def fetch(type):
    '''
    type(str): fetches COTrip's API based on the type ["plannedEvents","incidents","roadConditions","weatherStations","snowPlows"]
    returns([dict]): json response of the API call
    '''
    return requests.get("https://data.cotrip.org/api/v1/%s?apiKey=J2N7GKZ-37Q4XSB-HXDQKMJ-6EEQH88"%type).json()

##### FILTERING FUNCTIONS 

def filter_events(events,src,dst,method="rect",all_points=None):
    '''
    Filters the events to be in a circle between src and dist
    events([dict]): The response from the cotrip API call
    src((float,float))*: tuple of latitidue and longitude for the source point
    dst((float,float))*: tuple of latitidue and longitude for the destination point
    to_date(date): the end date to filter by (Default tomorrow's date)
    '''
    
    close_events = []
    for event in events["features"]:
        coords = event["geometry"]["coordinates"]
        for coord in coords:
            point_isin = filter_point(src,dst,coord[1],coord[0],method,all_points)
            # add if in
            if point_isin:
                close_events.append(event)
            
    return close_events

def filter_incidents(events,src,dst,method="rect",all_points=None):
    '''
    Filters the events to be in a circle between src and dist
    events([dict]): The response from the cotrip API call
    src((float,float))*: tuple of latitidue and longitude for the source point
    dst((float,float))*: tuple of latitidue and longitude for the destination point
    to_date(date): the end date to filter by (Default tomorrow's date)
    '''
    
    close_events = []
    for event in events["features"]:
        coords = event["geometry"]["coordinates"]
        point_isin = False
        
        # if 1d array make 2d
        if not isinstance(coords[0], list): 
            coords = [coords]
            
        for coord in coords:
            if len(coord) != 2:
                continue
            point_isin = filter_point(src,dst,coord[1],coord[0],method,all_points)
            if point_isin:
                close_events.append(event)
                break
                    
    return close_events

def filter_roadConditions(res,src,dst,method="rect",all_points=None):
    '''
    Filters the road conditions to be in a circle between src and dist
    res([dict]): The response from the cotrip API call
    src((float,float))*: tuple of latitidue and longitude for the source point
    dst((float,float))*: tuple of latitidue and longitude for the destination point
    to_date(date): the end date to filter by (Default tomorrow's date)
    returns: a list of filtered road condition objects
    '''
    in_roads = []
    rect = get_rectangel(src,dst,all_points)
    
    for road in res["features"]:
        road["in_points"] = list(filter(lambda x: point_in_rect(rect,(x[1],x[0])),road["geometry"]["coordinates"]))
        if len(road["in_points"]) > 0:
            in_roads.append(road)
        
    return in_roads

def filter_weatherStations(res,src,dst,method="rect",all_points=None):
    '''
    Filters the weather station points to be in a circle between src and dist
    points([list(float,float)]): a list of points 
    src((float,float))*: tuple of latitidue and longitude for the source point
    dst((float,float))*: tuple of latitidue and longitude for the destination point
    returns: a list of filtered weather station points 
    ''' 
    return list(filter(lambda x: filter_point(src,dst,x["geometry"]["coordinates"][1],x["geometry"]["coordinates"][0],method,all_points),res["features"]))


def filter_point(src,dst,lat,lon,method="rect",all_points=None):
    if method == "rect":
        rect = get_rectangel(src,dst,all_points) #for the rectange method
        return point_in_rect(rect,(lat,lon))
    else:
        c,r = draw_circle(src,dst)
        return in_circle((lat,lon),c,r)

def get_plannedEvents(src,dst,to_date=None,method="rect",routes_points=None):
    '''
    Gets the planned events from source to destination 
    src((float,float))*: tuple of latitidue and longitude for the source point
    dst((float,float))*: tuple of latitidue and longitude for the destination point
    to_date(date): the end date to filter by (Default tomorrow's date)
    method(str): the filteration method (rect/circle)
    routes_points([(lat,lon)...]): a list of all roads points from source to destination
    returns: a list of planned events json objects
    '''
    events = fetch("plannedEvents")
    close_events = filter_events(events,src,dst,method,routes_points)
    
    #filter by date
    if to_date == None:
        today = datetime.datetime.today()
        to_date = today 
    
    # get all events that started in the past and did not end yet or will start tomorrow.
    timely_events = list(filter(lambda x: datetime.datetime.strptime(x["properties"]["schedule"][0]["startTime"],'%Y-%m-%dT%H:%M:%S.%fZ').date() == today.date() , close_events))
    timely_events.sort(key=lambda x: x["properties"]["startTime"])
        
    # construct return dictionary
    planned_events = []
    for event in timely_events:
        text = event["properties"]["travelerInformationMessage"]
        start_date = event["properties"]["schedule"][0]["startTime"]
        end_date = event["properties"]["schedule"][0]["endTime"]
        points = []
        for point in event["geometry"]["coordinates"]:
            points.append(point)
            
        #add event to dictionary
        planned_events.append({"text":text,"start_date":start_date,"end_date":end_date,"points":points})
    
    #return plannedEvents
    return planned_events

def get_incidents(src,dst,method="rect",routes_points=None):
    '''
    Gets the indidents from source to destination 
    src((float,float))*: tuple of latitidue and longitude for the source point
    dst((float,float))*: tuple of latitidue and longitude for the destination point
    method(str): the filteration method (rect/circle)
    routes_points([(lat,lon)...]): a list of all roads points from source to destination
    returns: a list of incident json objects
    '''
    events = fetch("incidents")
    close_events = filter_incidents(events,src,dst,method,routes_points)
    
    if len(close_events) == 0:return [] # return if 0
    
    #filter cleared 
    filtered_events = list(filter(lambda x: x["properties"]["status"] != "event cleared" , close_events))
    
    if len(filtered_events) == 0:return [] # return if 0
    
    # construct return dictionary
    planned_events = []
    for event in filtered_events:
        text = event["properties"]["travelerInformationMessage"]
        start_date = event["properties"]["startTime"]
        points = []
        # sometimes it is a 1d arry (case 1) and sometimes it is 2d (case 2)
        coords = event["geometry"]["coordinates"]
        if type(coords[0]) == float:
            points.append(coords)
        else:
            for point in coords:
                points.append(point)
            
        #add event to dictionary
        planned_events.append({"text":text,"start_date":start_date,"points":points})
    
    #return plannedEvents
    return planned_events
    

def get_currentRoadConditions(src,dst,method="rect",routes_points=None):
    '''
    Gets the current road conditions from source to destination 
    src((float,float))*: tuple of latitidue and longitude for the source point
    dst((float,float))*: tuple of latitidue and longitude for the destination point
    method(str): the filteration method (rect/circle)
    routes_points([(lat,lon)...]): a list of all roads points from source to destination
    returns: a list of road condition json objects
    '''
    res = fetch("roadConditions")
    in_roads = filter_roadConditions(res,src,dst,method,routes_points)
        
    # construct return dictionary
    in_road_conditions = []
    for road in in_roads:
        obj = dict(
            route_name = road["properties"]["routeName"],
            current_conditions = road["properties"]["currentConditions"],
            in_points = road["in_points"]
        )
            
        #add event to dictionary
        in_road_conditions.append(obj)
    
    #return plannedEvents
    return in_road_conditions

def sort_by_closest(point,x):
    return geopy.distance.geodesic(point,[x[1],x[0]]).m

def get_weather_info(point):
    '''
    Gets the weather information at source using OpenWeatherAPI (temperature, feels like temperature, wind speed, wind direction, uvi, visibility)
    src((float,float))*: tuple of latitidue and longitude for the source point
    method(str): the filteration method (rect/circle)
    returns: a list of weather information json objects
    '''
    lat = point[0]
    lon = point[1]
    res = requests.get(f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={openweather_key}&units=imperial").json()
    
    if "current" in res:
        res = res["current"]
    else:
        return {}

    #print temp
    print("open weather result = ", res)
    #information
    obj = dict()    
    obj["temp"] = res["temp"] if "temp" in res else None
    obj["wind_speed"] = res["wind_speed"] if "temp" in res else None
    obj["visibility"] = res["visibility"] if "temp" in res else None
    obj["uvi"] = res["uvi"] if "temp" in res else None
    obj["wind_deg"] = res["wind_deg"] if "temp" in res else None
    
    return obj
    
def get_weatherStations(src):
    '''
    Gets the weather information at source location (Min, max and current temperature, avg wind speed, avgh wind direction, visibility, and precpipitation rate)
    src((float,float))*: tuple of latitidue and longitude for the source point
    returns: a list of weather information json objects
    '''
    res = fetch("weatherStations")
    weather_stations = res["features"]
    ws_geo = list(filter(lambda x: "geometry" in x,weather_stations))
    ws_sorted = sorted(ws_geo, key=lambda x: sort_by_closest(src,x["geometry"]["coordinates"])) 
    
    keys = ["min temperature","max temperature", "temperature","average wind speed","average wind direction","visibility","precipitation rate"]
    obj = dict()
    
    for key in keys:
        for station in ws_sorted:
            values = list(filter(lambda x: x["type"] == key,station["properties"]["sensors"]))
            obj[key] = None
            if len(values) > 0:
                if "currentReading" in values[0]:
                    try:
                        obj[key] = float(values[0]["currentReading"])
                    except ValueError:
                        obj[key] = values[0]["currentReading"]   
                    
                    #value fouhnd in this station
                    break
        
    return obj

def calc_space_between_points(src,dst,routes_points=None):
    return 200

def read_all_previous_aq_points():
    return []

def get_roadAirQuality(src,dst,routes_points=None,space_between_points=None,max_points=25,previous_points=[]):
    '''
    Gets the road air quality
    src((float,float))*: tuple of latitidue and longitude for the source point
    dst((float,float))*: tuple of latitidue and longitude for the destination point
    routes_points([(lat,lon)...]): a list of all roads points from source to destination
    space_between_points(int): The space between each coordinate in the matrix
    max_points(int): the maximum number of points to include in the matrix
    returns: a dictionary of average air quality and a list of pm2.5 information for each coordniate
    '''
    #space between points
    if space_between_points == None:
        space_between_points = calc_space_between_points(src,dst,routes_points)
    
    #read previous stored points
    if previous_points == []:
        previous_points = read_all_previous_aq_points()
    
    #make matrix 
    rect = get_rectangel(src,dst,routes_points,lat_first=True)
    matrix = get_matrix(rect,space_between_points,max_points)
    (base,api_key) = breez_base_key()

    #call for each point
    responses = []
    for p in matrix:
        (lat,lon) = p   
        pm = get_cached_air_quality(lat,lon,previous_points)
        if pm == None: 
            api = "current-conditions?lat=%f&lon=%f&features=pollutants_concentrations&key=%s" % (lat,lon,api_key)
            res = requests.get(base+api).json()    
            pm = res["data"]["pollutants"]["pm25"]["concentration"]["value"]
        responses.append(dict(
            lat = lat,
            lon = lon,
            pm = pm,
            full_res = res
        ))
            
    
    avg_air = average(list(map(lambda x: x["pm"],responses)))
    
    air_q_dict = dict(
        avg_air_quality = avg_air,
        points = responses
    )
    
    return air_q_dict

def get_matrix(rect,space=2000, max_points=25):

    #make the matrix 
    points_steps = int(sqrt(max_points))
    
    #right col
    right_points = rect[:2]
    spaced_col_r = np.linspace(right_points[0],right_points[1],points_steps)

    #left col
    left_points = rect[2:]
    spaced_col_l = np.linspace(left_points[1],left_points[0],points_steps)

    matrix = []
    for i in range(len(spaced_col_r)):
        
        row = list(np.linspace(spaced_col_r[i],spaced_col_l[i],points_steps))
        matrix += row
    
    #space the matrix
    spaced_matrix= []
    spaced_matrix.append(matrix[0])
    for p in matrix[1:]:
        far = True
        for sp in spaced_matrix:
            dist = geopy.distance.geodesic(sp, p).m
            if dist < space:
                far = False
                break
        if far:
            spaced_matrix.append(p)
        
    return spaced_matrix

def get_all_possible_routes(lat_1,lon1,lat_2,lon_2,condence=False):
    """
    It uses the gmaps library to get all the possible routes between the two points and then decodes the polylines for each route.
    lat_1 (float): latitude for point 1
    lon_1 (float): longitude for point 1
    lat_2 (float): latitude for point 2
    lat_2 (float): longitude for point 2
    Returns (list): A list of all the decoded points for all the routes between the two locations.
    """
    dirs = gmaps.directions((lat_1,lon1),(lat_2,lon_2), alternatives=True)
    all_points = []
    for i,dir in enumerate(dirs):
        poly = dir["overview_polyline"]["points"]
        points = polyline.decode(poly) 
        points = list(map(lambda x: (x[0],x[1],i),points))
        
        #if condence
        if condence:
            cpoints = []
            for pi in range(1,len(points)):
                p1 = points[pi-1]
                p2 = points[pi]
                c = condense_points((p1[0],p1[1]),(p2[0],p2[1]))
                cpoints = cpoints + c
            cpoints = list(map(lambda x: (x[0],x[1],i),cpoints))
            points = cpoints
        
        all_points = all_points + points
    
    return all_points

def in_rect(lat,lon,bl,tr):
    """
    Checks if coordinates (lat,long) are inside a rectangle defined by bottom left (bl) and top right (tr) corners.    
    lat: float
        Latitude coordinate of the point.
    lon: float
        Longitude coordinate of the point.
    bl: (float, float)
        Tuple containing bottom left coordinates of the rectangle.
    tr: (float, float)
        Tuple containing top right coordinates of the rectangle.
    
    Returns
    -------
    bool
        True if point (lat,long) is inside the rectangle, False otherwise.
    """
    
    return lon >= bl[0] and lon <= tr[0] and lat <= tr[1] and lat >= bl[1]

def point_in_rect(rect,point):
    '''
    rect([(float,float)x4]): [top_left,top_right,bottom_right,bottom_left]
    point([float,float]): lat, lon
    returns(Bool): True/False
    '''
    lat = point[0]
    lon = point[1]
    bl = rect[-1]
    tr = rect[1]
    
    return in_rect(lat,lon,bl,tr)

def line_intersect_rect(rect,line):
    for i,point in enumerate(rect):
        next_point = rect[i+1 % len(rect)]
        segment = [point,next_point]
        if intersect(segment[0],segment[1],line[0],line[1]):
            return True
    return False

def get_rectangel(src,dst,all_points=None,threshhold=50,lat_first=False):
    '''
    src([float,float]): (Latituide, Longitude)
    dst([float,float]): (Latituide, Longitude)
    returns([(float,float)x4]): [top_left,top_right,bottom_right,bottom_left]
    '''
    #call gmaps
    if all_points == None:
        all_points = get_all_possible_routes(src[0],src[1],dst[0],dst[1])
        
    #get points
    top = max(all_points, key=lambda x:x[1])[1]
    right = max(all_points, key=lambda x:x[0])[0]
    bottom = min(all_points, key=lambda x:x[1])[1]
    left = min(all_points, key=lambda x:x[0])[0]
    
    #make rect
    rect = [(top,left),(top,right),(bottom,right),(bottom,left)]
    
    if lat_first:
        rect = [(left,top),(right,top),(right,bottom),(left,bottom)]
    
    return rect

# Return true if line segments AB and CD intersect
def line_intersect_rect(rect,line):
    '''
    Checks if a line intersects a rectangle 
    rect([(float,float)x4]): four points of the corners of the rectangle [(lat,lon)*4]
    line([[float,float],[float,float]]): two points of the start and end of the line
    returns (bool): True/False
    '''
    for i in range(len(rect)):
        next_i = (i+1) % len(rect)
        next_point = rect[next_i]
        segment = [rect[i],next_point]
        if intersect(segment[0],segment[1],line[0],line[1]):
            return True
    return False

def intersect(A,B,C,D):
    '''
    Checks if line A-B intersects with line C-D
    A([float,float]): (Latituide, Longitude)
    B([float,float]): (Latituide, Longitude)
    C([float,float]): (Latituide, Longitude)
    D([float,float]): (Latituide, Longitude)
    returns (bool): True/False
    '''
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

#helping functions to find intersects (see intersects)
def ccw(A,B,C):
    return (C[0]-A[0]) * (B[1]-A[1]) > (B[0]-A[0]) * (C[1]-A[1])
    
    
def zoom_center(lons: tuple=None, lats: tuple=None, lonlats: tuple=None,
        format: str='lonlat', projection: str='mercator',
        width_to_height: float=2.0):
    """Finds optimal zoom and centering for a plotly mapbox.
    Must be passed (lons & lats) or lonlats.
    Temporary solution awaiting official implementation, see:
    https://github.com/plotly/plotly.js/issues/3434
    
    Parameters
    --------
    lons: tuple, optional, longitude component of each location
    lats: tuple, optional, latitude component of each location
    lonlats: tuple, optional, gps locations
    format: str, specifying the order of longitud and latitude dimensions,
        expected values: 'lonlat' or 'latlon', only used if passed lonlats
    projection: str, only accepting 'mercator' at the moment,
        raises `NotImplementedError` if other is passed
    width_to_height: float, expected ratio of final graph's with to height,
        used to select the constrained axis.
    
    Returns
    --------
    zoom: float, from 1 to 20
    center: dict, gps position with 'lon' and 'lat' keys

    >>> print(zoom_center((-109.031387, -103.385460),
    ...     (25.587101, 31.784620)))
    (5.75, {'lon': -106.208423, 'lat': 28.685861})
    """
    if lons is None and lats is None:
        if isinstance(lonlats, tuple):
            lons, lats = zip(*lonlats)
        else:
            raise ValueError(
                'Must pass lons & lats or lonlats'
            )
    
    maxlon, minlon = max(lons), min(lons)
    maxlat, minlat = max(lats), min(lats)
    center = {
        'lon': round((maxlon + minlon) / 2, 6),
        'lat': round((maxlat + minlat) / 2, 6)
    }
    
    # longitudinal range by zoom level (20 to 1)
    # in degrees, if centered at equator
    lon_zoom_range = np.array([
        0.0007, 0.0014, 0.003, 0.006, 0.012, 0.024, 0.048, 0.096,
        0.192, 0.3712, 0.768, 1.536, 3.072, 6.144, 11.8784, 23.7568,
        47.5136, 98.304, 190.0544, 360.0
    ])
    
    if projection == 'mercator':
        margin = 1.2
        height = (maxlat - minlat) * margin * width_to_height
        width = (maxlon - minlon) * margin
        lon_zoom = np.interp(width , lon_zoom_range, range(20, 0, -1))
        lat_zoom = np.interp(height, lon_zoom_range, range(20, 0, -1))
        zoom = round(min(lon_zoom, lat_zoom), 2)
    else:
        raise NotImplementedError(
            f'{projection} projection is not implemented'
        )
    
    return zoom, center

def get_info(src,dst,to_date=None,method="rect",types=["plannedEvents","incidents","roadConditions","weatherStations","airQuality"],previous_air_points=[]):
    
    '''
    Returns the information points for the selected API type that resides between the src and destination
    src((float,float))*: tuple of latitidue and longitude for the source point
    dst((float,float))*: tuple of latitidue and longitude for the destination point
    to_date(date): the end date to filter by (Default tomorrow's date)
    types([str]): a list of the event type to be returned from the following strings ["plannedEvents","incidents","roadConditions","weatherStations","airQuality"]
    returns: a dictionary of list of each type
    '''
    
    info_dic = {}
    routes_points = get_all_possible_routes(src[0],src[1],dst[0],dst[1])
    for type in types:
        if type == "plannedEvents":
            info_dic[type] = get_plannedEvents(src,dst,to_date,method,routes_points)
            print("Planned Events: %d" % len(info_dic[type]))
        elif type == "incidents":
            info_dic[type] = get_incidents(src,dst,method,routes_points)
            print("Incidents: %d" % len(info_dic[type]))
        elif type == "roadConditions":
            info_dic[type] = get_currentRoadConditions(src,dst,method,routes_points)
            print("Road Conditions: %d" % len(info_dic[type]))
        elif type == "weatherStations":
            info_dic[type] = get_weather_info(src)
            print("Weather Stations: %d" % len(info_dic[type]))
        elif type == "airQuality":
            info_dic[type] = get_roadAirQuality(src,dst,routes_points,previous_points=previous_air_points)
            print("Road Avg Quality: %d" % len(info_dic[type]["points"]))
        else:
            return info_dic
    #return 
    return info_dic


def generate_map_image(src,dst,routes_points,airQuality_info=[],plannedEvents_info=[],incidents_info=[], filepath=None):
    
    '''
    src((float,float)): latitude and longitude of the source
    dst((float,float)): latitude and longitude of the destination
    routes_points([(float,float)...]): list of points of the all possible routes from src to dst
    airQuality_info(dict): a dictionary of the airQuality_info from get_info["airQuality"]
    plannedEvents_info(dict): a dictionary of the plannedEvents_info from get_info["plannedEvents"]
    incidents_info(dict): a dictionary of the incidents_info from get_info["incidents"]
    filepath(str) optional: saves the image to the specified filepath
    returns(bytes): returns the bytes of the image 
    '''
    
    import plotly.graph_objects as go
    import plotly.express as px
    px.set_mapbox_access_token(plotly_key)

    #coords
    lats = [src[0],dst[0]]
    lons = [src[1],dst[1]]

    #zoom function
    zoom, center = zoom_center(lons=lons,lats=lats)
    
    #main fig (air)
    colors = ["green","yellow","yellow","orange","orange","red","red","red","red","red","purple","purple","purple","purple","purple"]
    if airQuality_info == [] or airQuality_info == None:
        airQuality_info = [{"lat":src[0],"lon":src[1],"pm":0},{"lat":dst[0],"lon":dst[1],"pm":0}]
        colors = ["white","white"]
        
    #remove_at location if more than two points for readaility
    if len(airQuality_info) > 2:
        airQuality_info = list(filter(lambda x: not ((x["lat"] == src[0] and x["lon"] == src[1]) or ((x["lat"] == dst[0] and x["lon"] == dst[1]))),airQuality_info))
    
    #create main figure
    main_fig = px.scatter_mapbox(airQuality_info,
                                lat="lat",lon="lon",color="pm",size=[40]*len(airQuality_info),
                                text=list(map(lambda x: str(round(x["pm"],1)),airQuality_info)),
                                color_continuous_scale=colors,
                                range_color=[0,250],
                                opacity=0.15,
                                size_max=40,
                                zoom=zoom-1,center=center,
                                height=600, width=800,labels={"pm":"Pm2.5 Level"})
    
    main_fig.update_traces(textfont=dict(color="gray"),marker=dict(allowoverlap=True),selector=dict(type='scattermapbox'))
    main_fig.update_coloraxes(colorbar=dict(orientation="h",thickness=15, yanchor="top", bgcolor="white"),colorbar_title=dict(text="Particle air pollution (PM2.5 in ug/m3)",side="top"))

    #add roads
    colors = ["dodgerblue","lightsteelblue","cornflowerblue","skyblue"]
    main_fig.add_scattermapbox(lat=list(map(lambda x: x[0],routes_points)),
                            lon=list(map(lambda x: x[1],routes_points)),
                            mode = "markers",
                            marker={'size': 2, 'color': list(map(lambda x: colors[x[2]],routes_points)), 'allowoverlap': True},
                            showlegend=False,
                            legendgroup=None)


    # #add events
    for event in plannedEvents_info:
        main_fig.add_scattermapbox(lat=list(map(lambda x: x[1],event["points"])),
                                lon=list(map(lambda x: x[0],event["points"])),
                                mode = "markers+text",
                                marker=dict(size= 8,color= 'yellow',allowoverlap=True, symbol="square"),
                                showlegend=False,
                                textfont=dict(
                                    size=10,
                                    color="white"
                                    ),
                                text="construction",
                                textposition="bottom center",
                                legendgroup=None)

    # #add incidents
    for inc in incidents_info:
        main_fig.add_scattermapbox(lat=list(map(lambda x: x[1],inc["points"])),
                                lon=list(map(lambda x: x[0],inc["points"])),
                                mode = "markers+text",
                                marker=dict(size= 8,color='red',allowoverlap=True, symbol="triangle"),
                                showlegend=False,
                                text="Incident",
                                textposition="bottom center",
                                textfont=dict(
                                    size=10,
                                    color="white"),
                                legendgroup=None)

    #add srs/dst
    main_fig.add_scattermapbox(lat=lats,
                            lon=lons,
                            mode = "markers+text",
                            text=["FROM","TO"],
                            textposition="bottom center",
                            showlegend=False,
                            marker=dict(
                                size=0,color="white"
                            ),
                            textfont=dict(
                                size=14,
                                color="white"
                            ),
                            legendgroup=None)
    
    #figure layout
    main_fig.update_layout(
                        mapbox=dict(style='dark'),
                        margin=dict(l=4, r=4, t=4, b=4)
                        )

    #store locally
    if filepath != None:
            main_fig.write_image(filepath)
    
    #generate bytes
    img_bytes = main_fig.to_image(format="png")
    
    return img_bytes

def get_air_quality_label(pm25_value:float):
    '''
    Returns if air quality is Good/Fair/Poor/Very Poor/Exremely Poor based pm25 level (www.epa.vic.gov.au)
    pm25_value(float): value of pm25
    returns(str): Good/Fair/Poor/Very Poor/Exremely Poor
    '''

    if pm25_value < 25:
        return "Good"
    elif pm25_value < 50:
        return "Fair"
    elif pm25_value < 100:
        return "Poor"
    elif pm25_value < 300:
        return "Very Poor"
    else:
        return "Exremely Poor"