import dataclasses
import typing as t

import psutil

from vbcore.base import BaseDTO
from vbcore.datastruct import ObjectDict


@dataclasses.dataclass(frozen=True)
class SwapStat(BaseDTO):
    total: int
    percent: float
    used: int
    free: int
    sin: int = 0
    sout: int = 0


@dataclasses.dataclass(frozen=True)
class MemoryStat(BaseDTO):  # pylint: disable=too-many-instance-attributes
    total: int
    available: int
    percent: float
    used: int
    free: int
    active: int
    inactive: int
    buffers: int
    cached: int
    shared: int
    slab: int
    swap: SwapStat


@dataclasses.dataclass(frozen=True)
class CpuFreq(BaseDTO):
    current: float
    min: float
    max: float


@dataclasses.dataclass(frozen=True)
class CpuTimes(BaseDTO):
    user: float
    nice: float
    system: float
    idle: float
    iowait: float
    irq: float
    softirq: float
    steal: float
    guest: float
    guest_nice: float


@dataclasses.dataclass(frozen=True)
class CpuStat(BaseDTO):
    count: int
    percent: float
    freq: CpuFreq
    times: CpuTimes


@dataclasses.dataclass(frozen=True)
class DiskStat(BaseDTO):
    total: int
    percent: float
    used: int
    free: int


@dataclasses.dataclass(frozen=True)
class NetStat(BaseDTO):
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errin: int
    errout: int
    dropin: int = 0
    dropout: int = 0


class SysStats:
    @classmethod
    def memory_stats(cls) -> MemoryStat:
        # noinspection PyProtectedMember
        memory = ObjectDict(**psutil.virtual_memory()._asdict())
        # noinspection PyProtectedMember
        swap = ObjectDict(**psutil.swap_memory()._asdict())
        return MemoryStat(
            total=memory.total,
            available=memory.available,
            percent=memory.percent,
            used=memory.used,
            free=memory.free,
            active=memory.active,
            inactive=memory.inactive,
            buffers=memory.buffers,
            cached=memory.cached,
            shared=memory.shared,
            slab=memory.slab,
            swap=SwapStat(
                total=swap.total,
                percent=swap.percent,
                used=swap.used,
                free=swap.free,
                sin=swap.sin,
                sout=swap.sout,
            ),
        )

    @classmethod
    def cpu_stats(cls) -> CpuStat:
        # noinspection PyProtectedMember
        freq = ObjectDict(**psutil.cpu_freq()._asdict())
        # noinspection PyProtectedMember
        times = ObjectDict(**psutil.cpu_times_percent()._asdict())
        return CpuStat(
            count=psutil.cpu_count(),
            percent=psutil.cpu_percent(),
            freq=CpuFreq(
                current=freq.current,
                min=freq.min,
                max=freq.max,
            ),
            times=CpuTimes(
                user=times.user,
                nice=times.nice,
                system=times.system,
                idle=times.idle,
                iowait=times.iowait,
                irq=times.irq,
                softirq=times.softirq,
                steal=times.steal,
                guest=times.guest,
                guest_nice=times.guest_nice,
            ),
        )

    @classmethod
    def disk_stats(cls) -> t.Dict[str, DiskStat]:
        resp: t.Dict[str, DiskStat] = {}
        for fs in psutil.disk_partitions():
            # noinspection PyProtectedMember
            usage = ObjectDict(**psutil.disk_usage(fs.mountpoint)._asdict())
            resp[fs.mountpoint] = DiskStat(
                total=usage.total,
                percent=usage.percent,
                used=usage.used,
                free=usage.free,
            )
        return resp

    @classmethod
    def net_stats(cls) -> t.Dict[str, NetStat]:
        responses: t.Dict[str, NetStat] = {}
        for nic, netio in dict(psutil.net_io_counters(pernic=True)).items():
            # noinspection PyProtectedMember
            data = ObjectDict(**netio._asdict())
            responses[nic] = NetStat(
                bytes_sent=data.bytes_sent,
                bytes_recv=data.bytes_recv,
                packets_sent=data.packets_sent,
                packets_recv=data.packets_recv,
                errin=data.errin,
                errout=data.errout,
                dropin=data.dropin,
                dropout=data.dropout,
            )
        return responses
