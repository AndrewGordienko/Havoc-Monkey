import sys
# sys.path.append('/usr/local/lib/python3.12/dist-packages')

import random
import time
import yaml
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError, ConfigLoadError, LockError

# Variables for configuration
SLEEP_TIME_MIN = 5  # Minimum time between actions
SLEEP_TIME_MAX = 15  # Maximum time between actions
AVOID_INTERFACE = 'ge-0/0/0'  # Interface to avoid for any actions
CONFIG_FILE_PATH = 'devices_config.yaml'  # Path to the YAML configuration file

# Load device configuration from YAML file
def load_device_config(file_path=CONFIG_FILE_PATH):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config['credentials'], config['devices']

# SSH credentials
credentials, devices = load_device_config()

# Track modified interfaces
modified_interfaces = []

def connect_to_device(device_ip):
    try:
        dev = Device(host=device_ip, user=credentials['username'], passwd=credentials['password'])
        dev.open()
        dev.facts_refresh()  # Ensure we refresh device facts after connection
        print(f"[INFO] Connected to device {device_ip}")
        return dev
    except ConnectError as err:
        print(f"[ERROR] Failed to connect to device {device_ip}: {err}")
        return None

def disable_interface(device, interface, device_name):
    print(f"[ACTION] Disabling {interface} on {device.hostname}")
    try:
        with Config(device, mode='exclusive') as cu:
            cu.load(f'set interfaces {interface} disable', format='set')
            cu.commit()
            print(f"[RESULT] {interface} on {device.hostname} disabled")
            modified_interfaces.append((device_name, interface))  # Use device_name, not device.hostname
    except Exception as e:
        print(f"[ERROR] Failed to disable {interface} on {device.hostname}: {e}")

def enable_interface(device, interface):
    print(f"[ACTION] Enabling {interface} on {device.hostname}")
    try:
        with Config(device, mode='exclusive') as cu:
            config = cu.rpc.get_config(filter_xml=f'<configuration><interfaces><interface><name>{interface}</name><disable/></interface></interfaces></configuration>')
            if config.find('.//disable') is not None:
                cu.load(f'delete interfaces {interface} disable', format='set')
                cu.commit()
                print(f"[RESULT] {interface} on {device.hostname} enabled")
            else:
                print(f"[INFO] {interface} on {device.hostname} is already enabled. Skipping.")
    except Exception as e:
        print(f"[ERROR] Failed to enable {interface} on {device.hostname}: {e}")

def inject_latency(device, interface, latency_ms, device_name):
    print(f"[ACTION] Injecting {latency_ms}ms latency on {interface} of {device.hostname}")
    try:
        with Config(device, mode='exclusive') as cu:
            cu.load(f'set firewall family inet filter LATENCY term 1 from interface {interface}', format='set')
            cu.load(f'set firewall family inet filter LATENCY term 1 then policer LATENCY_POLICER', format='set')
            cu.load(f'set firewall policer LATENCY_POLICER if-exceeding bandwidth-limit {latency_ms}m burst-size-limit 10k', format='set')
            cu.load(f'set firewall policer LATENCY_POLICER then loss-priority low', format='set')
            cu.commit()
            print(f"[RESULT] Latency of {latency_ms}ms injected on {interface} of {device.hostname}")
            modified_interfaces.append((device_name, interface))  # Use device_name, not device.hostname
    except Exception as e:
        print(f"[ERROR] Failed to inject latency on {interface} of {device.hostname}: {e}")

def remove_latency(device, interface):
    print(f"[ACTION] Removing latency on {interface} of {device.hostname}")
    try:
        with Config(device, mode='exclusive') as cu:
            cu.load(f'delete firewall family inet filter LATENCY term 1 from interface {interface}', format='set')
            cu.load(f'delete firewall family inet filter LATENCY term 1 then policer LATENCY_POLICER', format='set')
            cu.load(f'delete firewall policer LATENCY_POLICER', format='set')
            cu.commit()
            print(f"[RESULT] Latency removed from {interface} of {device.hostname}")
    except ConfigLoadError as e:
        print(f"[ERROR] Failed to remove latency on {interface} of {device.hostname}: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error when removing latency on {interface} of {device.hostname}: {e}")

def create_network_surge(device, interface, device_name):
    print(f"[ACTION] Creating network surge on {interface} of {device.hostname}")
    try:
        with Config(device, mode='exclusive') as cu:
            cu.load(f'set firewall policer SURGE_POLICER if-exceeding bandwidth-limit 1000m burst-size-limit 500k', format='set')
            cu.load(f'set firewall policer SURGE_POLICER then discard', format='set')
            cu.load(f'set firewall family inet filter SURGE term 1 from interface {interface}', format='set')
            cu.load(f'set firewall family inet filter SURGE term 1 then policer SURGE_POLICER', format='set')
            cu.commit()
            print(f"[RESULT] Network surge created on {interface} of {device.hostname}")
            modified_interfaces.append((device_name, interface))  # Use device_name, not device.hostname
    except Exception as e:
        print(f"[ERROR] Failed to create network surge on {interface} of {device.hostname}: {e}")

def enable_modified_interfaces():
    print("\n[INFO] Enabling all modified interfaces...")

    for device_name, interface in modified_interfaces:
        device_ip = devices.get(device_name, {}).get("ip")
        if not device_ip:
            print(f"[ERROR] Device {device_name} not found in devices configuration. Skipping...")
            continue

        # Connect to the device
        dev = connect_to_device(device_ip)
        if dev is None:
            continue

        try:
            print(f"[ACTION] Re-enabling {interface} on {device_name}")
            enable_interface(dev, interface)
        finally:
            dev.close()

    print("[INFO] All modified interfaces enabled.")

def havoc_monkey():
    while True:
        # Randomly select a device and its IP
        device_name = random.choice(list(devices.keys()))
        device_info = devices[device_name]
        device_ip = device_info["ip"]

        # Exclude the interface specified in AVOID_INTERFACE
        available_interfaces = [interface for interface in device_info["interfaces"] if interface != AVOID_INTERFACE]
        
        # If no interfaces are left after excluding AVOID_INTERFACE, skip the device
        if not available_interfaces:
            print(f"[INFO] No available interfaces on {device_name} to manipulate.")
            continue

        # Connect to the device
        dev = connect_to_device(device_ip)
        if dev is None:
            continue

        try:
            # Randomly select a `ge-` interface from the device, excluding the avoided one
            interface = random.choice(available_interfaces)

            # Randomly choose an action: disable, inject latency, or create network surge
            action = random.choice(["disable", "inject_latency", "create_surge"])

            if action == "disable":
                disable_interface(dev, interface, device_name)
            elif action == "inject_latency":
                latency = random.randint(50, 500)
                inject_latency(dev, interface, latency, device_name)
            elif action == "create_surge":
                create_network_surge(dev, interface, device_name)

            # Wait for a random time (based on SLEEP_TIME_MIN and SLEEP_TIME_MAX)
            wait_time = random.uniform(SLEEP_TIME_MIN, SLEEP_TIME_MAX)
            print(f"[WAIT] Waiting for {wait_time:.2f} seconds before the next action...")
            time.sleep(wait_time)

            # Re-enable the interface if it was disabled or latency removed
            if action == "disable":
                enable_interface(dev, interface)
            elif action == "inject_latency":
                remove_latency(dev, interface)

        finally:
            # Close the connection
            dev.close()

        # Wait before performing another action
        sleep_time = random.uniform(SLEEP_TIME_MIN, SLEEP_TIME_MAX)
        print(f"[WAIT] Sleeping for {sleep_time:.2f} seconds before the next action...")
        time.sleep(sleep_time)

if __name__ == "__main__":
    try:
        havoc_monkey()
    except KeyboardInterrupt:
        print("\n[INFO] Havoc Monkey stopped by user.")
        enable_modified_interfaces()
