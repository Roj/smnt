"""CLI entrypoint for ETL"""
from datetime import datetime

import typer

from smnt.load import load
from smnt.scraping import get_current_weather_and_forecast


def etl():
    """Scrap weather, forecast and load to sqlite db"""
    typer.echo(f"[{datetime.now()}] Running ETL")
    current_weather, forecast = get_current_weather_and_forecast()
    load(current_weather, forecast)
    typer.echo(f"[{datetime.now()}] .. done!")


def main():
    """Main entrypoint for CLI"""
    typer.run(etl)


if __name__ == "__main__":
    main()
