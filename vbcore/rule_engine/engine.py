import logging
import typing as t

from rule_engine import Context, resolve_item, Rule

from ..types import StrDict
from .base import RuleInfo, RuleType


class RuleEngine:
    def __init__(
        self,
        context: t.Optional[Context] = None,
        case_insensitive: bool = True,
        raise_exc: bool = False,
    ):
        self.raise_exc = raise_exc
        self.case_insensitive = case_insensitive
        self._context = context or Context(resolver=self.resolver)
        self._logger: logging.Logger = logging.getLogger(self.__module__)

    @property
    def context(self) -> Context:
        return self._context

    @context.setter
    def context(self, context: Context):
        self._context = context

    def resolver(self, thing, name: str):
        if self.case_insensitive is True:
            return resolve_item(thing, name.lower())
        return resolve_item(thing, name)

    def prepare_rule(self, rule: RuleType) -> Rule:
        if isinstance(rule, str):
            return Rule(rule, context=self.context)
        return rule

    def evaluate(self, rule: RuleType, data: dict) -> t.Any:
        rule = self.prepare_rule(rule)
        try:
            result = rule.evaluate(data)
            self._logger.debug("evaluated rule '%s', result: '%s'", rule, result)
            return result
        except Exception as exc:
            self._logger.exception(exc)
            if self.raise_exc is False:
                return None
            raise

    def matches(self, rule: RuleType, data: dict) -> bool:
        rule = self.prepare_rule(rule)
        try:
            result = rule.matches(data)
            self._logger.debug("rule '%s' %smatches", rule, "" if result else "not ")
            return result
        except Exception as exc:
            self._logger.exception(exc)
            if self.raise_exc is False:
                return False
            raise

    def apply(
        self, rules: t.List[RuleInfo], data: dict
    ) -> t.Generator[t.Tuple[RuleInfo, t.Any], None, None]:
        for rule in rules:
            self._logger.debug("executing rule: %s", rule.id)
            if rule.evaluate:
                result = self.evaluate(rule.rule, data)
            else:
                result = self.matches(rule.rule, data)
            yield rule, result

    def which_matches(self, rules: t.List[RuleInfo], data: dict) -> t.List[RuleInfo]:
        cursor = self.apply(rules, data)
        return [match[0] for match in filter(lambda x: bool(x[1]) is True, cursor)]

    def first_match(self, rules: t.List[RuleInfo], data: dict) -> t.Optional[RuleInfo]:
        for result in self.apply(rules, data):
            if result[1] is True:
                return result[0]
        return None

    def perform_on_match(
        self, rules: t.List[RuleInfo], data: dict, *args, **kwargs
    ) -> StrDict:
        results: StrDict = {}
        for rule, result in self.apply(rules, data):
            if rule.evaluate is True or result is True:
                results[rule.id] = rule.action.perform(
                    data, *args, rule=rule, rule_result=result, **kwargs
                )
        return results
