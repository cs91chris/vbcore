import typing as t
from dataclasses import dataclass

from user_agents import parsers

from vbcore.base import BaseDTO


@dataclass(frozen=True)
class Version(BaseDTO):
    string: str
    number: int

    def __str__(self):
        return f"{self.string}"


@dataclass(frozen=True)
class Client(BaseDTO):
    family: str
    version: Version

    def __str__(self):
        return f"{self.family} {self.version}"


@dataclass(frozen=True)
class DeviceType(BaseDTO):
    computer: bool
    bot: bool
    mobile: bool
    tablet: bool
    email_client: bool
    touch_capable: bool


@dataclass(frozen=True)
class Device(BaseDTO):
    family: str
    brand: str
    model: str
    type: DeviceType


@dataclass(frozen=True)
class UserAgent(BaseDTO):
    parser_class: t.ClassVar[t.Type[parsers.UserAgent]] = parsers.UserAgent

    raw: str
    operating_system: Client
    browser: Client
    device: Device

    def __str__(self):
        return self.raw

    @classmethod
    def parse(cls, user_agent: str) -> "UserAgent":
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
