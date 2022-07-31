"""ETL Dag for main task"""
import datetime

import pendulum
from airflow.decorators import dag, task

from smnt.load import load
from smnt.scraping import get_current_weather_and_forecast


@dag(
    schedule_interval=datetime.timedelta(hours=1),
    start_date=pendulum.datetime(2022, 7, 31, tz="UTC"),
    catchup=False,
    tags=["etl"],
)
def smnt_etl():
    """
    ### ETL
    ETL for the SMN't service.
    """

    @task()
    def etl():
        """###ETL main task"""
        current_weather, forecast = get_current_weather_and_forecast()
        load(current_weather, forecast)

    etl()


smnt_etl_dag = smnt_etl()  #  pylint: disable=invalid-name
