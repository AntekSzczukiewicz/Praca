import pandas as pd
import os, re
import time

#ustawienie sciezki
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

name_list = ["temperature", "humidity", "particle_5", "particle_0x5"]
#wczytanie nazw plikow z folderu pliki
filenames = os.listdir('pliki/')

def data_import(path):
    df = pd.read_csv(path, sep=";", nrows=50000) ### USTAWIC NA 50000 ###
    df = df.drop("VarName", axis=1)
    df = df.drop("Validity", axis=1)

    df = df[["TimeString", "Time_ms", "VarValue"]]
    return df




def get_dataframe(komora, data_type):
    pattern = re.compile(f"^k{komora}_{data_type}")
    names = [name for name in filenames if pattern.match(name)]
    dfs = [data_import(path = f"pliki/{name}") for name in names]
    if dfs:
        df = pd.concat(dfs, axis=0)
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

CHAMBERS = {1 : import_chamber(1), 2 : import_chamber(2), 3 : import_chamber(3), 4 : import_chamber(4)}

class Day:
    #TH 
    def __init__(self, start, stop, active_chambers):
        self.start = start
        self.stop = stop
        self.active_chambers = active_chambers
        self.D = {}
        self.get_all_data()
        self.analyze()

    def get_th(self, df):
        self.th = df[(df["TimeString"] >= self.start) & (df["TimeString"] <= self.stop)]
        self.th.loc[:, "Temperature"] = self.th["Temperature"].apply(lambda x : float(x.replace(",", ".")))
        self.th.loc[:, "Humidity"] = self.th["Humidity"].apply(lambda x : float(x.replace(",", ".")))
        return self.th

    def get_p(self, df):
        self.p = df[(df["TimeString"] >= self.start) & (df["TimeString"] <= self.stop)]
        return self.p

    def get_chamber(self, K):
        return {"th" : self.get_th(K["th"]), "p" : self.get_p(K["p"])}

    def get_all_data(self):
        for k in self.active_chambers:
            self.D[k] = self.get_chamber(CHAMBERS[1])
        return self.D

    def chamber_analyze(self, n):
        chamber = self.D[n]
        S = {}
        S["temp_max"] = max(chamber["th"]["Temperature"])
        S["temp_min"] = min(chamber["th"]["Temperature"])
        S["temp_mean"] = chamber["th"]["Temperature"].mean()

        S["hum_max"] = max(chamber["th"]["Humidity"])
        S["hum_min"] = min(chamber["th"]["Humidity"])
        S["hum_mean"] = chamber["th"]["Humidity"].mean()

        S["max_5"] = max(chamber["p"]["particle_5"])
        S["max_0x5"] = max(chamber["p"]["particle_0x5"])
        self.D[n]["analysis"] = S
        return S

    def analyze(self):
        for k in self.D.keys():
            self.chamber_analyze(k)

d1 = Day(pd.Timestamp(2023, 7, 14, 12, 25), pd.Timestamp(2023, 7, 14, 12, 55), [1, 2, 3, 4])

print(d1.D)