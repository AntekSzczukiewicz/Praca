import pandas as pd
import os, re, pickle, tkinter, openpyxl, shutil, sys
import xlwings as xw

#ustawienie sciezki

if getattr(sys, 'frozen', False):
    dname = os.path.dirname(sys.executable)
else:
    dname = os.path.dirname(os.path.abspath(__file__))


filepath = dname + '\pliki'

name_list = ["temperature", "humidity", "particle_5", "particle_0x5"]
#wczytanie nazw plikow z folderu pliki
filenames = os.listdir(filepath)

#funkcja do wczytywania alarmow
def alarms_import(path):
    try: 
        df = pd.read_csv(path, sep=";", index_col=False, on_bad_lines='skip')
        df = df[["TimeString", "Time_ms", "MsgNumber"]]
    except FileNotFoundError:
        df = pd.DataFrame(columns=["TimeString", "Time_ms", "MsgNumber"])
    return df

def alarms_dataframe():
    pattern = re.compile(f"^Alarm_log")
    names = [name for name in filenames if pattern.match(name)]
    dfs = [alarms_import(path = f"{filepath}/{name}") for name in names]
    if dfs:
        df = pd.concat(dfs, axis=0)
        df["TimeString"] = pd.to_datetime(df["TimeString"], format=r"%d.%m.%Y %H:%M:%S")
        return df
    return pd.DataFrame(columns=["TimeString", "Time_ms", "MsgNumber"])

def incubation_import(path):
    try:
        df = pd.read_csv(path, sep=";", index_col=False, skiprows=1, on_bad_lines='skip', encoding='unicode_escape')
        df = df.rename(columns={df.columns[0]: "Czas[YY-MM-DD hh:mm]", df.columns[1]: "PT1", df.columns[2]: "CO2"})
    except FileNotFoundError:
        df = pd.DataFrame(columns = ["Czas[YY-MM-DD hh:mm]", "PT1", "CO2"])
    return df

def incubation_dataframe():
    pattern = re.compile(f"^inkubacja")
    names = [name for name in filenames if pattern.match(name)]
    dfs = [incubation_import(path = f"{filepath}/{name}") for name in names]
    if dfs:
        df = pd.concat(dfs, axis=0)
        df["Czas[YY-MM-DD hh:mm]"] = pd.to_datetime(df["Czas[YY-MM-DD hh:mm]"], format=r"%Y-%m-%d %H:%M:%S")
        return df
    return pd.DataFrame(columns = ["Czas[YY-MM-DD hh:mm]", "PT1", "CO2"])

#funkcja do importowania temperatury wilgotnosci i czastek
def data_import(path):
    try:
        df = pd.read_csv(path, sep=";", index_col=False, on_bad_lines='skip')
        df = df[["TimeString", "Time_ms", "VarValue"]]
    except FileNotFoundError:
        df = pd.DataFrame(columns=["TimeString", "Time_ms", "VarValue"])
    return df

def get_dataframe(komora, data_type):
    pattern = re.compile(f"^k{komora}_{data_type}")
    names = [name for name in filenames if pattern.match(name)]
    dfs = [data_import(path = f"{filepath}/{name}") for name in names]
    if dfs:
        df = pd.concat(dfs, axis=0)
        return df
    return pd.DataFrame(columns=["TimeString", "Time_ms", "VarValue"])

def import_chamber(number):
    D = {}
    for name in name_list:
        D[name] = get_dataframe(number, name)
    
    if len(D[name]) > 0:
        th = pd.merge(D["temperature"], D["humidity"], on=["TimeString"], how="inner")
        th = th.rename(columns={"VarValue_x" : "Temperature", "VarValue_y" : "Humidity", "Time_ms_x" : "Time_ms"})
        th = th.drop("Time_ms_y", axis=1)

        p = pd.merge(D["particle_5"], D["particle_0x5"], on=["TimeString"], how="inner")
        p = p.rename(columns={"VarValue_x" : "particle_5", "VarValue_y" : "particle_0x5", "Time_ms_x" : "Time_ms"})
        p = p.drop("Time_ms_y", axis=1)
    else:
        th = pd.DataFrame(columns=["TimeString", "Time_ms", "Temperature", "Humidity"])
        p = pd.DataFrame(columns=["TimeString", "Time_ms", "particle_5", "particle_0x5"])

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
        self.do_incubation = False
        self.incubation_start = None
        self.incubation_stop = None
        self.active_chambers = active_chambers
        self.K = {}
        #self.get_all_data()
        #self.analyze()

    def get_th(self, df):
        self.th = df[(df["TimeString"] >= self.start) & (df["TimeString"] <= self.stop)]
        self.th.loc[:, "Temperature"] = self.th["Temperature"].apply(lambda x : float(x.replace(",", ".")))
        self.th.loc[:, "Humidity"] = self.th["Humidity"].apply(lambda x : float(x.replace(",", ".")))
        self.th.loc[:, "Time_ms"] = self.th["Time_ms"].apply(lambda x : float(x.replace(",", ".")))
        return self.th

    def get_p(self, df):
        self.p = df[(df["TimeString"] >= self.start) & (df["TimeString"] <= self.stop)]
        self.p.loc[:, "Time_ms"] = self.p["Time_ms"].apply(lambda x : float(x.replace(",", ".")))
        return self.p
    
    def get_a(self):
        self.a = self.alarms[(self.alarms["TimeString"] >= self.start) & (self.alarms["TimeString"] <= self.stop)]
        self.a.loc[:, "Time_ms"] = self.a["Time_ms"].apply(lambda x : float(x.replace(",", ".")))
        return self.a
    
    def get_i(self):
        if self.do_incubation:
            self.i = self.incubation[(self.incubation["Czas[YY-MM-DD hh:mm]"] >= self.incubation_start) & (self.incubation["Czas[YY-MM-DD hh:mm]"] <= self.incubation_stop)]
            return self.i
        return None

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
    I = incubation_dataframe()
    return {'Chambers' : C, 'Alarms': A, 'Incubation' : I}
