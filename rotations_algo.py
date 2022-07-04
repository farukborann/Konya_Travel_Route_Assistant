from helpers import get_distance_between_points_new, routing_time
from shapely.geometry import Point
from datetime import datetime
from shapely.wkt import loads
import pandas as pd

coef = 0.2

def filter(choices):
    potential_choices = pd.DataFrame()
    for c in choices:
        potential_choices = potential_choices.append(pd.read_json(f"./Data/{c}.json"), ignore_index=True)
    return potential_choices


def get_positions_dataframe(current_location, potential_choices, avaible_time, budget):
    potential_choices = filter(potential_choices)
    trip_radius = coef * avaible_time
    title_pool = list()
    
    mahalle = pd.read_csv("Data/mahalle.csv").drop("Unnamed: 0", axis=1)[["geometry","SESDensity"]]
    coords_df = potential_choices[["title","latitude", "longitude", "rating","placeUrl"]]
    bikes = pd.read_json("Data/bisiklet_kiralama_konumları.json")
    # bike check
    for long, lat in zip(bikes["x"], bikes["y"]):
        if get_distance_between_points_new(current_location[0],
                                           current_location[1], 
                                           lat, 
                                           long) < 0.3:

            bike_station = [lat, long]
            # trip_size check    
            for title, lat, long, rating, placeUrl in zip(coords_df["title"], coords_df["latitude"], coords_df["longitude"], coords_df["rating"], coords_df["placeUrl"]):
                if get_distance_between_points_new(current_location[0],
                                                   current_location[1], 
                                                   lat, 
                                                   long) <= trip_radius:

                    
                    for g, s in zip(mahalle["geometry"], mahalle["SESDensity"]):
                        # budget check
                        #§if s == budget:
                            #contains check
                            if loads(g).contains(Point(long, lat)):
                                rout_time = routing_time(current_location[0], current_location[1], lat, long, "bike")                                                       
                                # none check
                                if rout_time != None and rout_time < avaible_time:
                                    title_pool.append([title, placeUrl, rating, lat, long])
                                    # send bike park coords
            break

    df = pd.DataFrame(title_pool, columns = ["title", "placeUrl", "rating", "lat", "long"]).sort_values("rating").iloc[-12:]
    df = df.append({'title':'Bisiklet Durağı', 'lat': bike_station[0], 'long':bike_station[1]}, ignore_index=True)

    df["path_time"] = None

    df["path_time"].iloc[-1] = routing_time(bike_station[0], bike_station[1], lat, long, "bike")
    for i in range(len(df)-1, -1, -1):
        df["path_time"].iloc[i] = routing_time(df["lat"].iloc[i-1], df["long"].iloc[i-1],
                                               df["lat"].iloc[i], df["long"].iloc[i], "bike")

    return df, bike_station



choices = ["museum", "cinema", "lunapark", "park"]
def get_positions(current_location, preferences, time, budget):
    prefs = []
    for pref in preferences:
        prefs.append(choices[pref-1])

    # return get_positions_dataframe([37.872194, 32.490857], choices, 40, "C")
    return get_positions_dataframe(current_location, prefs, time, budget)

