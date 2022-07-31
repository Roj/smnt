import re
import requests
import json
import pandas as pd

LOCATION_ID = 10821 # CABA
url_pronostico = "https://www.smn.gob.ar/pronostico/?loc=10821"
FORECAST_URL = "https://ws1.smn.gob.ar/v1/forecast/location/10821"
WEATHER_URL = "https://ws1.smn.gob.ar/v1/weather/location/zoom/2"


def get_jwt_token():
    html_pronostico = requests.get(url_pronostico).content
    obj = re.search("localStorage\.setItem\('token', '([A-z0-9\.\-]+)'\);", html_pronostico.decode("utf-8"))
    jwt = obj.group(1)
    return jwt

def query_endpoint_with_jwt(endpoint, jwt):
    auth_header = f"JWT {jwt}"
    response = requests.get(endpoint, headers={"Authorization": auth_header, "Accept": "application/json"})
    return json.loads(response.content.decode("utf-8"))

def get_forecast(jwt):
    forecast_data = query_endpoint_with_jwt(FORECAST_URL, jwt)
    forecast_df = pd.DataFrame(forecast_data["forecast"])
    return forecast_df

def get_current_weather(jwt, location=LOCATION_ID):
    now = query_endpoint_with_jwt(WEATHER_URL, jwt)
    df_now = pd.DataFrame(now)
    df_now["location_name"] = df_now.location.map(lambda loc: loc["name"])
    df_now["location_id"] = df_now.location.map(lambda loc: loc["id"])
    caba_ahora = df_now.loc[df_now.location_id == location]
    return caba_ahora    

def run_etl():
    jwt = get_jwt_token()
    
    forecast_df = get_forecast(jwt)
    current_weather = get_current_weather(jwt)
    # TODO: convert forecast_df rows to the models
    
    # TODO: convert to model
