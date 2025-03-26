import pathlib
from timer_wraper import timeit
import multiprocessing as mp
import pandas as pd
import polars as pl
import csv

df = pd.read_csv("aisdk-2025-01-23.csv")

mmsi = pd.unique(df["MMSI"])
mmsi_df = pd.DataFrame(mmsi, columns=["MMSI"])
mmsi_df.to_csv("mmsi.csv", index=False, header=False)

#-------------------------
# df = pl.read_csv("aisdk-2025-01-20.csv", columns=["# Timestamp","MMSI", "Latitude", "Longitude"])
# mmsi = df.unique(subset = ["MMSI"], maintain_order=True)
# mmsi = mmsi["MMSI"].to_list()
# print(mmsi["MMSI"].to_list())
# print(type(mmsi["MMSI"].to_list()))
# print(len(mmsi["MMSI"].to_list()))

#-------------------------

# file = open("mmsi.csv", "r")
# mmsi = list(csv.reader(file))
# file.close()
# print(mmsi)
# mmsi = [int(i) for x in mmsi for i in x]
# print(mmsi)



# print(mmsi)

# print(len(mmsi))

def create_subfiles(mmsi, df):
    vessel = df.filter(pl.col("MMSI") == mmsi)

    vessels_dir = pathlib.Path("vessels")
    vessels_dir.mkdir(exist_ok=True)

    vessel.write_csv(vessels_dir / f"vessel_{mmsi}.csv")



# Function do_parallel Took 319.0905 seconds (4516 files total)
# @timeit
# def do_parallel():
#     df = pl.read_csv("aisdk-2025-01-23.csv", columns=["# Timestamp","MMSI", "Latitude", "Longitude"])
#     with open("mmsi.csv", "r") as file:
#         mmsi = [int(row[0]) for row in csv.reader(file)]
    
#     # mmsi = df.unique(subset = ["MMSI"], maintain_order=True)
#     # mmsi = mmsi["MMSI"].to_list()

#     workers = mp.cpu_count() - 1
#     pool = mp.Pool(workers)

#     lst = [(mmsi[i], df) for i in range(len(mmsi))]
#     pool.starmap(create_subfiles, lst)
#     pool.close()

@timeit
def do_sequential():
    df = pl.read_csv("aisdk-2025-01-23.csv", columns=["# Timestamp","MMSI", "Latitude", "Longitude", "SOG", "COG"])
    with open("mmsi.csv", "r") as file:
        mmsi = [int(row[0]) for row in csv.reader(file)]
    for i in mmsi:
        create_subfiles(i, df)

if __name__ == '__main__':
    # do_parallel()
    do_sequential()