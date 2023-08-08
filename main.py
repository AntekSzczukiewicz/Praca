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

def paste_templates(dst):
    path = 'szablony'
    names = os.listdir(path)
    for name in names:
        for n in DAY_NUMBERS:
            shutil.copy(f'{path}/{name}', f'{dst}/{n}')

def generate(data):
    path = create_folder(data)
    paste_templates(path)
    for i in DAY_NUMBERS:
        d = create_day_obj(data[i], i)
        for k in d.active_chambers:
            th = d.K[k]['th']

            with xw.App(visible=False) as a:
                wb = a.books.open(f'{path}/{d.number}/szablon_dnia.xlsx')
                wb.sheets(f'TW{k}').range('A1').value = th
                wb.save()

    #    day2excel_template(d)

CHAMBERS = import_chambers()
ALARMS = alarms_dataframe()
app = App(generate)
app.mainloop()
