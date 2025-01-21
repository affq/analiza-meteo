import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from pymongo import MongoClient
import math
from redis import Redis
from redis.commands.timeseries import TimeSeries
from datetime import datetime, timedelta
from PIL import Image, ImageTk
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEngineSettings
from flask import Flask, render_template
from flask_socketio import SocketIO
import threading

def polacz_z_redis():
    r = Redis(host='localhost', port=6380, db=0)
    ts = TimeSeries(r)
    return ts

def polacz_z_mongo():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["pag"]
    return client, db

def pobierz_wojewodztwa():
    client, db = polacz_z_mongo()
    wojewodztwa = db.stations.distinct("wojewodztwo")
    wojewodztwa = [w for w in wojewodztwa if not (isinstance(w, float) and math.isnan(w))]
    powiaty = db.stations.distinct("powiat")
    powiaty  = [p for p in powiaty if not (isinstance(p, float) and math.isnan(p))]
    client.close()
    return powiaty, wojewodztwa

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

def licz_srednia(dane):
    try:
        srednia = round(sum(dane) / len(dane), 1)
        return srednia
    except ZeroDivisionError:
        return "brak danych"

def licz_mediana(dane):
    if len(dane) % 2 == 0:
        mediana = round((sorted(dane)[len(dane) // 2] + sorted(dane)[len(dane) // 2 - 1]) / 2, 1)
    else:
        mediana = round(sorted(dane)[len(dane) // 2], 1)
    return mediana

app = Flask(__name__, template_folder=r"C:\Users\adria\Desktop\STUDIA_FOLDERY\pag-2-blok-2\web\templates", static_url_path='', static_folder=r"C:\Users\adria\Desktop\STUDIA_FOLDERY\pag-2-blok-2\web\static")
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template("map.html")

def wybierz_powiat(value):
    client, db = polacz_z_mongo()
    wojewodztwo_powiatu = db.stations.find_one({"powiat": value})["wojewodztwo"]
    selected_wojewodztwo.set(wojewodztwo_powiatu)
    selected_powiat.set(value)
    client.close()

def wybierz_wojewodztwo(value):
    client, db = polacz_z_mongo()
    powiaty_w_wojewodztwie = db.stations.distinct("powiat", {"wojewodztwo": value})
    powiat_dropdown["values"] = powiaty_w_wojewodztwie
    selected_powiat.set("Wybierz")
    selected_wojewodztwo.set(value)
    client.close()

def write_data(dane_dzien, dane_noc):
    try:
        srednia = licz_srednia(dane_dzien['B00202A'])
        mediana = licz_mediana(dane_dzien['B00202A'])
        kierunek_wiatru_label.config(text=f"{srednia}°")
        kierunek_wiatru_label_mediana.config(text=f"{mediana}°")
    except ZeroDivisionError:
        kierunek_wiatru_label.config(text=f"brak danych")
    except IndexError:
        kierunek_wiatru_label_mediana.config(text=f"brak danych")
    
    try:
        srednia = licz_srednia(dane_noc['B00202A'])
        mediana = licz_mediana(dane_noc['B00202A'])
        kierunek_wiatru_label_night.config(text=f"{srednia}°")
        kierunek_wiatru_label_night_mediana.config(text=f"{mediana}°")
    except ZeroDivisionError:
        kierunek_wiatru_label_night.config(text=f"brak danych")
    except IndexError:
        kierunek_wiatru_label_night_mediana.config(text=f"brak danych")

    try:
        srednia = licz_srednia(dane_dzien['B00300S'])
        mediana = licz_mediana(dane_dzien['B00300S'])
        t_powietrza_label.config(text=f"{srednia} °C")
        t_powietrza_label_mediana.config(text=f"{mediana} °C")
    except ZeroDivisionError:
        t_powietrza_label.config(text=f"brak danych")
    except IndexError:
        t_powietrza_label_mediana.config(text=f"brak danych")
    
    try:
        srednia = licz_srednia(dane_noc['B00300S'])
        mediana = licz_mediana(dane_noc['B00300S'])
        t_powietrza_label_night.config(text=f"{srednia} °C")
        t_powietrza_label_night_mediana.config(text=f"{mediana} °C")
    except ZeroDivisionError:
        t_powietrza_label_night.config(text=f"brak danych")
    except IndexError:
        t_powietrza_label_night_mediana.config(text=f"brak danych")

    try:
        srednia = licz_srednia(dane_dzien['B00305A'])
        mediana = licz_mediana(dane_dzien['B00305A'])
        t_gruntu_label.config(text=f"{srednia} °C")
        t_gruntu_label_mediana.config(text=f"{mediana} °C")
    except ZeroDivisionError:
        t_gruntu_label.config(text=f"brak danych")
    except IndexError:
        t_gruntu_label_mediana.config(text=f"brak danych")
    
    try:
        srednia = licz_srednia(dane_noc['B00305A'])
        mediana = licz_mediana(dane_noc['B00305A'])
        t_gruntu_label_night.config(text=f"{srednia} °C")
        t_gruntu_label_mediana_night.config(text=f"{mediana} °C")
    except ZeroDivisionError:
        t_gruntu_label_night.config(text=f"brak danych")
    except IndexError:
        t_gruntu_label_mediana_night.config(text=f"brak danych")

    if len(dane_dzien['B00604S']) > 0:
        B00604S = dane_dzien['B00604S'][0]
        opad_dobowy_label.config(text=f"{B00604S} mm")
    elif len(dane_noc['B00604S']) > 0:
        B00604S = dane_noc['B00604S'][0]
        opad_dobowy_label.config(text=f"{B00604S} mm")
    else:
        opad_dobowy_label.config(text=f"brak danych")
    
    try:
        srednia = licz_srednia(dane_dzien['B00606S'])
        mediana = licz_mediana(dane_dzien['B00606S'])
        opad_godzinowy_label.config(text=f"{srednia} mm")
        opad_godzinowy_label_mediana.config(text=f"{mediana} mm")
    except ZeroDivisionError:
        opad_godzinowy_label.config(text=f"brak danych")
    except IndexError:
        opad_godzinowy_label_mediana.config(text=f"brak danych")
    
    try:
        srednia = licz_srednia(dane_noc['B00606S'])
        mediana = licz_mediana(dane_noc['B00606S'])
        opad_godzinowy_label_night.config(text=f"{srednia} mm")
        opad_godzinowy_label_night_mediana.config(text=f"{mediana} mm")
    except ZeroDivisionError:
        opad_godzinowy_label_night.config(text=f"brak danych")
    except IndexError:
        opad_godzinowy_label_night_mediana.config(text=f"brak danych")
    
    try:
        srednia = licz_srednia(dane_dzien['B00608S'])
        mediana = licz_mediana(dane_dzien['B00608S'])
        opad_dziesieciominutowy_label.config(text=f"{srednia} mm")
        opad_dziesieciominutowy_label_mediana.config(text=f"{mediana} mm")
    except ZeroDivisionError:
        opad_dziesieciominutowy_label.config(text=f"brak danych")
    except IndexError:
        opad_dziesieciominutowy_label_mediana.config(text=f"brak danych")
    
    try:
        srednia = licz_srednia(dane_noc['B00608S'])
        mediana = licz_mediana(dane_noc['B00608S'])
        opad_dziesieciominutowy_label_night.config(text=f"{srednia} mm")
        opad_dziesieciominutowy_label_night_mediana.config(text=f"{mediana} mm")
    except ZeroDivisionError:
        opad_dziesieciominutowy_label_night.config(text=f"brak danych")
    except IndexError:
        opad_dziesieciominutowy_label_night_mediana.config(text=f"brak danych")

    try:
        srednia = licz_srednia(dane_dzien['B00702A'])
        mediana = licz_mediana(dane_dzien['B00702A'])
        predkosc_wiatru_label.config(text=f"{srednia} m/s")
        predkosc_wiatru_label_mediana.config(text=f"{mediana} m/s")
    except ZeroDivisionError:
        predkosc_wiatru_label.config(text=f"brak danych")
    except IndexError:
        predkosc_wiatru_label_mediana.config(text=f"brak danych")
    
    try:
        srednia = licz_srednia(dane_noc['B00702A'])
        mediana = licz_mediana(dane_noc['B00702A'])
        predkosc_wiatru_label_night.config(text=f"{srednia} m/s")
        predkosc_wiatru_label_night_mediana.config(text=f"{mediana} m/s")
    except ZeroDivisionError:
        predkosc_wiatru_label_night.config(text=f"brak danych")
    except IndexError:
        predkosc_wiatru_label_night_mediana.config(text=f"brak danych")
    
    try:
        srednia = licz_srednia(dane_dzien['B00703A'])
        mediana = licz_mediana(dane_dzien['B00703A'])
        maks_predkosc_wiatru_label.config(text=f"{srednia} m/s")
        maks_predkosc_wiatru_label_mediana.config(text=f"{mediana} m/s")
    except ZeroDivisionError:
        maks_predkosc_wiatru_label.config(text=f"brak danych")
    except IndexError:
        maks_predkosc_wiatru_label_mediana.config(text=f"brak danych")

    try: 
        srednia = licz_srednia(dane_noc['B00703A'])
        mediana = licz_mediana(dane_noc['B00703A'])
        maks_predkosc_wiatru_label_night.config(text=f"{srednia} m/s")
        maks_predkosc_wiatru_label_night_mediana.config(text=f"{mediana} m/s")
    except ZeroDivisionError:
        maks_predkosc_wiatru_label_night.config(text=f"brak danych")
    except IndexError:
        maks_predkosc_wiatru_label_night_mediana.config(text=f"brak danych")
    
    if len(dane_dzien['B00714A']) > 0:
        B00714A = dane_dzien['B00714A'][0]
        najwiekszy_poryw_label.config(text=f"{B00714A} m/s")
    elif len(dane_noc['B00714A']) > 0:
        B00714A = dane_noc['B00714A'][0]
        najwiekszy_poryw_label.config(text=f"{B00714A} m/s")
    else:
        najwiekszy_poryw_label.config(text=f"brak danych")

    try:
        srednia = licz_srednia(dane_dzien['B00802A'])
        mediana = licz_mediana(dane_dzien['B00802A'])
        wilgotnosc_wzgl_powietrza_label.config(text=f"{srednia} %")
        wilgotnosc_wzgl_powietrza_label_mediana.config(text=f"{mediana} %")
    except ZeroDivisionError:
        wilgotnosc_wzgl_powietrza_label.config(text=f"brak danych")
    except IndexError:
        wilgotnosc_wzgl_powietrza_label_mediana.config(text=f"brak danych")
    
    try:
        srednia = licz_srednia(dane_noc['B00802A'])
        mediana = licz_mediana(dane_noc['B00802A'])
        wilgotnosc_wzgl_powietrza_label_night.config(text=f"{srednia} %")
        wilgotnosc_wzgl_powietrza_label_night_mediana.config(text=f"{mediana} %")
    except ZeroDivisionError:
        wilgotnosc_wzgl_powietrza_label_night.config(text=f"brak danych")
    except IndexError:
        wilgotnosc_wzgl_powietrza_label_night_mediana.config(text=f"brak danych")


def licz(stacje):
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


@socketio.on('wybrano')
def test(jednostka):
    print(jednostka)
    if jednostka['type'] == "pow":
        stacje = wybierz_stacje_powiatu(jednostka['name'])
        wybierz_powiat(jednostka['name'])
        licz(stacje)

    elif jednostka['type'] == "woj":
        stacje = wybierz_stacje_wojewodztwa(jednostka['name'])
        wybierz_wojewodztwo(jednostka['name'])
        licz(stacje)


def zaladuj_strone():
    app = QApplication([])
    web_view = QWebEngineView()
    web_view.load(f"http://127.0.0.1:5000")
    
    window = QMainWindow()
    window.setWindowTitle("Mapa")

    settings = web_view.settings()
    settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)

    layout = QVBoxLayout()
    layout.addWidget(web_view)

    central_widget = QWidget()
    central_widget.setLayout(layout)
    window.setCentralWidget(central_widget)

    window.resize(800, 600)
    return window, app

def wybierz_z_mapy():
    app = QApplication([])
    web_view = QWebEngineView()
    web_view.load(f"http://127.0.0.1:5000")
    
    window = QMainWindow()
    window.setWindowTitle("Mapa")

    settings = web_view.settings()
    settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)

    layout = QVBoxLayout()
    layout.addWidget(web_view)

    central_widget = QWidget()
    central_widget.setLayout(layout)
    window.setCentralWidget(central_widget)

    window.resize(800, 600)
    window.show()
    app.exec()

    return window, app

def wybierz_z_mapy_thread():
    threading.Thread(target=wybierz_z_mapy).start()

def start_tkinter_app():
    global selected_powiat, selected_wojewodztwo, powiat_dropdown, wojewodztwo_dropdown, kalendarz, wybierz_wojewodztwo_label, selected_date, thermometer_img, rain_img, wind_img, moon_img, sun_img, days_night_imgs, t_powietrza_label, t_powietrza_label_night, t_powietrza_label_mediana, t_powietrza_label_night_mediana, t_powietrza_srednia_sep, t_powietrza_mediana_sep, t_powietrza_srednie, t_powietrza_mediany, t_gruntu_label, t_gruntu_label_night, t_gruntu_label_mediana, t_gruntu_label_night_mediana, t_gruntu_srednie_sep, t_gruntu_mediana_sep, t_gruntu_srednie, t_gruntu_mediany, opad_dobowy_label, opad_godzinowy_label, opad_godzinowy_label_night, opad_godzinowy_label_mediana, opad_godzinowy_label_night_mediana, opad_godzinowy_srednie_sep, opad_godzinowy_mediana_sep, opad_godzinowy_srednie, opad_godzinowy_mediany, opad_dziesieciominutowy_label, opad_dziesieciominutowy_label_night, opad_dziesieciominutowy_label_mediana, opad_dziesieciominutowy_label_night_mediana, opad_dziesieciominutowy_srednie_sep, opad_dziesieciominutowy_mediana_sep, opad_dziesieciominutowy_srednie, opad_dziesieciominutowy_mediany, predkosc_wiatru_label, predkosc_wiatru_label_night, predkosc_wiatru_label_mediana, predkosc_wiatru_label_night_mediana, predkosc_wiatru_srednia_sep, predkosc_wiatru_mediana_sep, predkosc_wiatru_srednia, predkosc_wiatru_mediana, maks_predkosc_wiatru_label, maks_predkosc_wiatru_label_night, maks_predkosc_wiatru_label_mediana, maks_predkosc_wiatru_label_night_mediana, wilgotnosc_wzgl_powietrza, wilgotnosc_wzgl_powietrza_label_night, wilgotnosc_wzgl_powietrza_label_mediana, wilgotnosc_wzgl_powietrza_label_night_mediana, wilgotnosc_wzgl_powietrza_srednia_sep, wilgotnosc_wzgl_powietrza_mediana_sep, wilgotnosc_wzgl_powietrza_srednia, wilgotnosc_wzgl_powietrza_mediana, kierunek_wiatru_label, kierunek_wiatru_label_night, kierunek_wiatru_label_mediana, kierunek_wiatru_label_night_mediana, kierunek_wiatru_srednia_sep, kierunek_wiatru_mediana_sep, kierunek_wiatru_srednia, kierunek_wiatru_mediana, najwiekszy_poryw_label, najwiekszy_poryw_label_night, najwiekszy_poryw_label_mediana, najwiekszy_poryw_label_night_mediana, najwiekszy_poryw_srednia_sep, najwiekszy_poryw_mediana_sep, najwiekszy_poryw_srednia, najwiekszy_poryw_mediana, wilgotnosc_wzgl_powietrza_label, wilgotnosc_wzgl_powietrza_label_night, wilgotnosc_wzgl_powietrza_label_mediana, wilgotnosc_wzgl_powietrza_label_night_mediana, wilgotnosc_wzgl_powietrza_srednia_sep, wilgotnosc_wzgl_powietrza_mediana_sep, wilgotnosc_wzgl_powietrza_srednia, wilgotnosc_wzgl_powietrza_mediana, t_gruntu_label_mediana_night

    def licz_powiat():
        stacje = wybierz_stacje_powiatu(selected_powiat.get())
        licz(stacje)

    def licz_wojewodztwo():
        stacje = wybierz_stacje_wojewodztwa(selected_wojewodztwo.get())
        licz(stacje)

    def wybierz_date():
        selected_date = kalendarz.get_date()
        wybierz_wojewodztwo_label.config(text=f"Wybrana data: {selected_date}")

    root = tk.Tk()
    root.geometry("1200x700")
    root.title("analiza danych meteo")

    options = tk.LabelFrame(root, text="Opcje")
    options.pack(side=tk.LEFT, fill=tk.BOTH, padx=10)

    results = tk.LabelFrame(root, text="Wyniki")
    results.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)

    moon_img = Image.open("img/moon.png")
    moon_img = moon_img.resize((20, 20))
    moon_img = ImageTk.PhotoImage(moon_img)

    sun_img = Image.open("img/sun.png")
    sun_img = sun_img.resize((20, 20))
    sun_img = ImageTk.PhotoImage(sun_img)

    thermometer_img = Image.open("img/thermometer.png")
    thermometer_img = thermometer_img.resize((30, 30))
    thermometer_img = ImageTk.PhotoImage(thermometer_img)

    rain_img = Image.open("img/rain.png")
    rain_img = rain_img.resize((30, 30))
    rain_img = ImageTk.PhotoImage(rain_img)

    wind_img = Image.open("img/wind.png")
    wind_img = wind_img.resize((30, 30))
    wind_img = ImageTk.PhotoImage(wind_img)

    days_night_imgs = tk.Frame(results)
    days_night_imgs.pack()

    for _ in range (3):
        moon_label = tk.Label(days_night_imgs, image=moon_img)
        moon_label.pack(side=tk.LEFT, pady=10, padx=60, expand=True)
        sun_label = tk.Label(days_night_imgs, image=sun_img)
        sun_label.pack(side=tk.LEFT, pady=10, padx=60, expand=True)

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

    temperatura_frame = tk.LabelFrame(results, text="Temperatura")
    temperatura_frame.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.BOTH)

    thermo_frame = tk.Frame(temperatura_frame)
    thermo_frame.pack(fill=tk.X)

    thermometer_label = tk.Label(thermo_frame, image=thermometer_img)
    thermometer_label.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

    opad_frame = tk.LabelFrame(results, text="Opad")
    opad_frame.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.BOTH)

    wiatr_frame = tk.LabelFrame(results, text="Wiatr")
    wiatr_frame.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.BOTH)

    t_powietrza_frame = tk.LabelFrame(temperatura_frame, text="Temperatura powietrza")
    t_powietrza_frame.pack(fill=tk.X, padx=10, pady=10)

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

    t_gruntu_frame = tk.LabelFrame(temperatura_frame, text="Temperatura gruntu")
    t_gruntu_frame.pack(fill=tk.X, padx=10, pady=10)

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

    rain_img_frame = tk.Frame(opad_frame)
    rain_img_frame.pack(fill=tk.X)

    rain_img_label = tk.Label(rain_img_frame, image=rain_img)
    rain_img_label.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

    opad_dobowy_frame = tk.LabelFrame(opad_frame, text="Opad dobowy")
    opad_dobowy_frame.pack(fill=tk.X, padx=10, pady=10)

    opad_dobowy_label = tk.Label(opad_dobowy_frame, text="")
    opad_dobowy_label.pack(pady=10, padx=10)

    opad_godzinowy_frame = tk.LabelFrame(opad_frame, text="Opad godzinowy")
    opad_godzinowy_frame.pack(fill=tk.X, padx=10, pady=10)

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

    opad_dziesieciominutowy_frame = tk.LabelFrame(opad_frame, text="Opad dziesięciominutowy")
    opad_dziesieciominutowy_frame.pack(fill=tk.X, padx=10, pady=10)

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

    wind_img_frame = tk.Frame(wiatr_frame)
    wind_img_frame.pack(fill=tk.X)

    wind_img_label = tk.Label(wind_img_frame, image=wind_img)
    wind_img_label.pack(side=tk.LEFT, pady=10, padx=10, expand=True)

    predkosc_wiatru_frame = tk.LabelFrame(wiatr_frame, text="Prędkość wiatru")
    predkosc_wiatru_frame.pack(fill=tk.X, padx=10, pady=10)

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

    kierunek_wiatru_frame = tk.LabelFrame(wiatr_frame, text="Kierunek wiatru")
    kierunek_wiatru_frame.pack(fill=tk.X, padx=10, pady=10)

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

    maks_predkosc_wiatru_frame = tk.LabelFrame(wiatr_frame, text="Maksymalna prędkość wiatru")
    maks_predkosc_wiatru_frame.pack(fill=tk.X, padx=10, pady=10)

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

    najwiekszy_poryw_frame = tk.LabelFrame(wiatr_frame, text="Największy poryw")
    najwiekszy_poryw_frame.pack(fill=tk.X, padx=10, pady=10)

    najwiekszy_poryw_label = tk.Label(najwiekszy_poryw_frame, text="")
    najwiekszy_poryw_label.pack(pady=10, padx=10)

    wilgotnosc_wzgl_powietrza_frame = tk.LabelFrame(temperatura_frame, text="Wilgotność wzgl. powietrza")
    wilgotnosc_wzgl_powietrza_frame.pack(fill=tk.X, padx=10, pady=10)

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

    mapa_button = tk.Button(options, text="Wybierz z mapy")
    mapa_button.pack(pady=10)
    mapa_button.configure(command=wybierz_z_mapy_thread)

    root.mainloop()

def run_flask():
    socketio.run(app, debug=True, use_reloader=False)

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    start_tkinter_app()