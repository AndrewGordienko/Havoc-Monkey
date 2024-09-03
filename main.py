import os
import random
import time

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

def run_command_on_device(device_ip, command):
    # Use os.system to execute SSH command (simple approach)
    ssh_command = f'sshpass -p {password} ssh -o StrictHostKeyChecking=no {username}@{device_ip} "{command}"'
    os.system(ssh_command)

def disable_interface(device_ip, interface):
    print(f"Disabling {interface} on {device_ip}")
    command = f"cli -c 'set interfaces {interface} disable; commit'"
    run_command_on_device(device_ip, command)

def enable_interface(device_ip, interface):
    print(f"Enabling {interface} on {device_ip}")
    command = f"cli -c 'delete interfaces {interface} disable; commit'"
    run_command_on_device(device_ip, command)

def chaos_monkey():
    while True:
        # Randomly pick a device
        device_name = random.choice(list(devices.keys()))
        device = devices[device_name]
        device_ip = device["ip"]

        # Randomly pick an interface to disable/enable
        interface = random.choice(device["interfaces"])

        # Randomly decide whether to disable or enable the interface
        if random.choice([True, False]):
            disable_interface(device_ip, interface)
        else:
            enable_interface(device_ip, interface)

        # Wait for a random time before the next action
        time.sleep(random.uniform(5, 15))

if __name__ == "__main__":
    try:
        chaos_monkey()
    except KeyboardInterrupt:
        print("Chaos Monkey stopped")
