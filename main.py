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
    print('GENEROWANIE')
    for i in DAY_NUMBERS:
        d = create_day_obj(data[i], i)
        with xw.App(visible=False) as a:
            wb = a.books.open(f'{path}/{d.number}/szablon_dnia.xlsx')
            print(f'    DZIEN {i}')
            a = d.K['a']
            write_data(a, wb, f'ALARMY', data['campain_name'], data['product_name'])
            for k in d.active_chambers:
                print(f'        KOMORA {k}')

                th = d.K[k]['th']
                p = d.K[k]['p']

                write_data(th, wb, f'TW{k}', data['campain_name'], data['product_name'])
                write_data(p, wb, f'K{k}', data['campain_name'], data['product_name'])

                #wb.sheets(f'TW{k}').range('A3').value = th
                #wb.sheets(f'TW{k}').range('B1').value = data['campain_name']
                #wb.sheets(f'TW{k}').range('B2').value = data['product_name']
#
                #wb.sheets(f'K{k}').range('A3').value = p
                #wb.sheets(f'K{k}').range('B1').value = data['campain_name']
                #wb.sheets(f'K{k}').range('B2').value = data['product_name']

            wb.save()

    print('ZAKONCZONO')

    #    day2excel_template(d)

def write_data(df, file, sheet, campain_name, product_name, data_cell='A3', campain_field='B1', product_field='B2'):
    file.sheets(sheet).range(data_cell).value = df
    file.sheets(sheet).range(campain_field).value = campain_name
    file.sheets(sheet).range(product_field).value = product_name


CHAMBERS = import_chambers()
ALARMS = alarms_dataframe()
app = App(generate)
app.mainloop()
