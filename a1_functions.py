import pandas as pd
import numpy as np
from haversine import haversine, Unit



def data_prep(df: pd.DataFrame):
    """Input - sub-dataframe, containing only one vessel"""
    df.rename(columns={"# Timestamp": "Date_time"}, inplace=True)
    df["Date_time"] = pd.to_datetime(df["Date_time"], dayfirst=True)
    df.sort_values("Date_time", inplace=True)

    df.drop(df[df.Latitude.abs() > 90].index, inplace=True)
    df.drop(df[df.Longitude.abs() > 180].index, inplace=True)
    # df.drop_duplicates(subset=["Date_time", "Latitude", "Longitude"], inplace=True)
    df.drop_duplicates(subset=["Date_time"], inplace=True)

    df.dropna(inplace=True)
    
    return df


def delta_t_s(df: pd.DataFrame):
    """Pandas dataframe, with only one vessel. Must contain 
    Date_time, Latitude and Longitude"""
    if df is None or df.empty:
        return pd.DataFrame() # return empty
    
    df["speed_m_per_s"] = df["SOG"] * 0.51444 # Converting knots to meters per second

    date_time = df["Date_time"].to_numpy()
    latitudes = df["Latitude"].to_numpy()
    longitudes = df["Longitude"].to_numpy()
    speed = df["speed_m_per_s"].to_numpy()

    delta_t = np.diff(date_time).astype("timedelta64[s]").astype(float)
    delta_t = np.insert(delta_t, 0, np.nan)

    delta_v = np.diff(speed).astype("float")
    delta_v = np.insert(delta_v, 0, np.nan)

    delta_s = np.full(len(latitudes), np.nan)
    for i in range(1, len(latitudes)):
        delta_s[i] = haversine((latitudes[i - 1], longitudes[i - 1]), (latitudes[i], longitudes[i]), unit=Unit.METERS)

    df["Delta_t"] = delta_t.tolist()
    df["Delta_s"] = delta_s.tolist()
    df["Delta_v"] = delta_v.tolist()

    return df



def predict_next_position(lon, lat, speed, course, time_diff):
    """
    Predict next (lon, lat) given previous speed (m/s), course (degrees), and time_diff (s)
    """
    R = 6371000  # Earth radius in m
    delta_distance = speed * time_diff 

    course_rad = np.radians(course)

    # Calculate new lat/lon using haversine formula approximation
    new_lat = lat + (delta_distance / R) * np.cos(course_rad) * (180 / np.pi)
    new_lon = lon + (delta_distance / (R * np.cos(np.radians(lat)))) * np.sin(course_rad) * (180 / np.pi)

    return new_lat, new_lon



def detect_location_jump(df: pd.DataFrame):
    if df is None or df.empty:
        return pd.DataFrame() # return empty

    df["Spoofing"] = False
    longitude = df["Longitude"].to_numpy()
    latitude = df["Latitude"].to_numpy()
    speed_m_per_s = df["speed_m_per_s"].to_numpy()
    cog = df["COG"].to_numpy()
    delta_t = df["Delta_t"].to_numpy()

    lst = []
    for i in range(1, len(longitude)): # skipping first row
        pred_lat, pred_lon = predict_next_position(
            longitude[i-1],
            latitude[i-1],
            speed_m_per_s[i-1],
            cog[i-1],
            delta_t[i]
        )
        difference = haversine((pred_lat, pred_lon), (latitude[i], longitude[i]), unit=Unit.METERS)
        if difference > 1000:
            lst.append(i)
    
    df.loc[df.index[lst], 'Spoofing'] = True
        

    df_spoof = df[df["Spoofing"] == True]

    if df_spoof.empty:
        return pd.DataFrame()

    return df_spoof




def inconsistent_speed(df: pd.DataFrame):
    if df is None or df.empty:
        return pd.DataFrame() # return empty
    
    df["inconsistent_acceleration"] = False
    speed = df["Delta_v"].to_numpy()
    time = df["Delta_t"].to_numpy()
    # speed_diff = np.gradient(speed) 
    # acceleration = speed_diff / time # m/s²
    acceleration = speed / time
    acceleration[np.isnan(acceleration)] = 0 
    acceleration[np.isinf(acceleration)] = 0 
    speed_jump = np.where(np.abs(acceleration) > 5)[0]
    for i in speed_jump:
        df.loc[df.index[i], "inconsistent_acceleration"] = True
    
    df_speed = df[df["inconsistent_acceleration"] == True]

    if df_speed.empty:
        return pd.DataFrame()

    return df_speed

