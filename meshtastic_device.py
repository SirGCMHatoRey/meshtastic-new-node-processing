import subprocess
import serial.tools.list_ports
import sys
import shlex
import json
from datetime import datetime

timeout_seconds = 10


def check_meshtastic_port(port):
    """Check if a Meshtastic device is connected at the specified port."""
    command = [sys.executable, '-m', 'meshtastic', '--port', port, '--info']
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=timeout_seconds)
        output_lines = result.stdout.strip().split('\n')
        if output_lines and output_lines[-1].startswith("Complete URL"):
            print(f"Meshtastic device found on {port}")
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error running Meshtastic command on {port}: {e}")
    except subprocess.TimeoutExpired:
        print(f"Timeout on {port}")
    except Exception as e:
        print(f"Unexpected error on {port}: {e}")
    return False


def check_meshtastic_ip(ip_address):
    """Check if a Meshtastic device is connected at the specified IP address."""
    command = [sys.executable, '-m', 'meshtastic', '--host', ip_address, '--info']
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=timeout_seconds)
        output_lines = result.stdout.strip().split('\n')
        if output_lines and output_lines[-1].startswith("Complete URL"):
            print(f"Meshtastic device found at {ip_address}")
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error connecting to Meshtastic device at {ip_address}: {e}")
    except subprocess.TimeoutExpired:
        print(f"Timeout connecting to {ip_address}")
    except Exception as e:
        print(f"Unexpected error connecting to {ip_address}: {e}")
    return False


def find_meshtastic_port():
    """Scan for Meshtastic device on COM ports or prompt for IP address."""
    ports = sorted(serial.tools.list_ports.comports(), key=lambda x: x.device, reverse=True)

    print("Scanning for Meshtastic device...")
    for port in ports:
        print(f"\nChecking port: {port.device}")
        if check_meshtastic_port(port.device):
            return port.device

    print("No Meshtastic device found on COM ports.")

    ip_address = input("Enter IP address of the Meshtastic device (or press Enter to exit): ").strip()

    if ip_address:
        if check_meshtastic_ip(ip_address):
            return f"--host {ip_address}"

    return None


def _parse_nodes_from_output(output):
    """Extract the parsed node list from Meshtastic CLI '--info' stdout."""
    start_index = output.find("Nodes in mesh:")
    if start_index == -1:
        return None

    json_data = output[start_index:].split("Nodes in mesh:")[1].strip()
    json_data = json_data.split("\n\n")[0]

    try:
        nodes_info = json.loads(json_data)
    except json.JSONDecodeError as json_error:
        print(f"Error decoding JSON from stdout: {json_error}")
        return None

    parsed_nodes = []
    for node_id, node_data in nodes_info.items():
        parsed_nodes.append({
            "id": node_id,
            "lastHeard": node_data.get("lastHeard", None),
            "user": node_data.get("user", {}),
            "deviceMetrics": node_data.get("deviceMetrics", {})
        })

    return {"nodes": parsed_nodes}


def get_nodes_info(connection_string):
    """Get the list of nodes and their info using Meshtastic CLI."""
    command = [sys.executable, '-m', 'meshtastic'] + connection_string.split() + ['--info']

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=45)
        parsed = _parse_nodes_from_output(result.stdout)
        if parsed is None:
            print("No nodes found in the output.")
        return parsed

    except subprocess.CalledProcessError as e:
        print(f"===>> Error running info command: {e}")
        print(f"===>> Command output (stdout): {e.stdout}")
        print(f"===>> Command output (stderr): {e.stderr}")
        if e.stdout:
            return _parse_nodes_from_output(e.stdout)

    except Exception as e:
        print(f"Unexpected error: {e}")

    return None


def sendMsg(node_id, message, connection_string):
    """Send a message to a specific node using Meshtastic CLI."""
    conn_parts = shlex.split(connection_string)
    command = [sys.executable, '-m', 'meshtastic'] + conn_parts + ['--sendtext', message, '--dest', node_id]

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error sending message to {node_id}: {e}")
        print(f"Command output: {e.stderr}")


def run_traceroute(node_id, connection_string):
    """Run traceroute on a node via the Meshtastic CLI.

    Returns (success, log_line). log_line is the fully-formatted line for
    node_archive.log_traceroute to append verbatim, or None when nothing
    should be logged.
    """
    try:
        if connection_string.startswith('--host'):
            parts = connection_string.split()
            protocol = parts[0]
            ip = parts[1]
            command = [sys.executable, '-m', 'meshtastic', protocol, ip, '--traceroute', node_id]
        else:
            command = [sys.executable, '-m', 'meshtastic', '--traceroute', node_id]

        print(f'Sending traceroute request to {node_id} (this could take a while)')

        result = subprocess.run(command, check=True, capture_output=True, text=True)

        traceroute_line = None
        for line in result.stdout.splitlines():
            if ' --> ' in line:
                traceroute_line = line.strip()
                break

        if traceroute_line:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"{timestamp} - Traceroute output for {node_id}: {traceroute_line}"
            print(log_entry)
            return True, log_entry

        print(f"No valid traceroute output for {node_id}.")
        return False, f"No valid traceroute output for {node_id}."

    except subprocess.CalledProcessError as e:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_message = f"{timestamp} - {node_id} {e.stderr.strip()}"
        print(f"Error running traceroute for {node_id}: {error_message}")
        return False, error_message

    except FileNotFoundError:
        print(f"The specified Python executable was not found: {sys.executable}")
        return False, None

    except Exception as e:
        print(f"An unexpected error occurred while running traceroute for {node_id}: {str(e)}")
        return False, None
