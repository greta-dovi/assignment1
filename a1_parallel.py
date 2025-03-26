import pathlib
import pandas as pd
import a1_functions as a1
from timer_wraper import timeit
import multiprocess as mp


def do_the_work(filename):
    df = pd.read_csv(filename)
    df_sub = a1.data_prep(df)
    df_sub = a1.delta_t_s(df_sub)

    location_jump_df = a1.detect_location_jump(df_sub)
    speed_jump_df = a1.inconsistent_speed(df_sub)

    return location_jump_df, speed_jump_df


@timeit
def do_sequential():
    p = pathlib.Path("vessels")
    file_list = [x.name for x in p.glob("*.csv") if x.is_file()]
    dir_list = [p / x for x in file_list]

    problems = []
    for filename in dir_list:
        loc, speed = do_the_work(filename)
        problems.append((loc, speed))

    with open("location1.csv", "w") as f1, open("speed1.csv", "w") as f2:
        for loc_df, sp_df in problems:
            loc_df.to_csv(f1, header=False, lineterminator='\n')
            sp_df.to_csv(f2, header=False, lineterminator='\n')    


@timeit
def do_parallel():
    p = pathlib.Path("vessels")
    file_list = [x.name for x in p.glob("*.csv") if x.is_file()]
    # file_list = [x.name for x in p.glob("*vessel_63601*.csv") if x.is_file()]
    dir_list = [p / x for x in file_list]

    workers = mp.cpu_count() - 1
    with mp.Pool(workers) as pool:
        problems = pool.map(do_the_work, dir_list) # [(dataframe, dataframe), (dataframe, dataframe)]

    with open("location.csv", "w") as f1, open("speed.csv", "w") as f2:
        for loc_df, sp_df in problems:
            loc_df.to_csv(f1, header=False, lineterminator='\n')
            sp_df.to_csv(f2, header=False, lineterminator='\n')



if __name__ == "__main__":
    # do_sequential()
    do_parallel()