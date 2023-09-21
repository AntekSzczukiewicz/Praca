import pandas as pd
import os, re, pickle, tkinter, openpyxl, shutil, sys
import xlwings as xw

#ustawienie sciezki

if getattr(sys, 'frozen', False):
    dname = os.path.dirname(sys.executable)
else:
    dname = os.path.dirname(os.path.abspath(__file__))


filepath = dname + '\pliki'

print(filepath)

name_list = ["temperature", "humidity", "particle_5", "particle_0x5"]
#wczytanie nazw plikow z folderu pliki
filenames = os.listdir(filepath)

#funkcja do wczytywania alarmow
def alarms_import(path):
    df = pd.read_csv(path, sep=";", index_col=False)
    df = df[["TimeString", "Time_ms", "MsgNumber"]]
    return df

def alarms_dataframe():
    pattern = re.compile(f"^Alarm_log")
    names = [name for name in filenames if pattern.match(name)]
    dfs = [alarms_import(path = f"{filepath}/{name}") for name in names]
    if dfs:
        df = pd.concat(dfs, axis=0)
        df["TimeString"] = pd.to_datetime(df["TimeString"], format=r"%d.%m.%Y %H:%M:%S")
        return df
    return pd.DataFrame()

def incubation_import():
    try:
        df = pd.read_csv(f'{filepath}/incubation.csv', sep=";", index_col=False, skiprows=1, encoding='latin')
        df["Time[YY-MM-DD hh:mm]"] = pd.to_datetime(df["Time[YY-MM-DD hh:mm]"], format='mixed')
    except:
        df = pd.DataFrame()
    return df
    

#funkcja do importowania temperatury wilgotnosci i czastek
def data_import(path):
    df = pd.read_csv(path, sep=";", nrows=50000, index_col=False) ### USTAWIC NA 50000 ###
    df = df[["TimeString", "Time_ms", "VarValue"]]
    return df

def get_dataframe(komora, data_type):
    pattern = re.compile(f"^k{komora}_{data_type}")
    names = [name for name in filenames if pattern.match(name)]
    dfs = [data_import(path = f"{filepath}/{name}") for name in names]
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
    def __init__(self, start, stop, active_chambers, CHAMBERS, alarms, incubation, number=0):
        self.CHAMBERS = CHAMBERS
        self.alarms = alarms
        self.incubation = incubation
        self.number = number
        self.start = start
        self.stop = stop
        self.incubation_end = self.start
        self.incubation_start = None
        self.active_chambers = active_chambers
        self.K = {}
        #self.get_all_data()
        #self.analyze()

    def get_th(self, df):
        self.th = df[(df["TimeString"] >= self.start - pd.Timedelta(minutes=15)) & (df["TimeString"] <= self.stop + pd.Timedelta(minutes=15))]
        self.th.loc[:, "Temperature"] = self.th["Temperature"].apply(lambda x : float(x.replace(",", ".")))
        self.th.loc[:, "Humidity"] = self.th["Humidity"].apply(lambda x : float(x.replace(",", ".")))
        self.th.loc[:, "Time_ms"] = self.th["Time_ms"].apply(lambda x : float(x.replace(",", ".")))
        return self.th

    def get_p(self, df):
        self.p = df[(df["TimeString"] >= self.start - pd.Timedelta(minutes=15)) & (df["TimeString"] <= self.stop + pd.Timedelta(minutes=15))]
        self.p.loc[:, "Time_ms"] = self.p["Time_ms"].apply(lambda x : float(x.replace(",", ".")))
        return self.p
    
    def get_a(self):
        self.a = self.alarms[(self.alarms["TimeString"] >= self.start - pd.Timedelta(minutes=15)) & (self.alarms["TimeString"] <= self.stop + pd.Timedelta(minutes=15))]
        self.a.loc[:, "Time_ms"] = self.a["Time_ms"].apply(lambda x : float(x.replace(",", ".")))
        return self.a
    
    def get_i(self):
        if self.incubation_start:
            self.i = self.incubation[(self.incubation["Time[YY-MM-DD hh:mm]"] >= self.incubation_start) & (self.incubation["Time[YY-MM-DD hh:mm]"] <= self.incubation_end)]
            return self.i
        return pd.DataFrame()

    def get_chamber(self, K):
        return {"th" : self.get_th(K["th"]), "p" : self.get_p(K["p"])}

    def get_all_data(self):
        for k in self.active_chambers:
            self.K[k] = self.get_chamber(self.CHAMBERS[k])
        self.K["a"] = self.get_a()
        self.K["i"] = self.get_i()
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

def day_stats(day, path):
    with open(f'{path}\{day.number}.txt', 'w') as f:
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

def convert_time_ms(value):
    f = str(int(float(value.replace(",", "."))))
    return f

#zapis temperatury i wilgotnosci
def th2csv(day, path):
    for k in day.active_chambers:
        df = day.K[k]["th"]
        df.to_csv(f'{path}/{day.number}_K{k}_temperatura_i_wilgotnosc.csv', sep=";")

def th2excel(day, path):
    for k in day.active_chambers:
        df = day.K[k]["th"]
        df.to_excel(f'{path}/{day.number}_K{k}_temperatura_i_wilgotnosc.xlsx')

#zapis czastek
def p2csv(day, path):
    for k in day.active_chambers:
        df = day.K[k]["p"]
        df.to_csv(f'{path}/{day.number}_K{k}_czastki.csv', sep=";")

def p2excel(day, path):
    for k in day.active_chambers:
        df = day.K[k]["p"]
        df.to_excel(f'{path}/{day.number}_K{k}_czastki.xlsx')

def a2csv(day, path):
    df = day.a
    df.to_csv(f'{path}/{day.number}_alarmy.csv', sep=";")

def a2excel(day, path):
    df = day.a
    df.to_excel(f'{path}/{day.number}_alarmy.xlsx')

def day2excel_template(day):
    with xw.App(visible=False) as a:
        wb = a.books.open('Szablon.xlsx')      
        wb.save()

def import_chambers():
    C = {}
    print('IMPORTUJE')
    for i in [1, 2, 3, 4]:
        print(f'    KOMORA {i}')
        C[i] = import_chamber(i)
    return C

def import_all():
    C = import_chambers()
    print('    ALARMY')
    A = alarms_dataframe()
    print('    INKUBACJA')
    I = incubation_import()
    return {'Chambers' : C, 'Alarms': A, 'Incubation' : I}