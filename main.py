from interface import *
from generator import *

def create_day_obj(data, n):
    Y = data["Y"]
    m = data["m"]
    d = data["d"]
    d = Day(pd.Timestamp(Y, m, d, data["start_h"], data["start_m"]), pd.Timestamp(Y, m, d, data["stop_h"], data["stop_m"]), data["chambers"], CHAMBERS, ALARMS, number=n)
    return d

def create_folder(data):
    s = data["campain_name"]
    s = s.replace('/', '-')
    s = s.replace('\\', '-')
    while os.path.isdir(s):
        s += '_'
    os.mkdir(s)
    [os.mkdir(s + f'\{i}') for i in DAY_NUMBERS]
    return s

def generate(data):
    path = create_folder(data)
    for i in DAY_NUMBERS:
        d = create_day_obj(data[i], i)
        #p2csv(d, f"{path}/{d.number}")
        p2excel(d, f"{path}/{d.number}")
        #th2csv(d, f"{path}/{d.number}")
        th2excel(d, f"{path}/{d.number}")
        #a2csv(d, f"{path}/{d.number}")
        a2excel(d, f"{path}/{d.number}")
        day_stats(d, f"{path}/{d.number}")

CHAMBERS = import_chambers()
ALARMS = alarms_dataframe()
app = App(generate)
app.mainloop()
