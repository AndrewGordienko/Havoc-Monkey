import sys
# sys.path.append('/usr/local/lib/python3.12/dist-packages') # This line might be important in solving an install bug you get

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

def create_traffic_shaper(device, interface, bandwidth_limit, device_name):
    print(f"[ACTION] Creating traffic shaper on {interface} of {device.hostname}")
    try:
        with Config(device, mode='exclusive') as cu:
            cu.load(f'set firewall family inet filter SHAPER term 1 from interface {interface}', format='set')
            cu.load(f'set firewall family inet filter SHAPER term 1 then policer SHAPER_POLICER', format='set')
            cu.load(f'set firewall policer SHAPER_POLICER if-exceeding bandwidth-limit {bandwidth_limit}m burst-size-limit 10k', format='set')
            cu.load(f'set firewall policer SHAPER_POLICER then loss-priority low', format='set')
            cu.commit()
            print(f"[RESULT] Traffic shaper created with {bandwidth_limit}Mbps limit on {interface} of {device.hostname}")
            modified_interfaces.append((device_name, interface))  # Use device_name, not device.hostname
    except Exception as e:
        print(f"[ERROR] Failed to create traffic shaper on {interface} of {device.hostname}: {e}")

def remove_traffic_shaper(device, interface):
    print(f"[ACTION] Removing traffic shaper on {interface} of {device.hostname}")
    try:
        with Config(device, mode='exclusive') as cu:
            cu.load(f'delete firewall family inet filter SHAPER term 1 from interface {interface}', format='set')
            cu.load(f'delete firewall family inet filter SHAPER term 1 then policer SHAPER_POLICER', format='set')
            cu.load(f'delete firewall policer SHAPER_POLICER', format='set')
            cu.commit()
            print(f"[RESULT] Traffic shaper removed from {interface} of {device.hostname}")
    except ConfigLoadError as e:
        print(f"[ERROR] Failed to remove traffic shaper on {interface} of {device.hostname}: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error when removing traffic shaper on {interface} of {device.hostname}: {e}")

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

            # Randomly choose an action: disable or create traffic shaper
            action = random.choice(["disable", "create_traffic_shaper"])

            if action == "disable":
                disable_interface(dev, interface, device_name)
            elif action == "create_traffic_shaper":
                bandwidth_limit = random.randint(50, 500)
                create_traffic_shaper(dev, interface, bandwidth_limit, device_name)

            # Wait for a random time (based on SLEEP_TIME_MIN and SLEEP_TIME_MAX)
            wait_time = random.uniform(SLEEP_TIME_MIN, SLEEP_TIME_MAX)
            print(f"[WAIT] Waiting for {wait_time:.2f} seconds before the next action...")
            time.sleep(wait_time)

            # Re-enable the interface if it was disabled or traffic shaper removed
            if action == "disable":
                enable_interface(dev, interface)
            elif action == "create_traffic_shaper":
                remove_traffic_shaper(dev, interface)

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
