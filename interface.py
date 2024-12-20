import tkinter as tk
from tkcalendar import DateEntry

def counter():
    i = 1
    while True:
        yield i
        i += 1

class App(tk.Tk):
    def __init__(self, command):
        super().__init__()
        #self.geometry("500x500")
        self.counter = counter()
        self.generate_command = command
        self.DAYS = []
        self.set_things()
        self.title("Generator raportu")
        self.resizable(False, False)

    def set_things(self):
        self.days_grid = tk.Frame(self)
        self.set_title()
        self.set_product_name()
        self.set_confirm_button()
        self.set_add_day_button()
        self.set_incubation()
        self.days_grid.pack(side=tk.LEFT, padx=10, pady=10)
    
    def set_info_label(self):
        self.info = tk.StringVar()
        self.info.set('test')
        self.info_label = tk.Label(self, textvariable=self.info)
        self.info_label.pack(side=tk.BOTTOM, pady=10)

    def set_title(self):
        frame = tk.Frame(self)
        label = tk.Label(frame, text="Nazwa kampanii:")
        label.pack(side=tk.LEFT, padx=10)
        self.title_field = tk.Entry(frame, width=40, font=("Arial", 12))
        self.title_field.pack(side=tk.RIGHT, padx=10)
        frame.pack(pady=10)

    def set_product_name(self):
        frame = tk.Frame(self)
        label = tk.Label(frame, text="Nazwa produktu:")
        label.pack(side=tk.LEFT, padx=10)
        self.product_name_field = tk.Entry(frame, width=40, font=("Arial", 12))
        self.product_name_field.pack(side=tk.RIGHT, padx=10)
        frame.pack(pady=10)

    def set_incubation(self):
        self.incubation_frame = tk.Frame(self)
        frame = self.incubation_frame
        frame.pack()

        tk.Label(frame, text="Początek inkubacji: ").pack(side = tk.LEFT)

        self.incubation_start_date = DateEntry(frame, date_pattern='dd-mm-yyyy')
        self.incubation_start_date.pack(side = tk.LEFT)

        self.incubation_start_h = tk.Spinbox(frame, from_=0, to=23, wrap=True, width=2)
        self.incubation_start_h.pack(side = tk.LEFT)

        self.incubation_start_m = tk.Spinbox(frame, from_=0, to=59, wrap=True, width=2)
        self.incubation_start_m.pack(side = tk.LEFT)

        tk.Label(frame, text="Koniec inkubacji: ").pack(side = tk.LEFT)

        self.incubation_stop_date = DateEntry(frame, date_pattern='dd-mm-yyyy')
        self.incubation_stop_date.pack(side = tk.LEFT)

        self.incubation_stop_h = tk.Spinbox(frame, from_=0, to=23, wrap=True, width=2)
        self.incubation_stop_h.pack(side = tk.LEFT)

        self.incubation_stop_m = tk.Spinbox(frame, from_=0, to=59, wrap=True, width=2)
        self.incubation_stop_m.pack(side = tk.LEFT)

    def set_day(self):

        row = next(self.counter)

        frame = tk.Frame(self.days_grid)
        day = IDay(frame)
        self.DAYS.append(day)

        #numer dnia
        title = tk.Label(frame, text=f"Dzień")
        title.grid(row=0, column=0, sticky="W")
        day.number.grid(row=0, column=1, sticky="W")

        #daty
        label_date = tk.Label(frame, text="Data:")
        label_date.grid(row=1, column=0, sticky="W")
        day.date.grid(row=1, column=1, sticky="W", padx=5)

        #start
        label_start = tk.Label(frame, text="start:")
        label_start.grid(row=1, column=2, sticky="W")
        day.start_h.grid(row=1, column=3, sticky="W")
        day.start_m.grid(row=1, column=4, sticky="W")

        #stop
        label_start = tk.Label(frame, text="stop:")
        label_start.grid(row=1, column=5, sticky="W")
        day.stop_h.grid(row=1, column=6, sticky="W")
        day.stop_m.grid(row=1, column=7, sticky="W")
        
        frame.grid(row=row, column=0, pady=10)

        #komory
        day.Chamber_button[1].grid(row=1, column=8)
        day.Chamber_button[2].grid(row=1, column=9)
        day.Chamber_button[3].grid(row=1, column=10)
        day.Chamber_button[4].grid(row=1, column=11)

    def set_confirm_button(self):
        self.confirm_button = tk.Button(self, text="Generuj", command=self.generate)
        self.confirm_button.pack(side=tk.BOTTOM, anchor=tk.SE, padx=10, pady=10)

    def set_add_day_button(self):
        self.confirm_button = tk.Button(self, text="Dodaj dzień", command=self.set_day)
        self.confirm_button.pack(side=tk.BOTTOM, padx=10, pady=10)

    def get_incubation(self):
        DATA = {}

        start_date = self.incubation_start_date.get_date()
        DATA["start_Y"] = int(start_date.year)
        DATA["start_M"] = int(start_date.month)
        DATA["start_D"] = int(start_date.day)

        stop_date = self.incubation_stop_date.get_date()
        DATA["stop_Y"] = int(stop_date.year)
        DATA["stop_M"] = int(stop_date.month)
        DATA["stop_D"] = int(stop_date.day)

        #godziny
        DATA["start_h"] = int(self.incubation_start_h.get())
        DATA["start_m"] = int(self.incubation_start_m.get())
        DATA["stop_h"] = int(self.incubation_stop_h.get())
        DATA["stop_m"] = int(self.incubation_stop_m.get())

        return DATA



    def get_day(self, day):
        DATA = {}
        
        #numer
        DATA['number'] = day.number.get()

        #data
        date = day.date.get_date()
        DATA["Y"] = int(date.year)
        DATA["m"] = int(date.month)
        DATA["d"] = int(date.day)

        #godziny
        DATA["start_h"] = int(day.start_h.get())
        DATA["start_m"] = int(day.start_m.get())
        DATA["stop_h"] = int(day.stop_h.get())
        DATA["stop_m"] = int(day.stop_m.get())

        #komory
        DATA["chambers"] = []
        for k in day.Chambers.keys():
            if day.Chambers[k].get():
                DATA["chambers"].append(k)

        return DATA

    def get(self):
        self.DATA = {'days' : {}}
        for day in self.DAYS:
            data = self.get_day(day)
            self.DATA['days'][int(data['number'])] = data 

        cn = self.title_field.get()
        self.DATA["campain_name"] = cn if cn else "bez nazwy"
        self.DATA["product_name"] = self.product_name_field.get()
        
        day_nums = list(self.DATA["days"].keys())
        day_nums.sort()
        self.DATA['day_numbers'] = day_nums

        self.DATA['incubation'] = self.get_incubation()

    def generate(self):
        self.get()
        self.generate_command(self.DATA)
            


class IDay():
    def __init__(self, frame):
        self.frame = frame
        self.number = tk.Spinbox(frame, from_=0, to=23, wrap=True, width=2)
        self.date = DateEntry(frame, date_pattern='dd-mm-yyyy')
        self.start_h = tk.Spinbox(frame, from_=0, to=23, wrap=True, width=2)
        self.start_m = tk.Spinbox(frame, from_=0, to=59, wrap=True, width=2)

        self.stop_h = tk.Spinbox(frame, from_=0, to=23, wrap=True, width=2)
        self.stop_m = tk.Spinbox(frame, from_=0, to=59, wrap=True, width=2)

        self.Chambers = {i : tk.IntVar() for i in [1, 2, 3, 4]}
        self.Chamber_button = {i : tk.Checkbutton(frame, text=f"K{i}", variable=self.Chambers[i]) for i in [1, 2, 3, 4]}

