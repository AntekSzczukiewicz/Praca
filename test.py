import pandas as pd
import os, re, pickle, tkinter

#ustawienie sciezki
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

name_list = ["temperature", "humidity", "particle_5", "particle_0x5"]
#wczytanie nazw plikow z folderu pliki
filenames = os.listdir('pliki/')

#funkcja do wczytywania alarmow
def alarms_import(path):
    df = pd.read_csv(path, sep=";")
    df = df[["TimeString", "Time_ms", "MsgNumber"]]
    return df

#funkcja do importowania temperatury wilgotnosci i czastek
def data_import(path):
    df = pd.read_csv(path, sep=";", nrows=50000) ### USTAWIC NA 50000 ###
    df = df[["TimeString", "Time_ms", "VarValue"]]
    return df

def get_dataframe(komora, data_type):
    pattern = re.compile(f"^k{komora}_{data_type}")
    names = [name for name in filenames if pattern.match(name)]
    print(names)
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

class Day:
    def __init__(self, start, stop, active_chambers, number=0):
        self.number = number
        self.start = start
        self.stop = stop
        self.active_chambers = active_chambers
        self.K = {}
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
            self.K[k] = self.get_chamber(CHAMBERS[k])
        return self.K

    def chamber_analyze(self, n):
        chamber = self.K[n]
        S = {}
        T = chamber["th"]["Temperature"]
        H = chamber["th"]["Humidity"]
        P = chamber["p"]["particle_5"]
        p = chamber["p"]["particle_0x5"]

        S["temp_max"] = max(T) if not T.empty else None
        S["temp_min"] = min(T) if not T.empty  else None
        S["temp_mean"] = T.mean() if not T.empty  else None

        S["hum_max"] = max(H) if not H.empty  else None
        S["hum_min"] = min(H) if not H.empty  else None
        S["hum_mean"] = H.mean() if not H.empty  else None

        S["max_5"] = max(P) if not P.empty  else None
        S["max_0x5"] = max(p) if not p.empty  else None
        self.K[n]["analysis"] = S
        return S

    def analyze(self):
        for k in self.active_chambers:
            self.chamber_analyze(k)

CHAMBERS = {1 : import_chamber(1), 2 : import_chamber(2), 3 : import_chamber(3), 4 : import_chamber(4)}
print(CHAMBERS[3]["p"])

d1 = Day(pd.Timestamp(2023, 6, 30, 11, 47), pd.Timestamp(2023, 6, 30, 12, 42), [1, 3])

#pickle.dump(d1, open('day.txt', 'wb'))

#d1 = pickle.load(open('day.txt', 'rb'))

def day_stats(day):
    with open(f'{day.number}.txt', 'w') as f:
        f.write(f'DZIEŃ {day.number}\n')
        f.write(f'{day.start} - {day.stop}\n\n')
        for k in day.active_chambers:
            f.write(f'----------K{k}----------\n')
            f.write(f'\nTEMPERATURA\n\n')
            f.write(f'max : {day.K[k]["analysis"]["temp_max"]}\n')
            f.write(f'min : {day.K[k]["analysis"]["temp_min"]}\n')
            f.write(f'średnia : {day.K[k]["analysis"]["temp_mean"]}\n')

            f.write(f'\nWILGOTNOŚĆ\n\n')
            f.write(f'max : {day.K[k]["analysis"]["hum_max"]}\n')
            f.write(f'min : {day.K[k]["analysis"]["hum_min"]}\n')
            f.write(f'średnia : {day.K[k]["analysis"]["hum_mean"]}\n')

            f.write(f'\nCZĄSTKI\n\n')
            f.write(f'max 5 : {day.K[k]["analysis"]["max_5"]}\n')
            f.write(f'max 0.5 : {day.K[k]["analysis"]["max_0x5"]}')

            f.write("\n\n")

#zapis temperatury i wilgotnosci
def th2csv(day):
    for k in day.active_chambers:
        df = day.K[k]["th"]
        df.to_csv(f'{day.number}_K{k}_temperatura_i_wilgotnosc.csv', sep=";")

#zapis czastek
def p2csv(day):
    for k in day.active_chambers:
        df = day.K[k]["p"]
        df.to_csv(f'{day.number}_K{k}_czastki.csv', sep=";")


day_stats(d1)
th2csv(d1)
p2csv(d1)