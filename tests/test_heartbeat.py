from asyncio import new_event_loop

from vbcore.heartbeat import Heartbeat


def test_run() -> None:
    pulses = 5
    delay = 0.01

    loop = new_event_loop()
    heartbeat = Heartbeat(delay=delay, loop=loop)
    loop.call_later(pulses * delay, heartbeat.shutdown)
    heartbeat.start()

    loop.run_until_complete(heartbeat.run_forever())
    # TODO assert the heartbeat
