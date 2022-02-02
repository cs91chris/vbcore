import pytest

from vbcore.tester.mixins import Asserter


def test_retrieve(support, session_save):
    session_save(
        [
            support.model(id=1, name="name-1"),
            support.model(id=2, name="name-2"),
            support.model(id=3, name="name-3"),
        ]
    )

    sample_id = 3
    record = support.fetch(id=sample_id).one()
    Asserter.assert_equals(record.id, sample_id)
    Asserter.assert_equals(record.name, f"name-{sample_id}")


def test_delete(support, session_save):
    session_save(
        [
            support.model(id=1, name="name-1"),
            support.model(id=2, name="name-2"),
            support.model(id=3, name="name-3"),
        ]
    )

    deleted = support.delete(id=2)
    Asserter.assert_equals(deleted, 1)
    records = support.fetch().all()
    Asserter.assert_equals(len(records), 2)


def test_bulk_insert(support):
    records = [
        support.model(id=1, name="name-1"),
        support.model(id=2, name="name-2"),
        support.model(id=3, name="name-3"),
    ]

    assert len(support.fetch().all()) == 0
    support.bulk_insert(records)
    assert len(support.fetch().all()) == 3


def test_bulk_upsert(support):
    load_step_1 = [
        support.model(id=1, name="name-1"),
        support.model(id=2, name="name-2"),
        support.model(id=3, name="name-3"),
    ]

    load_step_2 = [
        support.model(id=1, name="name-1"),
        support.model(id=2, name="name-2"),
        support.model(id=3, name="name-3"),
        support.model(id=4, name="name-4"),
    ]

    support.bulk_upsert(load_step_1)
    support.bulk_upsert(load_step_2)

    Asserter.assert_equals(len(support.fetch().all()), 4)


@pytest.mark.parametrize(
    "res_id, name",
    [
        (1, "test-1"),
        (2, "test-2"),
    ],
    ids=["update", "create"],
)
def test_update_or_create(res_id, name, support):
    support.bulk_insert([support.model(id=1, name="name-1")])

    support.update_or_create({"name": name}, id=res_id)
    record = support.fetch().get(res_id)
    Asserter.assert_equals(record.name, name)
