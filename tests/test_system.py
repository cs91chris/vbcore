from vbcore.system import (
    CpuFreq,
    CpuStat,
    CpuTimes,
    DiskStat,
    MemoryStat,
    NetStat,
    SwapStat,
    SysStats,
)
from vbcore.tester.asserter import Asserter


def test_memory_stats():
    stats = SysStats.memory_stats()
    Asserter.assert_true(isinstance(stats, MemoryStat))
    Asserter.assert_true(isinstance(stats.swap, SwapStat))


def test_cpu_stats():
    stats = SysStats.cpu_stats()
    Asserter.assert_true(isinstance(stats, CpuStat))
    Asserter.assert_true(isinstance(stats.freq, CpuFreq))
    Asserter.assert_true(isinstance(stats.times, CpuTimes))


def test_disk_stats():
    stats = SysStats.disk_stats()
    for stat in stats.values():
        Asserter.assert_true(isinstance(stat, DiskStat))


def test_net_stats():
    stats = SysStats.net_stats()
    for stat in stats.values():
        Asserter.assert_true(isinstance(stat, NetStat))
