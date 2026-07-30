from datetime import datetime, timedelta

from node_classifier import classify_node

NOW = datetime(2024, 1, 1, 12, 0, 0)


def _last_heard(hours_ago):
    return (NOW - timedelta(hours=hours_ago)).timestamp()


def test_no_last_heard():
    assert classify_node("!abc", None, set(), set(), NOW) == "no_last_heard"


def test_exactly_at_threshold_is_not_stale():
    last_heard = _last_heard(2)
    assert classify_node("!abc", last_heard, set(), set(), NOW) == "new"


def test_just_past_threshold_is_stale():
    last_heard = _last_heard(2) - 1
    assert classify_node("!abc", last_heard, set(), set(), NOW) == "stale"


def test_fresh_and_already_logged():
    last_heard = _last_heard(1)
    assert classify_node("!abc", last_heard, set(), {"!abc"}, NOW) == "already_logged"


def test_fresh_not_logged_not_existing_is_new():
    last_heard = _last_heard(1)
    assert classify_node("!abc", last_heard, set(), set(), NOW) == "new"


def test_fresh_not_logged_already_existing_is_known():
    last_heard = _last_heard(1)
    assert classify_node("!abc", last_heard, {"!abc"}, set(), NOW) == "known"
