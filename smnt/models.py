from sqlalchemy import Column, Integer, Float, DateTime, Date, String, ForeignKey, declarative_base

Base = declarative_base()

class PeriodPrediction(Base):
    __tablename__ = "period_prediction"
    # Identifying info
    datetime = Column(DateTime)
    predicted_date = Column(Date)
    period_name = Column(String)
    prediction_id = Column(Integer, primary_key=True)
    # Values
    humidity = Column(Float)
    probability_rain_min = Column(Float)
    probability_rain_max = Column(Float)
    temperature = Column(Float)
    gust_range_min = Column(Float)
    gust_range_max = Column(Float)
    weather_description = Column(String)
    weather_description_id = Column(Integer)
    wind_direction = Column(String)
    wind_degrees = Column(Float)
    wind_speed_min = Column(Float)
    wind_speed_max = Column(Float)

class DayPrediction(Base):
    __tablename__ = "day_prediction"
    datetime = Column(DateTime)
    location_id = Column(Integer)
    predicted_date = Column(Date)
    temperature_min = Column(Float)
    temperature_max = Column(Float)
    humidity_min = Column(Float)
    humidity_max = Column(Float)
    early_morning = Column(Integer, ForeignKey("period_prediction.prediction_id"))
    morning = Column(Integer, ForeignKey("period_prediction.prediction_id"))
    afternoon = Column(Integer, ForeignKey("period_prediction.prediction_id"))
    night = Column(Integer, ForeignKey("period_prediction.prediction_id"))


class ActualWeather(Base):
    __tablename__ = "actual_weather"
    datehour = Column(DateTime)
    humidity = Column(Float)
    pressure = Column(Float)
    feels_like = Column(Float)
    temperature = Column(Float)
    visibility = Column(Float)
    weather_description = Column(String)
    weather_description_id = Column(Integer)
    wind_direction = Column(String)
    wind_degrees = Column(Float)
    wind_speed = Column(Float)
    location_id = Column(Integer)
    location_name = Column(String)
