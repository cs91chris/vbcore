import functools

import click

from vbcore import aio
from vbcore.brokers.consumer import Consumer
from vbcore.brokers.data import Header
from vbcore.brokers.factory import BrokerEnum, BrokerFactory
from vbcore.brokers.publisher import Publisher
from vbcore.importer import Importer
from vbcore.tools.cli import CliOpt, CliReqOpt
from vbcore.types import OptStr, StrList

main = click.Group(name="broker", help="broker client handler")


def common_options(func):
    @CliOpt.choice("-b", "--broker", default="DUMMY", values=BrokerEnum.items())
    @CliReqOpt.string("-s", "--server", envvar="BROKER_SERVER")
    @CliOpt.dict("options", "-o", "--option")
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@main.command(name="publish", help="publish message on topic")
@common_options
@CliReqOpt.string("-t", "--topic")
@CliOpt.string("-m", "--message")
@CliOpt.dict("data", "-D", "--data")
@CliOpt.dict("headers", "-H", "--header")
def publish(
    broker: str, topic: str, server: str, options: dict, message: OptStr, data: dict, headers: dict
):
    publisher = Publisher(BrokerFactory.instance(broker, servers=server, **options))
    aio.execute(publisher.raw_publish(topic, message or data, Header.from_dict(**headers)))


@main.command(name="subscribe", help="subscribe and consume messages")
@common_options
@CliOpt.multi("callbacks", "-C", "--callback")
def subscribe(broker: str, server: str, options: dict, callbacks: StrList):
    instance = BrokerFactory.instance(broker, servers=server, **options)
    cbs = [Importer.from_module(cb, call_with=True) for cb in callbacks]

    async def wrapper():
        consumer = Consumer(instance, callbacks=cbs)
        await consumer.run()

    aio.execute(wrapper())
