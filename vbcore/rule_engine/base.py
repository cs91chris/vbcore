import typing as t
from abc import ABC, abstractmethod
from dataclasses import dataclass

from rule_engine import Rule

RuleType = t.Union[str, Rule]


class ActionRule(ABC):
    @abstractmethod
    def perform(
        self,
        data: t.Any,
        *args,
        rule: t.Optional["RuleInfo"] = None,
        rule_result: t.Any = None,
        **kwargs,
    ) -> t.Any:
        """perform the action rule"""


class NoneActionRule(ActionRule):
    def perform(
        self,
        data: t.Any,
        *args,
        rule: t.Optional["RuleInfo"] = None,
        rule_result: t.Any = None,
        **kwargs,
    ) -> t.Any:
        """no operation are performed and none are returned"""


class IdentityActionRule(ActionRule):
    def perform(
        self,
        data: t.Any,
        *args,
        rule: t.Optional["RuleInfo"] = None,
        rule_result: t.Any = None,
        **kwargs,
    ) -> t.Any:
        """no operation are performed and return the data as is"""
        return data


@dataclass(frozen=True)
class RuleInfo:
    id: str  # pylint: disable=invalid-name
    rule: RuleType
    evaluate: bool = False
    action: t.Optional[ActionRule] = NoneActionRule()

    def __str__(self) -> str:
        return f"<{self.id} - {self.rule}>"
