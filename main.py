import random
import time
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError

# Define the vSRX devices, their interfaces, and credentials
devices = {
    "vSRX1": {
        "ip": "192.168.255.2",
        "interfaces": ["ge-0/0/0", "ge-0/0/1", "ge-0/0/2"],
        "username": "user1",
        "password": "password1"
    },
    "vSRX2": {
        "ip": "192.168.255.3",
        "interfaces": ["ge-0/0/0", "ge-0/0/1", "ge-0/0/2"],
        "username": "user2",
        "password": "password2"
    },
    "vSRX3": {
        "ip": "192.168.255.4",
        "interfaces": ["ge-0/0/0", "ge-0/0/1", "ge-0/0/2", "ge-0/0/3"],
        "username": "user3",
        "password": "password3"
    },
    "vSRX4": {
        "ip": "192.168.255.5",
        "interfaces": ["ge-0/0/0", "ge-0/0/1", "ge-0/0/2"],
        "username": "user4",
        "password": "password4"
    }
}

# To track changes made during chaos
changes = {}

# Function to connect to a device
def connect_to_device(device_ip, username, password):
    try:
        dev = Device(host=device_ip, user=username, passwd=password)
        dev.open()
        print(f"Successfully connected to {device_ip}")
        return dev
    except ConnectError as err:
        print(f"Failed to connect to {device_ip}: {err}")
        return None

# Disable an interface
def disable_interface(device, interface):
    print(f"Disabling {interface} on {device.hostname}...")
    with Config(device, mode='exclusive') as cu:
        cu.load(f'set interfaces {interface} disable', format='set')
        cu.commit()
        print(f"{interface} on {device.hostname} disabled")
        changes[(device.hostname, interface)] = "disabled"

# Enable an interface
def enable_interface(device, interface):
    print(f"Enabling {interface} on {device.hostname}...")
    with Config(device, mode='exclusive') as cu:
        cu.load(f'delete interfaces {interface} disable', format='set')
        cu.commit()
        print(f"{interface} on {device.hostname} enabled")
        changes[(device.hostname, interface)] = "enabled"

# Inject latency
def inject_latency(device, interface, latency_ms):
    print(f"Injecting {latency_ms}ms latency on {interface} of {device.hostname}...")
    with Config(device, mode='exclusive') as cu:
        cu.load(f'set firewall family inet filter LATENCY term 1 from interface {interface}', format='set')
        cu.load(f'set firewall family inet filter LATENCY term 1 then policer LATENCY_POLICER', format='set')
        cu.load(f'set firewall policer LATENCY_POLICER if-exceeding bandwidth-limit {latency_ms}m burst-size-limit 10k', format='set')
        cu.load(f'set firewall policer LATENCY_POLICER then delay {latency_ms}', format='set')
        cu.commit()
        print(f"Latency injected on {interface} of {device.hostname}")
        changes[(device.hostname, interface)] = "latency_injected"

# Remove latency
def remove_latency(device, interface):
    print(f"Removing latency on {interface} of {device.hostname}...")
    with Config(device, mode='exclusive') as cu:
        cu.load(f'delete firewall family inet filter LATENCY term 1 from interface {interface}', format='set')
        cu.load(f'delete firewall family inet filter LATENCY term 1 then policer LATENCY_POLICER', format='set')
        cu.load(f'delete firewall policer LATENCY_POLICER', format='set')
        cu.commit()
        print(f"Latency removed on {interface} of {device.hostname}")
        changes[(device.hostname, interface)] = "latency_removed"

# Simulate a network surge by increasing bandwidth
def create_network_surge(device, interface):
    print(f"Creating network surge on {interface} of {device.hostname}...")
    with Config(device, mode='exclusive') as cu:
        cu.load(f'set firewall policer SURGE_POLICER if-exceeding bandwidth-limit 1000m burst-size-limit 500k', format='set')
        cu.load(f'set firewall policer SURGE_POLICER then discard', format='set')
        cu.load(f'set firewall family inet filter SURGE term 1 from interface {interface}', format='set')
        cu.load(f'set firewall family inet filter SURGE term 1 then policer SURGE_POLICER', format='set')
        cu.commit()
        print(f"Network surge created on {interface} of {device.hostname}")
        changes[(device.hostname, interface)] = "surge"

# Simulate traffic congestion by reducing bandwidth
def simulate_traffic_congestion(device, interface):
    print(f"Simulating traffic congestion on {interface} of {device.hostname}...")
    with Config(device, mode='exclusive') as cu:
        cu.load(f'set firewall policer CONGESTION_POLICER if-exceeding bandwidth-limit 10m burst-size-limit 10k', format='set')
        cu.load(f'set firewall policer CONGESTION_POLICER then discard', format='set')
        cu.load(f'set firewall family inet filter CONGESTION term 1 from interface {interface}', format='set')
        cu.load(f'set firewall family inet filter CONGESTION term 1 then policer CONGESTION_POLICER', format='set')
        cu.commit()
        print(f"Traffic congestion simulated on {interface} of {device.hostname}")
        changes[(device.hostname, interface)] = "congestion"

# Restore network to the original state
def cleanup():
    print("Restoring network to the original state...")
    for device_name, device_info in devices.items():
        dev = connect_to_device(device_info["ip"], device_info["username"], device_info["password"])
        if dev is None:
            continue

        try:
            for interface in device_info["interfaces"]:
                if (device_name, interface) in changes:
                    action = changes[(device_name, interface)]
                    if action == "disabled":
                        enable_interface(dev, interface)
                    elif action == "latency_injected":
                        remove_latency(dev, interface)
                    elif action == "surge" or action == "congestion":
                        with Config(dev, mode='exclusive') as cu:
                            cu.load(f'delete firewall family inet filter SURGE term 1 from interface {interface}', format='set')
                            cu.load(f'delete firewall family inet filter CONGESTION term 1 from interface {interface}', format='set')
                            cu.load(f'delete firewall policer SURGE_POLICER', format='set')
                            cu.load(f'delete firewall policer CONGESTION_POLICER', format='set')
                            cu.commit()
                            print(f"Surge or congestion removed from {interface} of {device_name}")
        finally:
            dev.close()

# Chaos Monkey main function
def chaos_monkey():
    while True:
        # Select a random device and interface
        device_name = random.choice(list(devices.keys()))
        device_info = devices[device_name]
        device_ip = device_info["ip"]
        username = device_info["username"]
        password = device_info["password"]
        interface = random.choice(device_info["interfaces"])

        # Connect to the device
        dev = connect_to_device(device_ip, username, password)
        if dev is None:
            continue

        try:
            # Select a random chaos action
            action = random.choice(["disable", "enable", "inject_latency", "remove_latency", "surge", "traffic_congestion"])

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
            elif action == "traffic_congestion":
                simulate_traffic_congestion(dev, interface)

        finally:
            dev.close()

        # Random wait before the next chaos action
        sleep_time = random.uniform(5, 20)
        print(f"Waiting for {sleep_time:.2f} seconds before the next chaos event...\n")
        time.sleep(sleep_time)

if __name__ == "__main__":
    try:
        print("Starting Chaos Monkey...")
        chaos_monkey()
    except KeyboardInterrupt:
        print("Chaos Monkey stopped")
        cleanup()
