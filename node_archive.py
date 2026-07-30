import os
from datetime import datetime

NODE_FILE = os.path.join(os.path.dirname(__file__), 'nodes.txt')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'traceroute_log.txt')


def load_existing_nodes():
    """Load existing node IDs from the node file."""
    nodes = set()
    if os.path.exists(NODE_FILE):
        with open(NODE_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    node_id, *rest = line.split(',')
                    nodes.add(node_id)
    return nodes


def load_traceroute_log_nodes():
    """Load node IDs from the traceroute log file."""
    logged_nodes = set()

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            for line in f:
                if 'Traceroute output for' in line:
                    logged_node = line.split()[6].rstrip(':')
                    logged_nodes.add(logged_node)
                elif len(line.split()) > 3 and line.split()[3].startswith('!'):
                    logged_node = line.split()[3]
                    logged_nodes.add(logged_node)

    return logged_nodes


def save_node(node_id, last_heard=None, user=None, device_metrics=None, seen_time=None):
    """Save a new node ID along with lastHeard, user, and deviceMetrics to the node file."""
    output_line = f"{node_id},{last_heard},{user},{device_metrics},{seen_time}\n"
    os.makedirs(os.path.dirname(NODE_FILE), exist_ok=True)
    with open(NODE_FILE, 'a') as f:
        f.write(output_line)


def log_traceroute(log_line):
    """Append a pre-formatted traceroute log line, if any.

    `log_line` comes from meshtastic_device.run_traceroute — None means
    nothing should be recorded.
    """
    if log_line is None:
        return
    with open(LOG_FILE, 'a') as log_file:
        log_file.write(f"{log_line}\n")
