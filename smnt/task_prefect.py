from datetime import datetime, timedelta
import prefect
from prefect.run_configs import DockerRun
from prefect import task, Flow
from prefect.schedules import IntervalSchedule

from smnt.scraping import get_current_weather_and_forecast
from smnt.database import Session
from smnt import models
from smnt.load import load

@task(max_retries=5, retry_delay=timedelta(minutes=1), nout=2)
def extract():
    return get_current_weather_and_forecast()

@task
def transform_load(current_weather, forecast):
    load(current_weather, forecast)


schedule = IntervalSchedule(
    start_date=datetime(2022,7,30,0) + timedelta(seconds=1),
    interval=timedelta(hours=1),
)

with Flow("SMN-ETL", schedule) as flow:
    current_weather, forecast = extract()
    transform_load(current_weather, forecast)

flow.register(project_name="SMNT")

# Configure extra environment variables for this flow,
# and set a custom image
flow.run_config = DockerRun(
    #env={"SOME_VAR": "VALUE"},
    image="smnt:latest"
)
