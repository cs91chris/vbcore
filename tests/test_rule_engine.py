import unittest

from vbcore.rule_engine import RuleEngine, RuleInfo


class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RuleEngine()
        self.sample = {
            "case_sensitive": "case_sensitive",
            "first_name": "Luke",
            "last_name": "Skywalker",
            "email": "luke@rebels.org",
        }

    def test_apply(self):
        result = self.engine.apply(
            [
                RuleInfo(id="01", rule='case_sensitive == "case_sensitive"'),
                RuleInfo(id="02", rule='CASE_SENSITIVE == "case_sensitive"'),
                RuleInfo(id="03", rule='Case_Sensitive == "case_sensitive"'),
                RuleInfo(id="simple_match", rule='last_name == "Skywalker"'),
                RuleInfo(id="simple_no_match", rule='last_name == "Vader"'),
                RuleInfo(
                    id="complex",
                    rule='first_name == "Luke" and email =~ ".*@rebels.org$"',
                ),
                RuleInfo(id="invalid_operation", rule="first_name + 1"),
                RuleInfo(id="invalid_rule", rule="abcdef"),
            ],
            self.sample,
        )

        self.assertEqual(
            {rule.id: resp for rule, resp in result},
            {
                "01": True,
                "02": True,
                "03": True,
                "simple_match": True,
                "simple_no_match": False,
                "complex": True,
                "invalid_operation": False,
                "invalid_rule": False,
            },
        )

    def test_which_matches(self):
        result = self.engine.which_matches(
            [
                RuleInfo(id="match_1", rule='first_name == "Luke"'),
                RuleInfo(id="no_match", rule='first_name == "FAKE"'),
                RuleInfo(id="match_2", rule='last_name == "Skywalker"'),
            ],
            self.sample,
        )
        self.assertEqual(list(r.id for r in result), ["match_1", "match_2"])

    def test_first_match(self):
        result = self.engine.first_match(
            [
                RuleInfo(id="no_match_1", rule='first_name == "FAKE 1"'),
                RuleInfo(id="this match", rule='first_name == "Luke"'),
                RuleInfo(id="no_match_2", rule='first_name == "FAKE 2"'),
            ],
            self.sample,
        )
        self.assertEqual(result.id, "this match")
