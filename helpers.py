from numpy import sin, cos, arccos, pi, round
from requests import get
from json import loads
import pandas as pd

def rad_to_deg(radians):
    degrees = radians * 180 / pi
    return degrees

def deg_to_deg(degrees):
    radians = degrees * pi / 180
    return radians

def get_distance_between_points_new(latitude1, longitude1, latitude2, longitude2, unit = 'kilometers'):
    
    theta = longitude1 - longitude2
    
    distance = 60 * 1.1515 * rad_to_deg(
        arccos(
            (sin(deg_to_deg(latitude1)) * sin(deg_to_deg(latitude2))) + 
            (cos(deg_to_deg(latitude1)) * cos(deg_to_deg(latitude2)) * cos(deg_to_deg(theta)))
        )
    )
    
    if unit == 'miles':
        return round(distance, 2)
    if unit == 'kilometers':
        return round(distance * 1.609344, 2)



def routing_time(lat1, long1, lat2, long2, vehicle):
    response = str(get(f"https://graphhopper.com/api/1/route?point={lat1},{long1}&point={lat2},{long2}&profile={vehicle}&locale=tr&calc_points=false&key=e39286d8-4f12-4dee-9fbf-3b61b01a7125"))
    
    if response == "<Response [200]>":
        js=str(get(f"https://graphhopper.com/api/1/route?point={lat1},{long1}&point={lat2},{long2}&profile={vehicle}&locale=tr&calc_points=false&key=e39286d8-4f12-4dee-9fbf-3b61b01a7125").content)[2:-1]
        return (loads(js)["paths"][0]["time"]) / 60000
    else:
        return None



def parser(datas=["cinema", "lunapark", "museum", "park"]):
    for d in datas:
        data = pd.read_json(f"./Data/{d}.json")
        urls = data["placeUrl"]

        for url, i in zip(urls, range(len(urls))):
            lat1, lat2 = url.index("!3d")+3, url.index("!4d")
            long1, long2 = lat2+3, url.index("!16")
            data["latitude"].iloc[i], data["longitude"].iloc[i] = url[lat1:lat2], url[long1:long2]
            data.to_json(f"./Data/{d}.json")