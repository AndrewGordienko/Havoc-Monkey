
# Havoc Monkey

**Havoc Monkey** is a robust network testing tool designed to simulate network disruptions and test the resilience of network infrastructure, built upon the work of [Chaos Monkey](https://github.com/Netflix/chaosmonkey) by Netflix. Through randomized network interface toggling, latency injection, and network surges, Havoc Monkey ensures your systems are prepared for unexpected failures. Designed for virtual environments like vSRX routers, it provides powerful, automated stress testing in real time.

---

## Features

- **Configurable Parameters:** Effortlessly adjust the time intervals between actions, define protected interfaces, and specify the YAML file path for network configuration.
- **Graceful Cleanup:** On termination, Havoc Monkey restores all modified interfaces to their original, active state.
- **Interface Protection:** A specific interface (e.g., ge-0/0/1) is protected from disruptions, ensuring critical network paths remain intact during tests.
- **Latency Injection:** Introduce random latency (between 50ms to 500ms) to specific interfaces to mimic real-world network delays.
- **Network Surges:** Generate network traffic surges on selected interfaces, putting additional load on your network.
- **Randomized Interface Disruptions:** Disable and re-enable network interfaces (ge-) at random, simulating network instability.

___

## How It Works

Havoc Monkey randomly selects devices from your network configuration and performs one of the following actions on their interfaces:

- **Create Network Surge:** Generates a surge of traffic on an interface to test how it handles high load.
- **Disable Interface:** Temporarily disables a selected ge- interface to simulate network failure.
- **Inject Latency:** Adds artificial latency to simulate network delays on the interface.

After performing these actions, the interface is restored, ensuring no lasting disruption. The tool repeats the process continuously until it is manually stopped.

___

## Installation

Havoc Monkey requires Python 3.x and the Junos PyEZ library to communicate with network devices.

### From Source

1. Clone the repository:

   ```bash
   git clone https://github.com/AndrewGordienko/havoc-monkey.git
   cd havoc-monkey
   ```

2. Install the required Python dependencies:

   ```bash
   python3 -m pip install -r requirements.txt
   ```
3. Troubleshooting:

If you encounter issues related to missing libraries (e.g., Paramiko or Junos PyEZ), ensure that you are using the correct version of Python and that your system path is properly configured. You may need to install dependencies using pip or apt-get. Check out this helpful [Stack Overflow](https://stackoverflow.com/questions/28991319/ubuntu-python-no-module-named-paramiko) thread for more details on how to resolve common installation issues, especially when mixing Python environments.

4. Create your configuration file:

   ```yaml
   # devices_config.yaml
   credentials:
     username: "your_username"
     password: "your_password"

   devices:
     vSRX1:
       ip: "192.168.255.2"
       interfaces:
         - "ge-0/0/0"
         - "ge-0/0/1"
         - "ge-0/0/2"
     vSRX2:
       ip: "192.168.255.3"
       interfaces:
         - "ge-0/0/0"
         - "ge-0/0/1"
         - "ge-0/0/2"
     vSRX3:
       ip: "192.168.255.4"
       interfaces:
         - "ge-0/0/0"
         - "ge-0/0/1"
         - "ge-0/0/2"
         - "ge-0/0/3"
     vSRX4:
       ip: "192.168.255.5"
       interfaces:
         - "ge-0/0/0"
         - "ge-0/0/1"
         - "ge-0/0/2"
   ```

5. Run Havoc Monkey:

   ```bash
   python3 havoc_main.py
   ```

---

## Configuration

Havoc Monkey is highly configurable through a YAML file (`devices_config.yaml`) and Python variables.

### YAML Configuration

The YAML file defines the devices and their interfaces to be managed by Havoc Monkey. Each device must include:

- **IP Address**: The IP of the device.
- **Interfaces**: A list of interfaces (`ge-0/0/x`) that Havoc Monkey will act upon.

### Python Variables

You can modify the behavior of Havoc Monkey by changing the following variables in the script:

- **`SLEEP_TIME_MIN` and `SLEEP_TIME_MAX`**: Controls the range for how long Havoc Monkey waits between actions.
- **`AVOID_INTERFACE`**: Specifies an interface to protect (e.g., `ge-0/0/1`), which Havoc Monkey will not disable or disrupt.

---

## Example

Here’s a quick example of Havoc Monkey in action:

```python
[INFO] Connected to device 192.168.255.1
[ACTION] Disabling ge-0/0/2 on vSRX1
[RESULT] ge-0/0/2 on vSRX1 disabled
[WAIT] Waiting for 12.43 seconds before re-enabling ge-0/0/2...
[ACTION] Enabling ge-0/0/2 on vSRX1
[RESULT] ge-0/0/2 on vSRX1 enabled
[WAIT] Sleeping for 9.21 seconds before the next action...

[INFO] Connected to device 192.168.255.3
[ACTION] Injecting 350ms latency on ge-0/0/0 of vSRX3
[RESULT] Latency of 350ms injected on ge-0/0/0 of vSRX3
[WAIT] Waiting for 10.75 seconds before removing latency from ge-0/0/0...
[ACTION] Removing latency on ge-0/0/0 of vSRX3
[RESULT] Latency removed from ge-0/0/0 of vSRX3
[WAIT] Sleeping for 7.63 seconds before the next action...

[INFO] Connected to device 192.168.255.4
[ACTION] Creating network surge on ge-0/0/1 of vSRX4
[RESULT] Network surge created on ge-0/0/1 of vSRX4
[WAIT] Waiting for 15.32 seconds before removing surge from ge-0/0/1...
[ACTION] Removing network surge on ge-0/0/1 of vSRX4
[RESULT] Network surge removed from ge-0/0/1 of vSRX4
[WAIT] Sleeping for 8.47 seconds before the next action...

[INFO] Connected to device 192.168.255.2
[ACTION] Disabling ge-0/0/3 on vSRX2
[RESULT] ge-0/0/3 on vSRX2 disabled
[WAIT] Waiting for 11.59 seconds before re-enabling ge-0/0/3...
[ACTION] Enabling ge-0/0/3 on vSRX2
[RESULT] ge-0/0/3 on vSRX2 enabled
[WAIT] Sleeping for 5.92 seconds before the next action...

```

Upon pressing `Ctrl+C`, Havoc Monkey gracefully restores all modified interfaces:

```python
[INFO] Havoc Monkey stopped by user.
[INFO] Enabling all modified interfaces...
[ACTION] Re-enabling ge-0/0/2 on vSRX1
[INFO] All modified interfaces enabled.
```

---


## License

Havoc Monkey is licensed under the MIT License. See `LICENSE` for more details.
