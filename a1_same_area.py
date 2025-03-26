import pandas as pd
from haversine import haversine, Unit
from datetime import datetime
import csv

df = pd.read_csv("location.csv", header=None)

df.rename(columns={0: "ind",
                   1: "Date_time",
                    2: "MMSI",
                    3: "Latitude",
                    4: "Longitude",
                    5: "SOG",
                    6: "COG",
                    7: "speed_m_per_s",
                    8: "Delta_t",
                    9: "Delta_s",
                    10: "Delta_v",
                    11: "Spoofing"}, inplace=True)

# print(df.head())
# df["Date_time"] = pd.to_datetime(df["Date_time"], dayfirst=True)
df.sort_values("Date_time", inplace=True)
print(df.head())

# thresholds
meters = 10 * 1852 # nm to meters
time = 5 * 60 # minutes to seconds

# df = df[0:100]

overlapping_ships = []

def time_differene(time1, time2):
    time_format = "%Y-%m-%d %H:%M:%S"
    t1 = datetime.strptime(time1, time_format)
    t2 = datetime.strptime(time2, time_format)
    return abs((t1 - t2).total_seconds())




row_count = len(df)
for i in range(0, row_count):
    row = df.iloc[[i]]
    # print(row)
    if i == row_count:
         continue # skip last
    
    lat1, lon1 = row["Latitude"].values[0], row["Longitude"].values[0]
    time1 = row["Date_time"].values[0]

    for j in range(i + 1, row_count):
        other_row = df.iloc[[j]]
        if row["MMSI"].values[0] == other_row["MMSI"].values[0]:
            continue

        time_diff = time_differene(other_row["Date_time"].values[0], row["Date_time"].values[0])
        if time_diff > time:
            break

        lat2, lon2 = other_row["Latitude"].values[0], other_row["Longitude"].values[0]
        time2 = other_row["Date_time"].values[0]

        loc_diff = haversine((lat1, lon1), (lat2, lon2), unit=Unit.METERS)

        if loc_diff < meters:
            overlapping_ships.append([row["MMSI"].values[0], lat1, lon1, other_row["MMSI"].values[0], lat2, lon2])
        # print(time_diff)




with open("overlapping_ships.csv", "w", newline="") as f:
        write = csv.writer(f)
        write.writerows(overlapping_ships)