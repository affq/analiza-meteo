import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from pymongo import MongoClient
import math
from redis import Redis
from redis.commands.timeseries import TimeSeries
from datetime import datetime, timedelta
from PIL import Image, ImageTk

def polacz_z_redis():
    r = Redis(host='localhost', port=6380, db=0)
    ts = TimeSeries(r)
    return ts

def polacz_z_mongo():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["pag"]
    return client, db

def wybierz_date():
    selected_date = kalendarz.get_date()
    wybierz_wojewodztwo_label.config(text=f"Wybrana data: {selected_date}")

def pobierz_wojewodztwa():
    client, db = polacz_z_mongo()
    wojewodztwa = db.stations.distinct("wojewodztwo")
    wojewodztwa = [w for w in wojewodztwa if not (isinstance(w, float) and math.isnan(w))]
    powiaty = db.stations.distinct("powiat")
    powiaty  = [p for p in powiaty if not (isinstance(p, float) and math.isnan(p))]
    client.close()
    return powiaty, wojewodztwa

def wybierz_wojewodztwo(value):
    client, db = polacz_z_mongo()
    powiaty_w_wojewodztwie = db.stations.distinct("powiat", {"wojewodztwo": value})
    powiat_dropdown["values"] = powiaty_w_wojewodztwie
    selected_powiat.set("Wybierz")
    client.close()

def wybierz_powiat(value):
    client, db = polacz_z_mongo()
    wojewodztwo_powiatu = db.stations.find_one({"powiat": value})["wojewodztwo"]
    selected_wojewodztwo.set(wojewodztwo_powiatu)
    client.close()

def wybierz_stacje_powiatu(value):
    client, db = polacz_z_mongo()
    stacje = db.stations.find({"powiat": value})
    stacje = [s["_id"] for s in stacje]
    client.close()
    return stacje

def wybierz_stacje_wojewodztwa(value):
    client, db = polacz_z_mongo()
    stacje = db.stations.find({"wojewodztwo": value})
    stacje = [s["_id"] for s in stacje]
    client.close()
    return stacje

pomiary = ["B00202A", "B00300S", "B00305A", "B00604S", "B00606S", "B00608S", "B00702A", "B00703A", "B00714A", "B00802A"]

def licz_powiat():
    stacje = wybierz_stacje_powiatu(selected_powiat.get())

    dane_dzien = {
        'B00202A': [],
        'B00300S': [],
        'B00305A': [],
        'B00604S': [],
        'B00606S': [],
        'B00608S': [],
        'B00702A': [],
        'B00703A': [],
        'B00714A': [],
        'B00802A': []
    }

    dane_noc = {
        'B00202A': [],
        'B00300S': [],
        'B00305A': [],
        'B00604S': [],
        'B00606S': [],
        'B00608S': [],
        'B00702A': [],
        'B00703A': [],
        'B00714A': [],
        'B00802A': []
    }

    client, db = polacz_z_mongo()
    ts = polacz_z_redis()

    data = kalendarz.get_date()

    for stacja in stacje:
        station = db.stations.find_one({"_id": stacja})
        timestamp_start = None
        timestamp_end = None

        day_before = datetime.strptime(data, "%Y-%m-%d") - timedelta(days=1)
        day_before = datetime.strftime(day_before, "%Y-%m-%d")
        timestamp_dusk_prev_day = None

        for days in station['sun_times']:
            if days['date'] == day_before:
                timestamp_dusk_prev_day = days['dusk']

            if days['date'] == data:
                timestamp_start = days['dawn']
                timestamp_end = days['dusk']
                break

        for pomiar in pomiary:
            try:
                range = ts.range(f"{stacja}:{pomiar}", timestamp_start, timestamp_end)
                for r in range:
                    dane_dzien[pomiar].append(r[1])
            except:
                pass

            try:
                range = ts.range(f"{stacja}:{pomiar}", timestamp_dusk_prev_day, timestamp_start)
                for r in range:
                    dane_noc[pomiar].append(r[1])
            except:
                pass
        
    client.close()
    write_data(dane_dzien, dane_noc)

def licz_wojewodztwo():
    stacje = wybierz_stacje_wojewodztwa(selected_wojewodztwo.get())

    dane_dzien = {
        'B00202A': [],
        'B00300S': [],
        'B00305A': [],
        'B00604S': [],
        'B00606S': [],
        'B00608S': [],
        'B00702A': [],
        'B00703A': [],
        'B00714A': [],
        'B00802A': []
    }

    dane_noc = {
        'B00202A': [],
        'B00300S': [],
        'B00305A': [],
        'B00604S': [],
        'B00606S': [],
        'B00608S': [],
        'B00702A': [],
        'B00703A': [],
        'B00714A': [],
        'B00802A': []
    }

    client, db = polacz_z_mongo()
    ts = polacz_z_redis()

    data = kalendarz.get_date()

    for stacja in stacje:
        station = db.stations.find_one({"_id": stacja})
        timestamp_start = None
        timestamp_end = None

        day_before = datetime.strptime(data, "%Y-%m-%d") - timedelta(days=1)
        day_before = datetime.strftime(day_before, "%Y-%m-%d")
        timestamp_dusk_prev_day = None

        for days in station['sun_times']:
            if days['date'] == day_before:
                timestamp_dusk_prev_day = days['dusk']

            if days['date'] == data:
                timestamp_start = days['dawn']
                timestamp_end = days['dusk']
                break
    
        for pomiar in pomiary:
            try:
                range = ts.range(f"{stacja}:{pomiar}", timestamp_start, timestamp_end)
                for r in range:
                    dane_dzien[pomiar].append(r[1])
            except:
                pass

            try:
                range = ts.range(f"{stacja}:{pomiar}", timestamp_dusk_prev_day, timestamp_start)
                for r in range:
                    dane_noc[pomiar].append(r[1])
            except:
                pass
        
    client.close()
    write_data(dane_dzien, dane_noc)

def write_data(dane_dzien, dane_noc):
    try:
        srednia = round(sum(dane_dzien['B00202A']) / len(dane_dzien['B00202A']), 1)
        mediana = round(sorted(dane_dzien['B00202A'])[len(dane_dzien['B00202A']) // 2], 1)
        kierunek_wiatru_label.config(text=f"{srednia}°")
        kierunek_wiatru_label_mediana.config(text=f"{mediana}°")
    except ZeroDivisionError:
        kierunek_wiatru_label.config(text=f"brak danych")
        kierunek_wiatru_label_mediana.config(text=f"brak danych")
    
    try:
        srednia = round(sum(dane_noc['B00202A']) / len(dane_noc['B00202A']), 1)
        mediana = round(sorted(dane_noc['B00202A'])[len(dane_noc['B00202A']) // 2], 1)
        kierunek_wiatru_label_night.config(text=f"{srednia}°")
        kierunek_wiatru_label_night_mediana.config(text=f"{mediana}°")
    except ZeroDivisionError:
        kierunek_wiatru_label_night.config(text=f"brak danych")
        kierunek_wiatru_label_night_mediana.config(text=f"brak danych")

    try:
        srednia = round(sum(dane_dzien['B00300S']) / len(dane_dzien['B00300S']), 1)
        mediana = round(sorted(dane_dzien['B00300S'])[len(dane_dzien['B00300S']) // 2], 1)
        t_powietrza_label.config(text=f"{srednia} °C")
        t_powietrza_label_mediana.config(text=f"{mediana} °C")
    except ZeroDivisionError:
        t_powietrza_label.config(text=f"brak danych")
        t_powietrza_label_mediana.config(text=f"brak danych")
    
    try:
        srednia = round(sum(dane_noc['B00300S']) / len(dane_noc['B00300S']), 1)
        mediana = round(sorted(dane_noc['B00300S'])[len(dane_noc['B00300S']) // 2], 1)
        t_powietrza_label_night.config(text=f"{srednia} °C")
        t_powietrza_label_night_mediana.config(text=f"{mediana} °C")
    except ZeroDivisionError:
        t_powietrza_label_night.config(text=f"brak danych")
        t_powietrza_label_night_mediana.config(text=f"brak danych")

    try:
        srednia = round(sum(dane_dzien['B00305A']) / len(dane_dzien['B00305A']), 1)
        mediana = round(sorted(dane_dzien['B00305A'])[len(dane_dzien['B00305A']) // 2], 1)
        t_gruntu_label.config(text=f"{srednia} °C")
        t_gruntu_label_mediana.config(text=f"{mediana} °C")
    except ZeroDivisionError:
        t_gruntu_label.config(text=f"brak danych")
        t_gruntu_label_mediana.config(text=f"brak danych")
    
    try:
        srednia = round(sum(dane_noc['B00305A']) / len(dane_noc['B00305A']), 1)
        mediana = round(sorted(dane_noc['B00305A'])[len(dane_noc['B00305A']) // 2], 1)
        t_gruntu_label_night.config(text=f"{srednia} °C")
        t_gruntu_label_mediana_night.config(text=f"{mediana} °C")
    except ZeroDivisionError:
        t_gruntu_label_night.config(text=f"brak danych")
        t_gruntu_label_mediana_night.config(text=f"brak danych")

    if len(dane_dzien['B00604S']) > 0:
        B00604S = round(sum(dane_dzien['B00604S']) / len(dane_dzien['B00604S']), 1)
        opad_dobowy_label.config(text=f"{B00604S} mm")
    elif len(dane_noc['B00604S']) > 0:
        B00604S = round(sum(dane_noc['B00604S']) / len(dane_noc['B00604S']), 1)
        opad_dobowy_label.config(text=f"{B00604S} mm")
    else:
        opad_dobowy_label.config(text=f"brak danych")
    
    try:
        srednia = round(sum(dane_dzien['B00606S']) / len(dane_dzien['B00606S']), 1)
        mediana = round(sorted(dane_dzien['B00606S'])[len(dane_dzien['B00606S']) // 2], 1)
        opad_godzinowy_label.config(text=f"{srednia} mm")
        opad_godzinowy_label_mediana.config(text=f"{mediana} mm")
    except ZeroDivisionError:
        opad_godzinowy_label.config(text=f"brak danych")
        opad_godzinowy_label_mediana.config(text=f"brak danych")
    
    try:
        srednia = round(sum(dane_noc['B00606S']) / len(dane_noc['B00606S']), 1)
        mediana = round(sorted(dane_noc['B00606S'])[len(dane_noc['B00606S']) // 2], 1)
        opad_godzinowy_label_night.config(text=f"{srednia} mm")
        opad_godzinowy_label_night_mediana.config(text=f"{mediana} mm")
    except ZeroDivisionError:
        opad_godzinowy_label_night.config(text=f"brak danych")
        opad_godzinowy_label_night_mediana.config(text=f"brak danych")
    
    try:
        srednia = round(sum(dane_dzien['B00608S']) / len(dane_dzien['B00608S']), 1)
        mediana = round(sorted(dane_dzien['B00608S'])[len(dane_dzien['B00608S']) // 2], 1)
        opad_dziesieciominutowy_label.config(text=f"{srednia} mm")
        opad_dziesieciominutowy_label_mediana.config(text=f"{mediana} mm")
    except ZeroDivisionError:
        opad_dziesieciominutowy_label.config(text=f"brak danych")
        opad_dziesieciominutowy_label_mediana.config(text=f"brak danych")
    
    try:
        srednia = round(sum(dane_noc['B00608S']) / len(dane_noc['B00608S']), 1)
        mediana = round(sorted(dane_noc['B00608S'])[len(dane_noc['B00608S']) // 2], 1)
        opad_dziesieciominutowy_label_night.config(text=f"{srednia} mm")
        opad_dziesieciominutowy_label_night_mediana.config(text=f"{mediana} mm")
    except ZeroDivisionError:
        opad_dziesieciominutowy_label_night.config(text=f"brak danych")
        opad_dziesieciominutowy_label_night_mediana.config(text=f"brak danych")

    try:
        srednia = round(sum(dane_dzien['B00702A']) / len(dane_dzien['B00702A']), 1)
        mediana = round(sorted(dane_dzien['B00702A'])[len(dane_dzien['B00702A']) // 2], 1)
        predkosc_wiatru_label.config(text=f"{srednia} m/s")
        predkosc_wiatru_label_mediana.config(text=f"{mediana} m/s")
    except ZeroDivisionError:
        predkosc_wiatru_label.config(text=f"brak danych")
        predkosc_wiatru_label_mediana.config(text=f"brak danych")
    
    try:
        srednia = round(sum(dane_noc['B00702A']) / len(dane_noc['B00702A']), 1)
        mediana = round(sorted(dane_noc['B00702A'])[len(dane_noc['B00702A']) // 2], 1)
        predkosc_wiatru_label_night.config(text=f"{srednia} m/s")
        predkosc_wiatru_label_night_mediana.config(text=f"{mediana} m/s")
    except ZeroDivisionError:
        predkosc_wiatru_label_night.config(text=f"brak danych")
        predkosc_wiatru_label_night_mediana.config(text=f"brak danych")
    
    try:
        srednia = round(sum(dane_dzien['B00703A']) / len(dane_dzien['B00703A']), 1)
        mediana = round(sorted(dane_dzien['B00703A'])[len(dane_dzien['B00703A']) // 2], 1)
        maks_predkosc_wiatru_label.config(text=f"{srednia} m/s")
        maks_predkosc_wiatru_label_mediana.config(text=f"{mediana} m/s")
    except ZeroDivisionError:
        maks_predkosc_wiatru_label.config(text=f"brak danych")
        maks_predkosc_wiatru_label_mediana.config(text=f"brak danych")

    try: 
        srednia = round(sum(dane_noc['B00703A']) / len(dane_noc['B00703A']), 1)
        mediana = round(sorted(dane_noc['B00703A'])[len(dane_noc['B00703A']) // 2], 1)
        maks_predkosc_wiatru_label_night.config(text=f"{srednia} m/s")
        maks_predkosc_wiatru_label_night_mediana.config(text=f"{mediana} m/s")
    except ZeroDivisionError:
        maks_predkosc_wiatru_label_night.config(text=f"brak danych")
        maks_predkosc_wiatru_label_night_mediana.config(text=f"brak danych")
    
    if len(dane_dzien['B00714A']) > 0:
        B00714A = round(sum(dane_dzien['B00714A']) / len(dane_dzien['B00714A']), 1)
        najwiekszy_poryw_label.config(text=f"{B00714A} m/s")
    elif len(dane_noc['B00714A']) > 0:
        B00714A = round(sum(dane_noc['B00714A']) / len(dane_noc['B00714A']), 1)
        najwiekszy_poryw_label.config(text=f"{B00714A} m/s")
    else:
        najwiekszy_poryw_label.config(text=f"brak danych")

    try:
        srednia = round(sum(dane_dzien['B00802A']) / len(dane_dzien['B00802A']), 1)
        mediana = round(sorted(dane_dzien['B00802A'])[len(dane_dzien['B00802A']) // 2], 1)
        wilgotnosc_wzgl_powietrza_label.config(text=f"{srednia} %")
        wilgotnosc_wzgl_powietrza_label_mediana.config(text=f"{mediana} %")
    except ZeroDivisionError:
        wilgotnosc_wzgl_powietrza_label.config(text=f"brak danych")
        wilgotnosc_wzgl_powietrza_label_mediana.config(text=f"brak danych")
    
    try:
        srednia = round(sum(dane_noc['B00802A']) / len(dane_noc['B00802A']), 1)
        mediana = round(sorted(dane_noc['B00802A'])[len(dane_noc['B00802A']) // 2], 1)
        wilgotnosc_wzgl_powietrza_label_night.config(text=f"{srednia} %")
        wilgotnosc_wzgl_powietrza_label_night_mediana.config(text=f"{mediana} %")
    except ZeroDivisionError:
        wilgotnosc_wzgl_powietrza_label_night.config(text=f"brak danych")
        wilgotnosc_wzgl_powietrza_label_night_mediana.config(text=f"brak danych")


root = tk.Tk()
root.geometry("700x1000")
root.title("analiza danych meteo")

options = tk.LabelFrame(root, text="Opcje")
options.pack(side=tk.LEFT, fill=tk.BOTH)

results = tk.LabelFrame(root, text="Wyniki")
results.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

moon_img = Image.open("img/moon.png")
moon_img = moon_img.resize((20, 20))
moon_img = ImageTk.PhotoImage(moon_img)

sun_img = Image.open("img/sun.png")
sun_img = sun_img.resize((20, 20))
sun_img = ImageTk.PhotoImage(sun_img)

days_night_imgs = tk.Frame(results)
days_night_imgs.pack()

moon_label = tk.Label(days_night_imgs, image=moon_img)
moon_label.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

empty_label = tk.Label(days_night_imgs, text=" ")
empty_label.pack(side=tk.LEFT, pady=10, padx=100, expand=True)

sun_label = tk.Label(days_night_imgs, image=sun_img)
sun_label.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

selected_date = tk.StringVar()
kalendarz = Calendar(options, selectmode='day', year=2024, month=10, day=1, date_pattern="yyyy-mm-dd")
kalendarz.pack(pady=20, padx=20)

button = tk.Button(options, text="Wybierz datę", command=wybierz_date)
button.pack(pady=10)

powiaty, wojewodztwa = pobierz_wojewodztwa()

wybierz_wojewodztwo_label = tk.Label(options, text="Wybierz województwo:")
wybierz_wojewodztwo_label.pack(pady=10)

selected_wojewodztwo = tk.StringVar(value="Wybierz")
wojewodztwo_dropdown = ttk.Combobox(options, textvariable=selected_wojewodztwo, values=wojewodztwa, state="readonly")
wojewodztwo_dropdown.pack(pady=10)

wojewodztwo_dropdown.bind("<<ComboboxSelected>>", lambda event: wybierz_wojewodztwo(selected_wojewodztwo.get()))

licz_woj_button = tk.Button(options, text="Oblicz dla województwa")
licz_woj_button.pack(pady=10)
licz_woj_button.configure(command=licz_wojewodztwo)

wybierz_powiat_label = tk.Label(options, text="Wybierz powiat:")
wybierz_powiat_label.pack(pady=10)

selected_powiat = tk.StringVar(value="Wybierz")
powiat_dropdown = ttk.Combobox(options, textvariable=selected_powiat, values=powiaty, state="readonly")
powiat_dropdown.pack(pady=10)

powiat_dropdown.bind("<<ComboboxSelected>>", lambda event: wybierz_powiat(selected_powiat.get()))

licz_button = tk.Button(options, text="Oblicz dla powiatu")
licz_button.pack(pady=10)
licz_button.configure(command=licz_powiat)

t_powietrza_frame = tk.LabelFrame(results, text="Temperatura powietrza")
t_powietrza_frame.pack(fill=tk.X, padx=10)

t_powietrza_srednie = tk.Frame(t_powietrza_frame)
t_powietrza_srednie.pack(fill=tk.X)

t_powietrza_label_night = tk.Label(t_powietrza_srednie, text="")
t_powietrza_label_night.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

t_powietrza_srednia_sep = tk.Label(t_powietrza_srednie, text="śr.")
t_powietrza_srednia_sep.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

t_powietrza_label = tk.Label(t_powietrza_srednie, text="")
t_powietrza_label.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

t_powietrza_mediany = tk.Frame(t_powietrza_frame)
t_powietrza_mediany.pack(fill=tk.X)

t_powietrza_label_night_mediana = tk.Label(t_powietrza_mediany, text="")
t_powietrza_label_night_mediana.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

t_powietrza_mediana_sep = tk.Label(t_powietrza_mediany, text="med.")
t_powietrza_mediana_sep.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

t_powietrza_label_mediana = tk.Label(t_powietrza_mediany, text="")
t_powietrza_label_mediana.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

t_gruntu_frame = tk.LabelFrame(results, text="Temperatura gruntu")
t_gruntu_frame.pack(fill=tk.X, padx=10)

t_gruntu_srednie = tk.Frame(t_gruntu_frame)
t_gruntu_srednie.pack(fill=tk.X)

t_gruntu_label_night = tk.Label(t_gruntu_srednie, text="")
t_gruntu_label_night.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

t_gruntu_srednie_sep = tk.Label(t_gruntu_srednie, text="śr.")
t_gruntu_srednie_sep.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

t_gruntu_label = tk.Label(t_gruntu_srednie, text="")
t_gruntu_label.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

t_gruntu_mediany = tk.Frame(t_gruntu_frame)
t_gruntu_mediany.pack(fill=tk.X)

t_gruntu_label_mediana_night = tk.Label(t_gruntu_mediany, text="")
t_gruntu_label_mediana_night.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

t_gruntu_mediana_sep = tk.Label(t_gruntu_mediany, text="med.")
t_gruntu_mediana_sep.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

t_gruntu_label_mediana = tk.Label(t_gruntu_mediany, text="")
t_gruntu_label_mediana.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

opad_dobowy_frame = tk.LabelFrame(results, text="Opad dobowy")
opad_dobowy_frame.pack(fill=tk.X, padx=10)

opad_dobowy_label = tk.Label(opad_dobowy_frame, text="")
opad_dobowy_label.pack(pady=10, padx=10)

opad_godzinowy_frame = tk.LabelFrame(results, text="Opad godzinowy")
opad_godzinowy_frame.pack(fill=tk.X, padx=10)

opad_godzinowy_srednie = tk.Frame(opad_godzinowy_frame)
opad_godzinowy_srednie.pack(fill=tk.X)

opad_godzinowy_label_night = tk.Label(opad_godzinowy_srednie, text="")
opad_godzinowy_label_night.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

opad_godzinowy_srednie_sep = tk.Label(opad_godzinowy_srednie, text="śr.")
opad_godzinowy_srednie_sep.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

opad_godzinowy_label = tk.Label(opad_godzinowy_srednie, text="")
opad_godzinowy_label.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

opad_godzinowy_mediany = tk.Frame(opad_godzinowy_frame)
opad_godzinowy_mediany.pack(fill=tk.X)

opad_godzinowy_label_night_mediana = tk.Label(opad_godzinowy_mediany, text="")
opad_godzinowy_label_night_mediana.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

opad_godzinowy_mediana_sep = tk.Label(opad_godzinowy_mediany, text="med.")
opad_godzinowy_mediana_sep.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

opad_godzinowy_label_mediana = tk.Label(opad_godzinowy_mediany, text="")
opad_godzinowy_label_mediana.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

opad_dziesieciominutowy_frame = tk.LabelFrame(results, text="Opad dziesięciominutowy")
opad_dziesieciominutowy_frame.pack(fill=tk.X, padx=10)

opad_dziesieciominutowy_srednie = tk.Frame(opad_dziesieciominutowy_frame)
opad_dziesieciominutowy_srednie.pack(fill=tk.X)

opad_dziesieciominutowy_label_night = tk.Label(opad_dziesieciominutowy_srednie, text="")
opad_dziesieciominutowy_label_night.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

opad_dziesieciominutowy_srednie_sep = tk.Label(opad_dziesieciominutowy_srednie, text="śr.")
opad_dziesieciominutowy_srednie_sep.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

opad_dziesieciominutowy_label = tk.Label(opad_dziesieciominutowy_srednie, text="")
opad_dziesieciominutowy_label.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

opad_dziesieciominutowy_mediany = tk.Frame(opad_dziesieciominutowy_frame)
opad_dziesieciominutowy_mediany.pack(fill=tk.X)

opad_dziesieciominutowy_label_night_mediana = tk.Label(opad_dziesieciominutowy_mediany, text="")
opad_dziesieciominutowy_label_night_mediana.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

opad_dziesieciominutowy_mediana_sep = tk.Label(opad_dziesieciominutowy_mediany, text="med.")
opad_dziesieciominutowy_mediana_sep.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

opad_dziesieciominutowy_label_mediana = tk.Label(opad_dziesieciominutowy_mediany, text="")
opad_dziesieciominutowy_label_mediana.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

predkosc_wiatru_frame = tk.LabelFrame(results, text="Prędkość wiatru")
predkosc_wiatru_frame.pack(fill=tk.X, padx=10)

predkosc_wiatru_srednia = tk.Frame(predkosc_wiatru_frame)
predkosc_wiatru_srednia.pack(fill=tk.X)

predkosc_wiatru_label_night = tk.Label(predkosc_wiatru_srednia, text="")
predkosc_wiatru_label_night.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

predkosc_wiatru_srednia_sep = tk.Label(predkosc_wiatru_srednia, text="śr.")
predkosc_wiatru_srednia_sep.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

predkosc_wiatru_label = tk.Label(predkosc_wiatru_srednia, text="")
predkosc_wiatru_label.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

predkosc_wiatru_mediana = tk.Frame(predkosc_wiatru_frame)
predkosc_wiatru_mediana.pack(fill=tk.X)

predkosc_wiatru_label_night_mediana = tk.Label(predkosc_wiatru_mediana, text="")
predkosc_wiatru_label_night_mediana.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

predkosc_wiatru_mediana_sep = tk.Label(predkosc_wiatru_mediana, text="med.")
predkosc_wiatru_mediana_sep.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

predkosc_wiatru_label_mediana = tk.Label(predkosc_wiatru_mediana, text="")
predkosc_wiatru_label_mediana.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

kierunek_wiatru_frame = tk.LabelFrame(results, text="Kierunek wiatru")
kierunek_wiatru_frame.pack(fill=tk.X, padx=10)

kierunek_srednia_frame = tk.Frame(kierunek_wiatru_frame)
kierunek_srednia_frame.pack(fill=tk.X)

kierunek_wiatru_label_night = tk.Label(kierunek_srednia_frame, text="")
kierunek_wiatru_label_night.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

kierunek_srednia_sep = tk.Label(kierunek_srednia_frame, text="śr.")
kierunek_srednia_sep.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

kierunek_wiatru_label = tk.Label(kierunek_srednia_frame, text="")
kierunek_wiatru_label.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

kierunek_mediana_frame = tk.Frame(kierunek_wiatru_frame)
kierunek_mediana_frame.pack(fill=tk.X)

kierunek_wiatru_label_night_mediana = tk.Label(kierunek_mediana_frame, text="")
kierunek_wiatru_label_night_mediana.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

kierunek_mediana_sep = tk.Label(kierunek_mediana_frame, text="med.")
kierunek_mediana_sep.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

kierunek_wiatru_label_mediana = tk.Label(kierunek_mediana_frame, text="")
kierunek_wiatru_label_mediana.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

maks_predkosc_wiatru_frame = tk.LabelFrame(results, text="Maksymalna prędkość wiatru")
maks_predkosc_wiatru_frame.pack(fill=tk.X, padx=10)

maks_predkosc_wiatru_srednia = tk.Frame(maks_predkosc_wiatru_frame)
maks_predkosc_wiatru_srednia.pack(fill=tk.X)

maks_predkosc_wiatru_label_night = tk.Label(maks_predkosc_wiatru_srednia, text="")
maks_predkosc_wiatru_label_night.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

maks_predkosc_wiatru_srednia_sep = tk.Label(maks_predkosc_wiatru_srednia, text="śr.")
maks_predkosc_wiatru_srednia_sep.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

maks_predkosc_wiatru_label = tk.Label(maks_predkosc_wiatru_srednia, text="")
maks_predkosc_wiatru_label.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

maks_predkosc_wiatru_mediana = tk.Frame(maks_predkosc_wiatru_frame)
maks_predkosc_wiatru_mediana.pack(fill=tk.X)

maks_predkosc_wiatru_label_night_mediana = tk.Label(maks_predkosc_wiatru_mediana, text="")
maks_predkosc_wiatru_label_night_mediana.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

maks_predkosc_wiatru_mediana_sep = tk.Label(maks_predkosc_wiatru_mediana, text="med.")
maks_predkosc_wiatru_mediana_sep.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

maks_predkosc_wiatru_label_mediana = tk.Label(maks_predkosc_wiatru_mediana, text="")
maks_predkosc_wiatru_label_mediana.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

najwiekszy_poryw_frame = tk.LabelFrame(results, text="Największy poryw")
najwiekszy_poryw_frame.pack(fill=tk.X, padx=10)

najwiekszy_poryw_label = tk.Label(najwiekszy_poryw_frame, text="")
najwiekszy_poryw_label.pack(pady=10, padx=10)

wilgotnosc_wzgl_powietrza_frame = tk.LabelFrame(results, text="Wilgotność wzgl. powietrza")
wilgotnosc_wzgl_powietrza_frame.pack(fill=tk.X, padx=10)

wilgotnosc_srednia_frame = tk.Frame(wilgotnosc_wzgl_powietrza_frame)
wilgotnosc_srednia_frame.pack(fill=tk.X)

wilgotnosc_wzgl_powietrza_label_night = tk.Label(wilgotnosc_srednia_frame, text="")
wilgotnosc_wzgl_powietrza_label_night.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

wilgotnosc_wzgl_srednia_sep = tk.Label(wilgotnosc_srednia_frame, text="śr.")
wilgotnosc_wzgl_srednia_sep.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

wilgotnosc_wzgl_powietrza_label = tk.Label(wilgotnosc_srednia_frame, text="")
wilgotnosc_wzgl_powietrza_label.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

wilgotnosc_mediany_frame = tk.Frame(wilgotnosc_wzgl_powietrza_frame)
wilgotnosc_mediany_frame.pack(fill=tk.X)

wilgotnosc_wzgl_powietrza_label_night_mediana = tk.Label(wilgotnosc_mediany_frame, text="")
wilgotnosc_wzgl_powietrza_label_night_mediana.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

wilgotnosc_wzgl_mediana_sep = tk.Label(wilgotnosc_mediany_frame, text="med.")
wilgotnosc_wzgl_mediana_sep.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

wilgotnosc_wzgl_powietrza_label_mediana = tk.Label(wilgotnosc_mediany_frame, text="")
wilgotnosc_wzgl_powietrza_label_mediana.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

root.mainloop()