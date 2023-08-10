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
    [os.mkdir(s + f'\{i}') for i in data["day_numbers"]]
    return s

def paste_templates(dst, day_numbers):
    path = 'szablony/szablon_dnia.xlsx'
    for n in day_numbers:
        shutil.copy(f'{path}', f'{dst}/{n}')
        os.rename(f'{dst}/{n}/szablon_dnia.xlsx', f'{dst}/{n}/{n}.xlsx')

def generate(data):
    path = create_folder(data)
    paste_templates(path, data['day_numbers'])
    print('GENEROWANIE')
    for i in data["day_numbers"]:
        d = create_day_obj(data['days'][i], i)
        with xw.App(visible=False) as a:
            wb = a.books.open(f'{path}/{d.number}/{d.number}.xlsx')
            print(f'    DZIEN {i}')
            a = d.K['a']
            write_data(a, wb, f'ALARMY', data['campain_name'], data_cell="B2", campain_field='D1')
            for k in d.active_chambers:
                print(f'        KOMORA {k}')

                th = d.K[k]['th']
                p = d.K[k]['p']

                write_data(th, wb, f'Temp i wilg K{k}', data['campain_name'], chamber=k)
                write_data(p, wb, f'K{k}', data['campain_name'], chamber=k)

            wb.save()

    print('ZAKONCZONO')

    #    day2excel_template(d)

def write_data(df, file, sheet, campain_name, chamber=None, data_cell='A1', campain_field='J1', chamber_field='G1'):
    file.sheets(sheet).range(data_cell).value = df
    file.sheets(sheet).range(campain_field).value = campain_name
    if chamber:
        file.sheets(sheet).range(chamber_field).value = f'K{chamber}'



CHAMBERS = import_chambers()
ALARMS = alarms_dataframe()
app = App(generate)
app.mainloop()
