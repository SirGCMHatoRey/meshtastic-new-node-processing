import meshtastic_device

SAMPLE_OUTPUT = (
    "Some preamble\n"
    "Nodes in mesh: "
    '{"!abc123": {"lastHeard": 1700000000, "user": {"longName": "Test"}, '
    '"deviceMetrics": {"batteryLevel": 90}}}\n'
    "\n"
    "Trailer text\n"
)


def test_parse_nodes_from_output_parses_json_block():
    parsed = meshtastic_device._parse_nodes_from_output(SAMPLE_OUTPUT)

    assert parsed == {
        "nodes": [
            {
                "id": "!abc123",
                "lastHeard": 1700000000,
                "user": {"longName": "Test"},
                "deviceMetrics": {"batteryLevel": 90},
            }
        ]
    }


def test_parse_nodes_from_output_missing_marker_returns_none():
    assert meshtastic_device._parse_nodes_from_output("no marker here") is None


def test_parse_nodes_from_output_invalid_json_returns_none():
    broken = "Nodes in mesh: {not valid json}\n\n"
    assert meshtastic_device._parse_nodes_from_output(broken) is None
