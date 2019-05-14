import pandas as pd
import numpy as np
import gpxpy
import json


def read_gpx(gpx_file):
    lats = []
    lons = []
    Heights = []
    timestamps = []

    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:

                lats.append(point.latitude)
                lons.append(point.longitude)
                timestamps.append(point.time)


    df = pd.DataFrame()
    df['longitude'] = lons
    df['latitude'] = lats
    df['starttime'] = timestamps
    df['stoptime'] = df['starttime'].shift(-1).fillna(method = 'ffill')
    df['duration'] = (df['stoptime'] - df['starttime'])/np.timedelta64(1,'s')

    return df


def create_czml_path(df_input, relative_elevation=False):
    results = []

    timestep = 0

    for i in df_input.index:
        results.append(timestep)
        results.append(df_input.longitude.ix[i])
        results.append(df_input.latitude.ix[i])

        if relative_elevation == True:
            results.append(10)  # for use with point = {"heightReference" : "RELATIVE_TO_GROUND"}
        else:
            results.append(df_input.elevation.ix[i])

        duration = df_input.duration.ix[(i)]
        timestep += duration

    return results



def generateCZML(df, time_multiplier=2):

    czml_output=[]

    global_starttime = str(min(df['starttime'])).replace(" ","T").replace("+00:00","Z")
    global_stoptime = str(max(df['stoptime'])).replace(" ","T").replace("+00:00","Z")
    global_availability = global_starttime + "/" + global_stoptime

    global_element = {
        "id": "document",
        "name": "Visualizing GPX data from SUMO",
        "version": "1.0",
        "author": "Kangle Li",
        "clock": {
            "interval" : global_availability,
            "currentTime": global_starttime,
            "multiplier": time_multiplier
        }
    }
    czml_output.append(global_element)

    point_id = "Point"
    point_object = {
        "id": point_id,
        "availability":  global_availability,
        "position":{
            "epoch": global_starttime,
            "cartographicDegrees": create_czml_path(df, relative_elevation = True)
        },
        "point": {
            "color":{ "rgba": [255,255,255,255]},
            "outlineColor": {"rgba": [0,173,253,255]},
            "outlineWidth":6,
            "pixelSize":8,
            "heightReference": "RELATIVE_TO_GROUND"
        }
    }
    czml_output.append(point_object)

    return czml_output


# main function
print('Start to parse the GPX file and convert it to the CZML file:\n')
gpx_file = open('C:\Eclipse\Sumo\kangle_demos\innenstadt_ignore_fcd\gpxoutput_geo.xml', 'r')
gpx = gpxpy.parse(gpx_file)
print(type(gpx))
df = read_gpx(gpx)
#print(df.tail(10))
#print(df.shape)
czml_output = generateCZML(df)
with open('C:\Projects\GPXtoCZML_demo\CZMLfromSUMO_date1.czml', 'w') as outfile:
    json.dump(czml_output, outfile)
print('End of parse and convert.\n')
