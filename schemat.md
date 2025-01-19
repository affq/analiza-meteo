# baza z informacjami nt. stacji - mongodb

baza: pag -> kolekcja: stations -> stacja

## przykładowa stacja:

    _id: 149180150,
    name: 'Brenna-Leśnica',
    location: { 
        type: 'Point', 
        coordinates: [ 18.902778, 49.719999999999985 ] 
        },
    powiat: 'cieszyński',
    wojewodztwo: 'śląskie'

## wypisanie wszystkich stacji:

    mongosh

    show dbs

    use pag

    show collections

    db.stations.find()



# baza z danymi meteorologicznymi - redis time series
baza -> id stacji -> id serii danych

## wypisanie danych z wybranej serii

    redis-cli -p 6380

### wybór wszystkich danych z serii:

    TS.RANGE 249180160:B00300S - +

### wybór danych z określonego zakresu:

    TS.RANGE 249180160:B00300S timestamp1 timestamp2