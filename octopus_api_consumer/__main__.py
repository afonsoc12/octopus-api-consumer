#!/usr/bin/env python3

# Execute with
# $ python octopus_api_consumer/__main__.py
# $ python -m octopus_api_consumer

import logging
import sys
from datetime import date, timedelta

import click as click

from octopus_api_consumer.influx import InfluxDB
from octopus_api_consumer.octopus import Octopus

if __package__ is None and not hasattr(sys, "frozen"):
    # Direct call of __main__.py
    import os.path

    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))


@click.command()
@click.option(
    "--period-start",
    type=click.DateTime(),
    default=(date.today() - timedelta(days=1)).isoformat(),
    help="Start timestamp to fetch data",
)
@click.option(
    "--period-end",
    type=click.DateTime(),
    default=None,
    help="End timestamp to fetch data",
)
@click.option(
    "--test",
    is_flag=True,
    help="Test flag. Bypasses storing data points and outputs to stdout",
)
def main(period_start, period_end, test):
    inf = InfluxDB()
    o = Octopus()

    cons = o.consumption(period_from=period_start, period_to=period_end)

    logging.debug(
        f"Got {len(cons)} consumption points, from {cons[0].interval_start} to"
        f" {cons[-1].interval_end}"
    )

    if test:
        logging.info(cons)
    else:
        inf.write_consumptions(cons)
        print()


if __name__ == "__main__":
    main()
