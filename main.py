import random
import time
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError

# Define the vSRX devices and their interfaces
devices = {
    "vSRX1": {
        "ip": "192.168.255.2",
        "interfaces": ["ge-0/0/0", "ge-0/0/1", "ge-0/0/2"]
    },
    "vSRX2": {
        "ip": "192.168.255.3",
        "interfaces": ["ge-0/0/0", "ge-0/0/1", "ge-0/0/2"]
    },
    "vSRX3": {
        "ip": "192.168.255.4",
        "interfaces": ["ge-0/0/0", "ge-0/0/1", "ge-0/0/2", "ge-0/0/3"]
    },
    "vSRX4": {
        "ip": "192.168.255.5",
        "interfaces": ["ge-0/0/0", "ge-0/0/1", "ge-0/0/2"]
    }
}

# SSH credentials
username = "your_username"
password = "your_password"

def connect_to_device(device_ip):
    try:
        dev = Device(host=device_ip, user=username, passwd=password)
        dev.open()
        return dev
    except ConnectError as err:
        print(f"Failed to connect to device {device_ip}: {err}")
        return None

def disable_interface(device, interface):
    print(f"Disabling {interface} on {device.hostname}")
    with Config(device, mode='exclusive') as cu:
        cu.load(f'set interfaces {interface} disable', format='set')
        cu.commit()

def enable_interface(device, interface):
    print(f"Enabling {interface} on {device.hostname}")
    with Config(device, mode='exclusive') as cu:
        cu.load(f'delete interfaces {interface} disable', format='set')
        cu.commit()

def chaos_monkey():
    while True:
        # Randomly pick a device
        device_name = random.choice(list(devices.keys()))
        device_info = devices[device_name]
        device_ip = device_info["ip"]

        # Connect to the device
        dev = connect_to_device(device_ip)
        if dev is None:
            continue

        try:
            # Randomly pick an interface to disable/enable
            interface = random.choice(device_info["interfaces"])

            # Randomly decide whether to disable or enable the interface
            if random.choice([True, False]):
                disable_interface(dev, interface)
            else:
                enable_interface(dev, interface)

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
