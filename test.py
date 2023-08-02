import pandas as pd
import os, re
import time

import time

name_list = ["temperature", "humidity", "particle_5", "particle_0x5"]

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

def data_import(path):
    df = pd.read_csv(path, sep=";", nrows=50000) ### USTAWIC NA 50000 ###
    df = df.drop("VarName", axis=1)
    df = df.drop("Validity", axis=1)

    df = df[["TimeString", "Time_ms", "VarValue"]]
    return df

#wczytanie nazw plikow z folderu pliki
filenames = os.listdir('pliki/')

def get_dataframe(komora, data_type):
    pattern = re.compile(f"k{komora}_{data_type}*")
    names = [name for name in filenames if pattern.match(name)]
    dfs = [data_import(path = f"pliki/{name}") for name in names]
    if dfs:
        df = pd.concat(dfs, axis=0)
        #konwertowanie TYLKO DATA
        #df["TimeString"] = pd.to_datetime(df["TimeString"], format=r"%d.%m.%Y %H:%M:%S")
        return df
    return pd.DataFrame()

def import_chamber(number):
    D = {}
    for n in name_list:
        D[n] = get_dataframe(number, n)
    
    th = pd.merge(D["temperature"], D["humidity"], on=["TimeString"], how="inner")
    th = th.rename(columns={"VarValue_x" : "Temperature", "VarValue_y" : "Humidity", "Time_ms_x" : "Time_ms"})
    th = th.drop("Time_ms_y", axis=1)

    p = pd.merge(D["particle_5"], D["particle_0x5"], on=["TimeString"], how="inner")
    p = p.rename(columns={"VarValue_x" : "particle_5", "VarValue_y" : "particle_0x5", "Time_ms_x" : "Time_ms"})
    p = p.drop("Time_ms_y", axis=1)

    th["TimeString"] = pd.to_datetime(th["TimeString"], format=r"%d.%m.%Y %H:%M:%S")
    p["TimeString"] = pd.to_datetime(p["TimeString"], format=r"%d.%m.%Y %H:%M:%S")

    RD = {"th" : th, "p" : p}
    return RD

#Filtrowanie warunkiem
K1 = import_chamber(1)
th = K1["th"]

print(th[(th["TimeString"] >= pd.Timestamp(2023, 7, 28, 10, 40))])

class Day:
    def __init__(self, start, stop):
        self.start = start
        self.stop = stop

    def show(self, df):
        return df[(df["TimeString"] >= self.start) & (df["TimeString"] <= self.stop)]
    
d1 = Day(pd.Timestamp(2023, 7, 28, 10, 40), pd.Timestamp(2023, 7, 28, 10, 43))
d1.show(th)