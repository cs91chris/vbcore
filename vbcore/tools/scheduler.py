import logging.config
from typing import TYPE_CHECKING

import click

from vbcore.datastruct.lazy import LazyImporter
from vbcore.tools.cli import CliInputFile, CliReqOpt
from vbcore.yaml import load_yaml_file

if TYPE_CHECKING:
    from vbcore.standalone.scheduler import APScheduler
else:
    APScheduler = LazyImporter.do_import(
        "vbcore.standalone.scheduler:APScheduler",
        message="you must install vbcore[scheduler]",
    )

main = click.Group(name="scheduler", help="start the scheduler")


@main.command("standalone")
@CliReqOpt.string("-c", "--config-file", envvar="CONFIG_FILE", type=CliInputFile())
def standalone(config_file):
    config = load_yaml_file(config_file)
    if "LOGGING" in config:
        logging.config.dictConfig(config["LOGGING"])

    handler = APScheduler.factory(config)
    handler.scheduler.start()
