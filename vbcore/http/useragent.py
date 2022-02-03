import dataclasses
import typing as t

from user_agents import parsers

from vbcore.datastruct import DataClassDictable


@dataclasses.dataclass(frozen=True)
class Version(DataClassDictable):
    string: str
    number: int

    def __str__(self):
        return f"{self.string}"


@dataclasses.dataclass(frozen=True)
class Client(DataClassDictable):
    family: str
    version: Version

    def __str__(self):
        return f"{self.family} {self.version}"


@dataclasses.dataclass(frozen=True)
class DeviceType(DataClassDictable):
    computer: bool
    bot: bool
    mobile: bool
    tablet: bool
    email_client: bool
    touch_capable: bool


@dataclasses.dataclass(frozen=True)
class Device(DataClassDictable):
    family: str
    brand: str
    model: str
    type: DeviceType


@dataclasses.dataclass(frozen=True)
class UserAgent(DataClassDictable):
    parser_class: t.ClassVar[t.Type[parsers.UserAgent]] = parsers.UserAgent

    raw: str
    operating_system: Client
    browser: Client
    device: Device

    def __str__(self):
        return f"{self.device} / {self.operating_system} / {self.browser}"

    @classmethod
    def parse(cls, user_agent: str):
        parsed = cls.parser_class(user_agent)

        return cls(
            raw=parsed.ua_string,
            browser=Client(
                family=parsed.browser.family,
                version=Version(
                    number=parsed.browser.version,
                    string=parsed.browser.version_string,
                ),
            ),
            operating_system=Client(
                family=parsed.os.family,
                version=Version(
                    number=parsed.os.version,
                    string=parsed.os.version_string,
                ),
            ),
            device=Device(
                family=parsed.device.family,
                brand=parsed.device.brand,
                model=parsed.device.model,
                type=DeviceType(
                    mobile=parsed.is_mobile,
                    tablet=parsed.is_tablet,
                    computer=parsed.is_pc,
                    bot=parsed.is_bot,
                    email_client=parsed.is_email_client,
                    touch_capable=parsed.is_touch_capable,
                ),
            ),
        )
