from smnt.models import DayPrediction, ActualWeather, PeriodPrediction
def actual_weather_from_row(caba_ahora):

    return ActualWeather(
        datehour = caba_ahora.date,
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
            period_preds.append(None)
            continue
        period_pred = PeriodPrediction(
            datetime=datehour,
            predicted_date=row.date,
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
    return DayPrediction(
        datetime=datehour,
        location_id=location_id,
        predicted_date=row.date,
        temperature_min=row.temp_min,
        temperature_max=row.temp_max,
        humidity_min=row.humidity_min,
        humidity_max=row.humidity_max,
        early_morning=period_preds[0],
        morning=period_preds[1],
        afternoon=period_preds[2],
        night=period_preds[3],
    )