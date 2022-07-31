import datetime
from smnt.models import DayPrediction, ActualWeather, PeriodPrediction
from smnt.config import LOCATION_ID
from sqlalchemy.orm import Session
from smnt.database import Session

def actual_weather_from_row(caba_ahora):

    return ActualWeather(
        datehour = datetime.datetime.fromisoformat(caba_ahora.date),
        humidity = caba_ahora.humidity,
        pressure = caba_ahora.pressure,
        feels_like = caba_ahora.feels_like,
        temperature = caba_ahora.temperature,
        visibility = caba_ahora.visibility,
        weather_description = caba_ahora.weather["description"],
        weather_description_id = caba_ahora.weather["id"],
        wind_direction = caba_ahora.wind["direction"],
        wind_degrees = caba_ahora.wind["deg"],
        wind_speed = caba_ahora.wind["speed"],
        location_id = caba_ahora.location_id,
        location_name = caba_ahora.location_name,
    )

def period_preds_from_row(row, datehour):
    period_preds = []
    for period_name in ["early_morning", "morning", "afternoon", "night"]:
        period = getattr(row, period_name)
        if period is None:
            #period_preds.append(None)
            continue
        period_pred = PeriodPrediction(
            datetime=datehour,
            predicted_date=datetime.date.fromisoformat(row.date),
            period_name=period_name,
            #day_prediction_id = ??,
            humidity=period["humidity"],
            probability_rain_min=period["rain_prob_range"][0],
            probability_rain_max=period["rain_prob_range"][1],
            temperature=period["temperature"],
            gust_range_min=0 if period["gust_range"] is None else period["gust_range"][0],
            gust_range_max=0 if period["gust_range"] is None else period["gust_range"][1],
            weather_description=period["weather"]["description"],
            weather_description_id=period["weather"]["id"],
            wind_direction=period["wind"]["direction"],
            wind_degrees=period["wind"]["deg"],
            wind_speed_min=period["wind"]["speed_range"][0],
            wind_speed_max=period["wind"]["speed_range"][1],
        )
        period_preds.append(period_pred)
    return period_preds

def day_pred_from_row(row, datehour, location_id):
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

def load(current_weather, forecast):
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