import os
from urllib import request
import json

import argparse
import json
import os
arg_parser = argparse.ArgumentParser()


arg_parser.add_argument('--id', action='store', type=str, required=True, dest='id')



args = arg_parser.parse_args()
print(args)

id = args.id



conf_local_tmp = conf_local_tmp = '/tmp/data'
conf_cities = conf_cities = {'Amsterdam': (52.37, 4.89), 'Paris': (48.85, 2.35), 'Berlin': (52.52, 13.41), 'Rome': (41.9, 12.5), 'Lisbon': (38.72, -9.14)}

def fetch_json(url):
    with request.urlopen(url, timeout=15) as resp:
        return json.loads(resp.read().decode('utf-8'))

def fetch_current(lat, lon):
    url = (
        'https://api.open-meteo.com/v1/forecast'
        f'?latitude={lat}&longitude={lon}'
        '&current=temperature_2m,relative_humidity_2m,wind_speed_10m'
        '&timezone=auto'
        )
    return fetch_json(url)['current']

os.makedirs(conf_local_tmp, exist_ok=True)

tabs_html = []
for city, (lat, lon) in conf_cities.items():
    current = fetch_current(lat, lon)
    tabs_html.append(
        f"<section><h2>{city}</h2>"
        f"<p><b>{current['temperature_2m']} °C</b><br>"
        f"Humidity: {current['relative_humidity_2m']}%<br>"
        f"Wind: {current['wind_speed_10m']} km/h</p></section>"
        )

page = (
    "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'>"
    "<title>City weather</title><style>"
    "body{font-family:sans-serif;display:flex;gap:1rem;flex-wrap:wrap}"
    "section{border:1px solid #ccc;border-radius:8px;padding:1rem}"
    "</style></head><body>" + "".join(tabs_html) + "</body></html>"
    )

widget_html_path = os.path.join(conf_local_tmp, 'weather_widget.html')
with open(widget_html_path, 'w') as f:
    f.write(page)

print(f'Wrote {widget_html_path}')

file_widget_html_path = open("/tmp/widget_html_path_" + id + ".json", "w")
file_widget_html_path.write(json.dumps(widget_html_path))
file_widget_html_path.close()
