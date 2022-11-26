import logging.config

import click

from vbcore.tools.cli import Cli, CliInputFile, CliReqOpt

try:
    from vbcore.standalone.scheduler import APScheduler
except ImportError:
    APScheduler = None  # type: ignore

from vbcore.yaml import load_yaml_file

main = click.Group(name="scheduler", help="start the scheduler")


@main.command("standalone")
@CliReqOpt.string("-c", "--config-file", envvar="CONFIG_FILE", type=CliInputFile())
def standalone(config_file):
    if APScheduler is None:
        Cli.abort("you must install vbcore[scheduler]")

    config = load_yaml_file(config_file)
    if "LOGGING" in config:
        logging.config.dictConfig(config["LOGGING"])

    handler = APScheduler.factory(config)
    handler.scheduler.start()
