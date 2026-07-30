import os

import node_archive


def _use_tmp_files(tmp_path, monkeypatch):
    monkeypatch.setattr(node_archive, "NODE_FILE", str(tmp_path / "nodes.txt"))
    monkeypatch.setattr(node_archive, "LOG_FILE", str(tmp_path / "traceroute_log.txt"))


def test_load_existing_nodes_missing_file(tmp_path, monkeypatch):
    _use_tmp_files(tmp_path, monkeypatch)
    assert node_archive.load_existing_nodes() == set()


def test_save_node_then_load_existing_nodes(tmp_path, monkeypatch):
    _use_tmp_files(tmp_path, monkeypatch)

    node_archive.save_node("!abc123", 1700000000, {"longName": "Test"}, {"batteryLevel": 90}, "2024-01-01 00:00:00")

    assert node_archive.load_existing_nodes() == {"!abc123"}


def test_log_traceroute_skips_none(tmp_path, monkeypatch):
    _use_tmp_files(tmp_path, monkeypatch)

    node_archive.log_traceroute(None)

    assert not os.path.exists(node_archive.LOG_FILE)


def test_log_traceroute_writes_line_verbatim(tmp_path, monkeypatch):
    _use_tmp_files(tmp_path, monkeypatch)

    node_archive.log_traceroute("2024-01-01 00:00:00 - Traceroute output for !abc123: !aaa --> !abc123")

    with open(node_archive.LOG_FILE) as f:
        content = f.read()
    assert content == "2024-01-01 00:00:00 - Traceroute output for !abc123: !aaa --> !abc123\n"


def test_load_traceroute_log_nodes_parses_success_and_error_lines(tmp_path, monkeypatch):
    _use_tmp_files(tmp_path, monkeypatch)

    node_archive.log_traceroute("2024-01-01 00:00:00 - Traceroute output for !abc123: !aaa --> !abc123")
    node_archive.log_traceroute("2024-01-01 00:00:01 - !def456 some stderr text")

    assert node_archive.load_traceroute_log_nodes() == {"!abc123", "!def456"}
