import logging.config

import click

try:
    from vbcore.standalone.scheduler import APScheduler
except ImportError:
    APScheduler = None  # type: ignore

from vbcore.yaml import load_yaml_file

main = click.Group(name="scheduler", help="start the scheduler")


@main.command("standalone")
@click.option(
    "-c",
    "--config-file",
    required=True,
    show_envvar=True,
    envvar="CONFIG_FILE",
    type=click.Path(exists=True, readable=True, file_okay=True, dir_okay=False),
)
def standalone(config_file):
    if APScheduler is None:
        raise ImportError("you must install vbcore[scheduler]")

    config = load_yaml_file(config_file)
    if "LOGGING" in config:
        logging.config.dictConfig(config["LOGGING"])

    handler = APScheduler.factory(config)
    handler.scheduler.start()
