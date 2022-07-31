import re
import requests
import json
import pandas as pd
from smnt.config import LOCATION_ID, FORECAST_URL, WEATHER_URL, JWT_URL

def get_jwt_token():
    html_pronostico = requests.get(JWT_URL).content
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

def get_current_weather_and_forecast():
    jwt = get_jwt_token()
    forecast_df = get_forecast(jwt)
    current_weather = get_current_weather(jwt)
    return current_weather, forecast_df