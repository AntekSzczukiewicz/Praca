from interface import *
from generator import *
import sys



if getattr(sys, 'frozen', False):
    dname = os.path.dirname(sys.executable)
else:
    dname = os.path.dirname(os.path.abspath(__file__))

templatepath = dname + '\szablony'

def create_day_obj(data, n):
    Y = data["Y"]
    m = data["m"]
    d = data["d"]
    d = Day(pd.Timestamp(Y, m, d, data["start_h"], data["start_m"]), pd.Timestamp(Y, m, d, data["stop_h"], data["stop_m"]), data["chambers"], CHAMBERS, ALARMS, INCUBATION, number=n)
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
    path = f'{templatepath}/szablon_dnia.xlsx'
    for n in day_numbers:
        shutil.copy(f'{path}', f'{dst}/{n}')
        os.rename(f'{dname}/{dst}/{n}/szablon_dnia.xlsx', f'{dst}/{n}/{n}.xlsx')
def generate(data):
    path = create_folder(data)
    paste_templates(path, data['day_numbers'])
    print('GENEROWANIE')
    last = None
    for i in data["day_numbers"]:
        d = create_day_obj(data['days'][i], i)
        if last:
            d.incubation_start = last.stop
        
        d.get_all_data()
        with xw.App(visible=False) as app:
            wb = app.books.open(f'{path}/{d.number}/{d.number}.xlsx')
            print(f'    DZIEN {i}')
            a = d.K['a']
            if not a.empty:
                a = a.rename(columns={'MsgNumber' : 'Nr alarmu'})
                write_data(a, wb, f'ALARMY', data['campain_name'], data_cell="A2", campain_field='D1')
            
            i = d.K['i']
            if not i.empty:
                i = i.rename(columns={i.columns.values[0] : 'Data i godzina', i.columns.values[1] : 'Temp', i.columns.values[2] : 'CO2'})
            #    i.columns.values[0] = 'Data i godzina'
            #    i.columns.values[1] = 'Temp'
            #    i.columns.values[2] = 'CO2'
                write_data(i, wb, f'INKUBACJA', data['campain_name'], data_cell="A3", campain_field='C1')
            for k in d.active_chambers:
                print(f'        KOMORA {k}')
                th = d.K[k]['th']
                th = th.rename(columns={'TimeString' : 'Data i godzina', 'Temperature' : 'Temperatura', 'Humidity' : 'Wilgotność'})
                
                p = d.K[k]['p']
                p = p.rename(columns={'TimeString' : 'Data i godzina', 'particle_5' : 'Cząstki 5um', 'particle_0x5' : 'Cząstki 0,5um'})
                
                write_data(th, wb, f'Temp i wilg K{k}', data['campain_name'], chamber=k)
                write_data(p, wb, f'K{k}', data['campain_name'], chamber=k)
            wb.save()
            last = d
    print('ZAKONCZONO')
    #    day2excel_template(d)
def write_data(df, file, sheet, campain_name, chamber=None, data_cell='A1', campain_field='J1', chamber_field='G1'):
    file.sheets(sheet).range(data_cell).value = df
    file.sheets(sheet).range(campain_field).value = campain_name
    if chamber:
        file.sheets(sheet).range(chamber_field).value = f'K{chamber}'
D = import_all()
CHAMBERS = D['Chambers']
ALARMS = D['Alarms']
INCUBATION = D['Incubation']
print(INCUBATION)
app = App(generate)
app.mainloop()
