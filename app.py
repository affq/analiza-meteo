import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from pymongo import MongoClient

def wybierz_date():
    wybrana_data = kalendarz.get_date()
    label.config(text=f"Wybrana data: {wybrana_data}")

def pobierz_wojewodztwa():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["pag"]
    kolekcja = db["stations"]
    wojewodztwa = kolekcja.distinct("wojewodztwo")
    powiaty = kolekcja.distinct("powiat")
    client.close()
    return powiaty, wojewodztwa

def wybierz_wojewodztwo(value):
    label_wojewodztwo.config(text=f"Wybrane województwo: {value}")

root = tk.Tk()
root.title("Hello World")

# Kalendarz
kalendarz = Calendar(root, selectmode='day', year=2024, month=10, day=1)
kalendarz.pack(pady=20)

# Przycisk wyboru daty
button = tk.Button(root, text="Wybierz datę", command=wybierz_date)
button.pack(pady=10)

# Etykieta wyświetlająca wybraną datę
label = tk.Label(root, text="")
label.pack(pady=10)

# Pobranie województw z bazy MongoDB
powiaty, wojewodztwa = pobierz_wojewodztwa()

# Lista rozwijana dla województw
label = tk.Label(root, text="Wybierz województwo:")
label.pack(pady=10)

# Zmienna do przechowywania wybranego województwa
selected_wojewodztwo = tk.StringVar(value="Wybierz")
dropdown = ttk.Combobox(root, textvariable=selected_wojewodztwo, values=wojewodztwa, state="readonly")
dropdown.pack(pady=10)

# Obsługa wyboru województwa
dropdown.bind("<<ComboboxSelected>>", lambda event: wybierz_wojewodztwo(selected_wojewodztwo.get()))

# Etykieta wyświetlająca wybrane województwo
label_wojewodztwo = tk.Label(root, text="")
label_wojewodztwo.pack(pady=10)

root.mainloop()