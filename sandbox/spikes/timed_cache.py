import time

from vbcore.datastruct.cache import TimedLRUCache

cache = TimedLRUCache(seconds=1)


@cache
def sample(data: str):
    print("executing function with:", data)
    return data.upper()


if __name__ == "__main__":
    print("result:", sample("aaa"))
    print("result:", sample("aaa"))
    time.sleep(1)
    print("result:", sample("bbb"))
    print("result:", sample("aaa"))
    print("result:", sample("bbb"))
