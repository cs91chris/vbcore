from vbcore.tester.asserter import Asserter


def test_evaluate(engine, sample_data):
    rule = 'first_name + " " + last_name'
    result = engine.evaluate(rule, sample_data)
    Asserter.assert_equals(result, "Luke Skywalker")


def test_matches(engine, sample_data):
    rule = 'first_name == "Luke" and email =~ ".*@rebels.org$"'
    Asserter.assert_true(engine.matches(rule, sample_data))

    rule = 'first_name == "Kage"'
    Asserter.assert_false(engine.matches(rule, sample_data))


def test_which_matches(engine, sample_data, sample_rules: tuple):
    rule_1, rule_2, rule_3, rule_4 = sample_rules
    rules = [rule_1, rule_2, rule_3, rule_4]
    result = engine.which_matches(rules, sample_data)
    Asserter.assert_equals(result, [rule_2, rule_3, rule_4])


def test_first_match(engine, sample_data, sample_rules: tuple):
    rule_1, rule_2, rule_3, _ = sample_rules
    rules = [rule_1, rule_2, rule_3]
    result = engine.first_match(rules, sample_data)
    Asserter.assert_equals(result, rule_2)


def test_perform_on_match(engine, sample_data, sample_rules: tuple):
    result = engine.perform_on_match(sample_rules, sample_data)
    Asserter.assert_equals(
        result,
        {
            "rule-2": "[rule-2][True]",
            "rule-3": "[rule-3][True]",
            "rule-4": "[rule-4][Luke Skywalker]",
        },
    )
