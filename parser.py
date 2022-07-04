import pandas as pd

datas=["cinema", "lunapark", "museum", "park"]

for d in datas:
    data = pd.read_json(f"./Data/{d}.json")
    urls = data["placeUrl"]

    for url, i in zip(urls, range(len(urls))):
        lat1, lat2 = url.index("!3d")+3, url.index("!4d")
        long1, long2 = lat2+3, url.index("!16")
        data["latitude"].iloc[i], data["longitude"].iloc[i] = url[lat1:lat2], url[long1:long2]
        data.to_json(f"./Data/{d}.json")