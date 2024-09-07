import sys
sys.path.append('/usr/local/lib/python3.12/dist-packages')

import random
import time
import yaml
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError, ConfigLoadError

# Load device configuration from YAML file
def load_device_config(file_path='devices_config.yaml'):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config['credentials'], config['devices']

# SSH credentials
credentials, devices = load_device_config()

# Track changes to revert them later
changes = []

def connect_to_device(device_ip):
    try:
        dev = Device(host=device_ip, user=credentials['username'], passwd=credentials['password'])
        dev.open()
        dev.facts_refresh()  # Ensure we refresh device facts after connection
        print(f"Successfully connected to device {device_ip}")
        return dev
    except ConnectError as err:
        print(f"Failed to connect to device {device_ip}: {err}")
        return None

def disable_interface(device, interface):
    print(f"Disabling {interface} on {device.hostname}")
    try:
        with Config(device, mode='exclusive') as cu:
            cu.load(f'set interfaces {interface} disable', format='set')
            cu.commit()
            print(f"Interface {interface} on {device.hostname} disabled")
            changes.append((device.hostname, interface, "disable"))
    except Exception as e:
        print(f"Failed to disable {interface} on {device.hostname}: {e}")

def enable_interface(device, interface):
    print(f"Enabling {interface} on {device.hostname}")
    try:
        with Config(device, mode='exclusive') as cu:
            config = cu.rpc.get_config(filter_xml=f'<configuration><interfaces><interface><name>{interface}</name><disable/></interface></interfaces></configuration>')
            if config.find('.//disable') is not None:
                cu.load(f'delete interfaces {interface} disable', format='set')
                cu.commit()
                print(f"Interface {interface} on {device.hostname} enabled")
                changes.append((device.hostname, interface, "enable"))
            else:
                print(f"Interface {interface} on {device.hostname} is not disabled. Skipping.")
    except Exception as e:
        print(f"Failed to enable {interface} on {device.hostname}: {e}")
        
def disable_all_interfaces(device, device_info):
    print(f"Disabling all interfaces on {device.hostname}")
    with Config(device, mode='exclusive') as cu:
        for interface in device_info["interfaces"]:
            cu.load(f'set interfaces {interface} disable', format='set')
            changes.append((device.hostname, interface, "disable"))
        cu.commit()
        print(f"All listed interfaces on {device.hostname} disabled")

def enable_all_interfaces(device, device_info):
    print(f"Enabling all interfaces on {device.hostname}")
    with Config(device, mode='exclusive') as cu:
        for interface in device_info["interfaces"]:
            cu.load(f'delete interfaces {interface} disable', format='set')
            changes.append((device.hostname, interface, "enable"))
        cu.commit()
        print(f"All listed interfaces on {device.hostname} enabled")

def inject_latency(device, interface, latency_ms):
    print(f"Injecting {latency_ms}ms latency on {interface} of {device.hostname}")
    try:
        with Config(device, mode='exclusive') as cu:
            cu.load(f'set firewall family inet filter LATENCY term 1 from interface {interface}', format='set')
            cu.load(f'set firewall family inet filter LATENCY term 1 then policer LATENCY_POLICER', format='set')
            cu.load(f'set firewall policer LATENCY_POLICER if-exceeding bandwidth-limit {latency_ms}m burst-size-limit 10k', format='set')
            cu.load(f'set firewall policer LATENCY_POLICER then loss-priority low', format='set')
            cu.commit()
            print(f"Latency injected on {interface} of {device.hostname}")
            changes.append((device.hostname, interface, "latency"))
    except Exception as e:
        print(f"Failed to inject latency on {interface} of {device.hostname}: {e}")

def remove_latency(device, interface):
    print(f"Removing latency on {interface} of {device.hostname}")
    try:
        with Config(device, mode='exclusive') as cu:
            cu.load(f'delete firewall family inet filter LATENCY term 1 from interface {interface}', format='set')
            cu.load(f'delete firewall family inet filter LATENCY term 1 then policer LATENCY_POLICER', format='set')
            cu.load(f'delete firewall policer LATENCY_POLICER', format='set')
            cu.commit()
            print(f"Latency removed on {interface} of {device.hostname}")
            changes.append((device.hostname, interface, "latency_removed"))
    except ConfigLoadError as e:
        print(f"Failed to remove latency on {interface} of {device.hostname}: {e}")
    except Exception as e:
        print(f"Unexpected error when removing latency on {interface} of {device.hostname}: {e}")
        
def create_network_surge(device, interface):
    print(f"Creating network surge on {interface} of {device.hostname}")
    try:
        with Config(device, mode='exclusive') as cu:
            cu.load(f'set firewall policer SURGE_POLICER if-exceeding bandwidth-limit 1000m burst-size-limit 500k', format='set')
            cu.load(f'set firewall policer SURGE_POLICER then discard', format='set')
            cu.load(f'set firewall family inet filter SURGE term 1 from interface {interface}', format='set')
            cu.load(f'set firewall family inet filter SURGE term 1 then policer SURGE_POLICER', format='set')
            cu.commit()
            print(f"Network surge created on {interface} of {device.hostname}")
            changes.append((device.hostname, interface, "surge"))
    except Exception as e:
        print(f"Failed to create network surge on {interface} of {device.hostname}: {e}")

def cleanup():
    print("Reverting changes to restore the network to its original state...")
    for device_name, interface, action in reversed(changes):
        device_ip = devices.get(device_name, {}).get("ip")
        if not device_ip:
            print(f"Device {device_name} IP not found in config, skipping...")
            continue
        dev = connect_to_device(device_ip)
        if dev is None:
            continue
        try:
            if action == "disable":
                enable_interface(dev, interface)
            elif action == "enable":
                disable_interface(dev, interface)
            elif action == "latency":
                remove_latency(dev, interface)
            elif action == "latency_removed":
                inject_latency(dev, interface, random.randint(50, 500))
            elif action == "surge":
                with Config(dev, mode='exclusive') as cu:
                    cu.load(f'delete firewall family inet filter SURGE term 1 from interface {interface}', format='set')
                    cu.load(f'delete firewall policer SURGE_POLICER', format='set')
                    cu.commit()
                print(f"Network surge removed from {interface} of {device_name}")
        finally:
            dev.close()
    print("Network restoration complete.")

def chaos_monkey():
    while True:
        device_name = random.choice(list(devices.keys()))
        device_info = devices[device_name]
        device_ip = device_info["ip"]

        # Connect to the device
        dev = connect_to_device(device_ip)
        if dev is None:
            continue

        try:
            # Randomly choose whether to target the entire device or a specific interface
            target_type = random.choice(["device", "interface"])

            if target_type == "device":
                # Randomly choose an action for the entire device
                action = random.choice(["disable_all", "enable_all"])
                if action == "disable_all":
                    disable_all_interfaces(dev, device_info)  # Pass device_info
                elif action == "enable_all":
                    enable_all_interfaces(dev, device_info)  # Pass device_info

            elif target_type == "interface":
                # Randomly pick an interface
                interface = random.choice(device_info["interfaces"])

                # Randomly choose an action: disable/enable interface, inject/remove latency, or create a surge
                action = random.choice(["disable", "enable", "inject_latency", "remove_latency", "surge"])
                
                if action == "disable":
                    disable_interface(dev, interface)
                elif action == "enable":
                    enable_interface(dev, interface)
                elif action == "inject_latency":
                    latency = random.randint(50, 500)  # Latency between 50ms and 500ms
                    inject_latency(dev, interface, latency)
                elif action == "remove_latency":
                    remove_latency(dev, interface)
                elif action == "surge":
                    create_network_surge(dev, interface)

        finally:
            dev.close()

        # Wait for a random time before the next action
        sleep_time = random.uniform(5, 15)
        print(f"Sleeping for {sleep_time} seconds before the next action...")
        time.sleep(sleep_time)

if __name__ == "__main__":
    try:
        chaos_monkey()
    except KeyboardInterrupt:
        print("Chaos Monkey stopped")
        cleanup()
