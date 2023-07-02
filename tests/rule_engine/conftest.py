import typing as t

import pytest

from vbcore.rule_engine import ActionRule, RuleEngine, RuleInfo


@pytest.fixture
def engine() -> RuleEngine:
    return RuleEngine()


@pytest.fixture
def sample_data() -> dict:
    return {
        "first_name": "Luke",
        "last_name": "Skywalker",
        "email": "luke@rebels.org",
    }


class SampleActionRule(ActionRule):
    def perform(
        self,
        data: t.Any,
        *_,
        rule: t.Optional["RuleInfo"] = None,
        rule_result: t.Any = None,
        **__,
    ) -> str:
        return f"[{rule.id}][{rule_result}]"


@pytest.fixture
def sample_rules() -> t.Tuple[RuleInfo, ...]:
    return (
        RuleInfo(
            id="rule-1",
            action=SampleActionRule(),
            rule="first_name == 'Kage'",
        ),
        RuleInfo(
            id="rule-2",
            action=SampleActionRule(),
            rule="FIRST_NAME == 'Luke'",
        ),
        RuleInfo(
            id="rule-3",
            action=SampleActionRule(),
            rule="last_name == 'Skywalker'",
        ),
        RuleInfo(
            id="rule-4",
            action=SampleActionRule(),
            evaluate=True,
            rule="first_name + ' ' + last_name",
        ),
    )
