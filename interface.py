import tkinter as tk
from tkcalendar import DateEntry
DAY_NUMBERS = [0, 3, 6, 9, 13, 14]
#Nazwa kampani - campain_name

class App(tk.Tk):
    def __init__(self, command):
        super().__init__()
        #self.geometry("500x500")
        self.generate_command = command
        self.day_nums = DAY_NUMBERS
        self.DAY = {}
        self.set_things()
        self.title("Generator raportu")
        self.resizable(False, False)

    def set_things(self):
        days_grid = tk.Frame(self)
        self.set_title()
        self.set_product_name()
        for i in self.day_nums:
            self.set_day(i, days_grid, i)
        days_grid.pack(side=tk.LEFT, padx=10, pady=10)
        self.set_confirm_button()

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

    def set_day(self, number, days_grid, row):
        frame = tk.Frame(days_grid)
        day = IDay(frame, number)
        self.DAY[number] = day

        #numer dnia
        title = tk.Label(frame, text=f"Dzień {day.number}")
        title.grid(row=0, column=0, sticky="W")

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
        self.confirm_button = tk.Button(self, text="Dodaj dzień", command=self.generate)
        self.confirm_button.pack(side=tk.BOTTOM, padx=10, pady=10)

    def get_day(self, number):
        day = self.DAY[number]
        DATA = {}
        
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
        self.DATA = {}
        for n in self.day_nums:
            self.DATA[n] = self.get_day(n)

        self.DATA["campain_name"] = self.title_field.get()
        self.DATA["product_name"] = self.product_name_field.get()

    def generate(self):
        self.get()
        self.generate_command(self.DATA)
            


class IDay():
    def __init__(self, frame, number):
        self.frame = frame
        self.number = number
        self.date = DateEntry(frame, date_pattern='dd-mm-yyyy')
        self.start_h = tk.Spinbox(frame, from_=0, to=23, wrap=True, width=2)
        self.start_m = tk.Spinbox(frame, from_=0, to=59, wrap=True, width=2)

        self.stop_h = tk.Spinbox(frame, from_=0, to=23, wrap=True, width=2)
        self.stop_m = tk.Spinbox(frame, from_=0, to=59, wrap=True, width=2)

        self.Chambers = {i : tk.IntVar() for i in [1, 2, 3, 4]}
        self.Chamber_button = {i : tk.Checkbutton(frame, text=f"K{i}", variable=self.Chambers[i]) for i in [1, 2, 3, 4]}