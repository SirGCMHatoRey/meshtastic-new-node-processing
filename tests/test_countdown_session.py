from types import SimpleNamespace

from countdown_session import _dispatch_key

FOCUSED = "K3ANO: newNodes Welcome to AustinMESH"
UNFOCUSED = "Some Other Window"


def test_dispatch_calls_action_when_focused():
    calls = []
    key_actions = {'l': lambda: calls.append('l')}

    stopped = _dispatch_key(SimpleNamespace(char='l'), FOCUSED, key_actions)

    assert calls == ['l']
    assert stopped is False


def test_dispatch_is_case_insensitive():
    calls = []
    key_actions = {'l': lambda: calls.append('l')}

    stopped = _dispatch_key(SimpleNamespace(char='L'), FOCUSED, key_actions)

    assert calls == ['l']
    assert stopped is False


def test_dispatch_ignores_unmapped_key():
    calls = []
    key_actions = {'l': lambda: calls.append('l')}

    stopped = _dispatch_key(SimpleNamespace(char='x'), FOCUSED, key_actions)

    assert calls == []
    assert stopped is False


def test_dispatch_q_stops_without_needing_key_actions_entry():
    stopped = _dispatch_key(SimpleNamespace(char='q'), FOCUSED, {})

    assert stopped is True


def test_dispatch_ignored_when_window_not_focused():
    calls = []
    key_actions = {'l': lambda: calls.append('l')}

    stopped = _dispatch_key(SimpleNamespace(char='l'), UNFOCUSED, key_actions)

    assert calls == []
    assert stopped is False


def test_dispatch_ignores_keys_without_char():
    stopped = _dispatch_key(SimpleNamespace(char=None), FOCUSED, {})

    assert stopped is False
