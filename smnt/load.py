"""Transformers and loaders to DB"""
import datetime
from typing import List

import pandas as pd

from smnt.database import Session
from smnt.config import LOCATION_ID
from smnt.models import ActualWeather, DayPrediction, PeriodPrediction


def actual_weather_from_row(current_weather: pd.Series) -> ActualWeather:
    """Construct an ActualWeather object from a pandas series.

    Parameters
    ----------
    current_weather : pd.Series
        Pandas series obtained from scraping an endpoint.

    Returns
    -------
    ActualWeather
    """
    return ActualWeather(
        datehour=datetime.datetime.fromisoformat(current_weather.date),
        humidity=current_weather.humidity,
        pressure=current_weather.pressure,
        feels_like=current_weather.feels_like,
        temperature=current_weather.temperature,
        visibility=current_weather.visibility,
        weather_description=current_weather.weather["description"],
        weather_description_id=current_weather.weather["id"],
        wind_direction=current_weather.wind["direction"],
        wind_degrees=current_weather.wind["deg"],
        wind_speed=current_weather.wind["speed"],
        location_id=current_weather.location_id,
        location_name=current_weather.location_name,
    )


def period_preds_from_row(
    row: pd.Series, datehour: datetime.datetime
) -> List[PeriodPrediction]:
    """Construct PeriodPrediction objects from a forecast row.
    Uses a contextual datehour to set the prediction time.

    Parameters
    ----------
    row : pd.Series
        Forecast row, including each period's prediction (early morning, etc.)
    datehour : datetime.datetime
        Prediction timestamp, truncated to hour resolution.

    Returns
    -------
    List[PeriodPrediction]
        List of period predictions. The list has as many elements as valid predictions there are
        in the row.
    """
    period_preds = []
    for period_name in ["early_morning", "morning", "afternoon", "night"]:
        period = getattr(row, period_name)
        if period is None:
            continue
        period_pred = PeriodPrediction(
            datetime=datehour,
            predicted_date=datetime.date.fromisoformat(row.date),
            period_name=period_name,
            humidity=period["humidity"],
            probability_rain_min=period["rain_prob_range"][0],
            probability_rain_max=period["rain_prob_range"][1],
            temperature=period["temperature"],
            gust_range_min=0
            if period["gust_range"] is None
            else period["gust_range"][0],
            gust_range_max=0
            if period["gust_range"] is None
            else period["gust_range"][1],
            weather_description=period["weather"]["description"],
            weather_description_id=period["weather"]["id"],
            wind_direction=period["wind"]["direction"],
            wind_degrees=period["wind"]["deg"],
            wind_speed_min=period["wind"]["speed_range"][0],
            wind_speed_max=period["wind"]["speed_range"][1],
        )
        period_preds.append(period_pred)
    return period_preds


def day_pred_from_row(
    row: pd.Series, datehour: datetime.datetime, location_id: int
) -> DayPrediction:
    """Generate a day prediction from a forecast row, a contextual prediction time,
    and the location id for which the prediction was made.
    Generates PeriodPredictions by cascade.

    Parameters
    ----------
    row : pd.Series
        Forecast row.
    datehour : datetime.datetime
        Contextual prediction time, truncated to hour resolution.
    location_id : int
        Location ID for the prediction.

    Returns
    -------
    DayPrediction
    """
    period_preds = period_preds_from_row(row, datehour)
    day_pred = DayPrediction(
        datetime=datehour,
        location_id=location_id,
        predicted_date=datetime.date.fromisoformat(row.date),
        temperature_min=row.temp_min,
        temperature_max=row.temp_max,
        humidity_min=row.humidity_min,
        humidity_max=row.humidity_max,
    )
    if period_preds:
        day_pred.period_predictions.extend(period_preds)
    return day_pred


def load(current_weather: pd.DataFrame, forecast: pd.DataFrame) -> None:
    """Create objects for scraped current weather and forecast,
    and load them into the DB.

    Parameters
    ----------
    current_weather : pd.DataFrame
        Current weather dataframe.
        Only first row will be used.
    forecast : pd.DataFrame
        Forecast dataframe.
    """
    actual_weather_obj = actual_weather_from_row(current_weather.iloc[0])

    forecast_objects = []
    now = datetime.datetime.now()
    now_datehour = datetime.datetime(now.year, now.month, now.day, now.hour)
    for row in forecast.itertuples():
        forecast_objects.append(day_pred_from_row(row, now_datehour, LOCATION_ID))

    with Session() as session:
        for obj in forecast_objects:
            session.add(obj)
        session.add(actual_weather_obj)
        session.commit()
