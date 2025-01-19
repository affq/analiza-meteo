## Wykonanie analiz geostatystycznych:
- a. Średniej i mediany wartości pomiaru w podziale na daty w poszczególnych województwach i
powiatach.  (opcjonalnie: w ciągu dnia i nocy w podziale na daty)
- b. Zmiany wartości średniej i mediany w zadanych interwałach czasu w województwach i
powiatach.  (opcjonalnie: w ciągu dnia i nocy w podziale na daty)


## Sposób liczenia średniej obcinanej w bibliotece SciPy:

    from scipy import stats
    stats.trim_mean(data, 0.1) # ucinanie na poziomie 10%


## Sposób przetwarzania danych o lokalizacji w bibliotece Astral:

    from astral import LocationInfo
    city = LocationInfo("Warsaw", "Poland", "Europe/Warsaw", 52.232222, 21.008333)
    print(city.name, city.latitude, city.longitude)

##  Sposób liczenia parametrów słońca w zadanym miejscu:
    from astral.sun import sun
    s = sun(city.observer, date=datetime.date(2021, 02, 14), tzinfo=city.timezone)
    print(s["dawn"], s["sunrise"], s["noon"], s["sunset"], s["dusk"])