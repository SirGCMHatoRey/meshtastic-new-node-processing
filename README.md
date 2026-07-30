# K3ANO NewNodes

A command-line tool for [Meshtastic](https://meshtastic.org/) mesh network operators. It watches your mesh for nodes it hasn't seen before, runs a traceroute against each new node, logs the result, and sends it a welcome message — automatically, on a repeating interval.

## Features

- Polls a Meshtastic device (USB serial, IP, or Bluetooth) for the current node list
- Detects new nodes (skipping ones already known, already traceroute-logged, or not heard from recently)
- Runs a traceroute against each new node and logs it to `traceroute_log.txt`
- Sends a configurable welcome message to new nodes
- Records every node seen in `nodes.txt`
- While running, press `L` to open the traceroute log, `N` to open the node list, or `Q` to quit

## Requirements

- Python 3.6+
- A Meshtastic device reachable over USB serial, IP, or Bluetooth
- **Windows**: `pywin32`, `pygetwindow`
- **Linux**: `python3-xlib`, `python3-tk`, `python3-dev`, `xdotool`

## Installation

The latest release of this fork is [v0.87](https://github.com/SirGCMHatoRey/meshtastic-new-node-processing/releases/tag/v0.87) — see its notes for what changed since v0.86. There's no prebuilt wheel for it; install from source:

```bash
git clone --branch v0.87 https://github.com/SirGCMHatoRey/meshtastic-new-node-processing.git
cd meshtastic-new-node-processing
pip install -e .
```

Or drop `--branch v0.87` to install the latest unreleased changes on `main`.

### Prebuilt wheel (upstream, v0.86 and earlier)

The original repo published prebuilt wheels through v0.86:

```bash
pip install https://github.com/StevoKeano/meshtastic-new-node-processing/releases/download/v0.86/K3ANO_NewNodes-0.86-py3-none-any.whl
```

See its [Releases page](https://github.com/StevoKeano/meshtastic-new-node-processing/releases) for all versions and asset filenames.

## Usage

Run it with any of these commands (all equivalent, installed as console scripts):

```bash
NewNodes
```

You'll be asked to confirm or change the welcome message, then whether your radio is connected via USB (`C`), IP (`I`), or Bluetooth (`B`). After that it polls on a loop, checking for new nodes each cycle.

### Command-line options

| Flag | Description |
|---|---|
| `--p <type> <value>` | Skip the connection prompt. `--p c COM9` (Windows serial), `--p c /dev/ttyACM0` (Linux serial), or `--p i 192.168.1.87` (IP) |
| `--m` | Use the welcome message from `settings.json` without prompting |
| `--v` | Enable verbose debug output |

Example:

```bash
NewNodes --p i 192.168.1.87 --m
```

## Configuration

The welcome message is stored in `settings.json`:

```json
{
  "welcome_message": "Welcome to the mesh! Join us on the AustinMesh discord chat: https://discord.gg/cpDFj345"
}
```

Update it interactively when prompted at startup, or edit the file directly.

## Files this tool creates

- `nodes.txt` — every node ID seen, with last-heard time, user info, and device metrics
- `traceroute_log.txt` — traceroute results for each new node

## Project layout

- `newNode.py` — entry point, connection setup, and the main poll loop
- `meshtastic_device.py` — Meshtastic CLI adapter (port/IP checks, node info, traceroute, sending messages)
- `node_archive.py` — reads and writes `nodes.txt` / `traceroute_log.txt`
- `node_classifier.py` — decides what to do with each node seen (new, already known, stale, etc.)
- `app_settings.py` — reads and writes `settings.json`
- `window_title.py` — sets the terminal window title (used to gate the `L`/`N`/`Q` keyboard shortcuts)
- `bt_info.py` — Bluetooth (BLE) device scanning and selection

## Running tests

```bash
pip install pytest
pytest
```

## License

MIT
