import sys
import subprocess

from bleak import BleakScanner

# Matches meshtastic.ble_interface.SERVICE_UUID
MESHTASTIC_SERVICE_UUID = "6ba1b218-15a8-461f-9fa8-5dcae273eafd"

timeout_seconds = 30


async def scan_bluetooth_devices():
    """Scan for nearby Meshtastic BLE devices."""
    print("Scanning for Meshtastic Bluetooth devices (10 seconds)...")
    discovered = await BleakScanner.discover(
        timeout=10, return_adv=True, service_uuids=[MESHTASTIC_SERVICE_UUID]
    )

    # bleak sometimes returns devices we didn't ask for, so filter to true
    # Meshtastic devices only.
    devices = [
        device
        for device, adv in discovered.values()
        if MESHTASTIC_SERVICE_UUID in adv.service_uuids
    ]
    return devices


def display_devices(devices):
    """Print the discovered devices with an index for selection."""
    if not devices:
        print("No Meshtastic Bluetooth devices found.")
        return

    print("Found the following Meshtastic Bluetooth devices:")
    for index, device in enumerate(devices):
        print(f"  [{index}] {device.name or 'Unknown'} ({device.address})")


def get_user_selection(devices):
    """Prompt the user to pick one of the discovered devices."""
    while True:
        choice = input(f"Select a device [0-{len(devices) - 1}]: ").strip()
        try:
            index = int(choice)
            if 0 <= index < len(devices):
                return devices[index]
        except ValueError:
            pass
        print("Invalid selection, try again.")


def run_meshtastic_info(address):
    """Verify the Meshtastic CLI can reach the device over BLE."""
    command = [sys.executable, '-m', 'meshtastic', '--ble', address, '--info']
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=timeout_seconds)
        output_lines = result.stdout.strip().split('\n')
        if output_lines and output_lines[-1].startswith("Complete URL"):
            print(f"Meshtastic device found at {address}")
            return True
    except subprocess.CalledProcessError as e:
        print(f"Error connecting to Meshtastic device at {address}: {e}")
    except subprocess.TimeoutExpired:
        print(f"Timeout connecting to {address}")
    except Exception as e:
        print(f"Unexpected error connecting to {address}: {e}")
    return False
