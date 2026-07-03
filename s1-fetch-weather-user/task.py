import os
import json

import argparse
import json
import os
arg_parser = argparse.ArgumentParser()


arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')


arg_parser.add_argument('--param_city', action='store', type=str, required=True, dest='param_city')
arg_parser.add_argument('--param_forecast_hours', action='store', type=str, required=True, dest='param_forecast_hours')

args = arg_parser.parse_args()
print(args)

id = args.id


param_city = args.param_city.replace('"','')
param_forecast_hours = args.param_forecast_hours.replace('"','')

conf_local_tmp = conf_local_tmp = '/tmp/data'
conf_cities = conf_cities = {'Amsterdam': (52.37, 4.89), 'Paris': (48.85, 2.35), 'Berlin': (52.52, 13.41), 'Rome': (41.9, 12.5), 'Lisbon': (38.72, -9.14)}

def fetch_json(url):
    with urllib.request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read().decode('utf-8'))

def fetch_current(lat, lon):
    url = (
        'https://api.open-meteo.com/v1/forecast'
        f'?latitude={lat}&longitude={lon}'
        '&current=temperature_2m,relative_humidity_2m,wind_speed_10m'
        '&timezone=auto'
        )
    return fetch_json(url)['current']

def fetch_hourly(lat, lon, hours):
    url = (
        'https://api.open-meteo.com/v1/forecast'
        f'?latitude={lat}&longitude={lon}'
        '&hourly=temperature_2m&forecast_days=2&timezone=auto'
        )
    return fetch_json(url)['hourly']['temperature_2m'][:hours]

os.makedirs(conf_local_tmp, exist_ok=True)

lat, lon = conf_cities[param_city]
hourly_temps = fetch_hourly(lat, lon, int(param_forecast_hours))
forecast_path = os.path.join(conf_local_tmp, 'forecast.csv')
with open(forecast_path, 'w', encoding='utf-8') as f:
    f.write('hour,temperature_c\n')
    for i, t in enumerate(hourly_temps):
        f.write(f'{i},{t}\n')
print(f'Wrote {forecast_path} ({len(hourly_temps)} rows)')

features = []
for city, (city_lat, city_lon) in conf_cities.items():
    current = fetch_current(city_lat, city_lon)
    features.append({
        'type': 'Feature',
        'properties': {
            'name': city,
            'temperature_c': current['temperature_2m'],
            'humidity_pct': current['relative_humidity_2m'],
            'wind_speed_kmh': current['wind_speed_10m'],
            },
        'geometry': {'type': 'Point', 'coordinates': [city_lon, city_lat]},
        })

cities_geojson_path = os.path.join(conf_local_tmp, 'cities.geojson')
with open(cities_geojson_path, 'w', encoding='utf-8') as f:
    json.dump({'type': 'FeatureCollection', 'features': features}, f)
print(f'Wrote {cities_geojson_path} ({len(features)} features)')

summary_path = os.path.join(conf_local_tmp, 'summary.csv')
with open(summary_path, 'w', encoding='utf-8') as f:
    f.write('city,temperature_c,humidity_pct,wind_speed_kmh\n')
    for feat in features:
        p = feat['properties']
        f.write(f"{p['name']},{p['temperature_c']},{p['humidity_pct']},{p['wind_speed_kmh']}\n")
print(f'Wrote {summary_path}')

file_cities_geojson_path = open("/tmp/cities_geojson_path_" + id + ".json", "w")
file_cities_geojson_path.write(json.dumps(cities_geojson_path))
file_cities_geojson_path.close()
file_forecast_path = open("/tmp/forecast_path_" + id + ".json", "w")
file_forecast_path.write(json.dumps(forecast_path))
file_forecast_path.close()
file_summary_path = open("/tmp/summary_path_" + id + ".json", "w")
file_summary_path.write(json.dumps(summary_path))
file_summary_path.close()
