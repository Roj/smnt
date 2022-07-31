"""Scraping utilities for web service"""
import re
import json
from typing import Dict, Tuple

import requests
import pandas as pd

from smnt.config import JWT_URL, LOCATION_ID, WEATHER_URL, FORECAST_URL


def get_jwt_token() -> str:
    """Request a JWT token from the service.
    The token must be used for follow up queries.

    Returns
    -------
    str
        JSON Web Token (JWT).
    """
    html_pronostico = requests.get(JWT_URL).content
    obj = re.search(
        r"localStorage\.setItem\('token', '([A-z0-9\.\-]+)'\);",
        html_pronostico.decode("utf-8"),
    )
    jwt = obj.group(1)
    return jwt


def query_endpoint_with_jwt(endpoint: str, jwt: str) -> Dict:
    """Generic GET request with a JSON Web Token.
    Returns JSON output as dict.

    Parameters
    ----------
    endpoint : str
        Endpoint URL.
    jwt : str
        JSON Web Token.

    Returns
    -------
    Dict
        Loaded JSON response.
    """
    auth_header = f"JWT {jwt}"
    response = requests.get(
        endpoint, headers={"Authorization": auth_header, "Accept": "application/json"}
    )
    return json.loads(response.content.decode("utf-8"))


def get_forecast(jwt: str) -> pd.DataFrame:
    """Get forecast dataframe.

    Parameters
    ----------
    jwt : str
        JSON Web Token.

    Returns
    -------
    pd.DataFrame
        Forecast dataframe.
    """
    forecast_data = query_endpoint_with_jwt(FORECAST_URL, jwt)
    forecast_df = pd.DataFrame(forecast_data["forecast"])
    return forecast_df


def get_current_weather(jwt: str, location: int = LOCATION_ID) -> pd.DataFrame:
    """Get current weather for given location.

    Parameters
    ----------
    jwt : str
        JSON Web Token.
    location : int, optional
        Location id to query for, by default smnt.config.LOCATION_ID

    Returns
    -------
    pd.DataFrame
        Current weather for location.
    """
    now = query_endpoint_with_jwt(WEATHER_URL, jwt)
    df_now = pd.DataFrame(now)
    df_now["location_name"] = df_now.location.map(lambda loc: loc["name"])
    df_now["location_id"] = df_now.location.map(lambda loc: loc["id"])
    caba_ahora = df_now.loc[df_now.location_id == location]
    return caba_ahora


def get_current_weather_and_forecast() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Wrapper that obtains both current weather and forecast.
    Automatically queries for a JSON Web Token.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        Current weather and forecast dataframes.
    """
    jwt = get_jwt_token()
    forecast_df = get_forecast(jwt)
    current_weather = get_current_weather(jwt)
    return current_weather, forecast_df
