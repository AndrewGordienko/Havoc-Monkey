
# Havoc Monkey

**Havoc Monkey** is a robust network testing tool designed to simulate network disruptions and test the resilience of network infrastructure, built upon the work of [Chaos Monkey](https://github.com/Netflix/chaosmonkey) by Netflix. Through randomized network interface toggling, latency injection, and network surges, Havoc Monkey ensures your systems are prepared for unexpected failures. Designed for virtual environments like vSRX routers, it provides powerful, automated stress testing in real time.

---

## Features

- **Configurable Parameters:** Effortlessly adjust the time intervals between actions, define protected interfaces and specify the YAML file path for network configuration.
- **Graceful Cleanup:** On termination, Havoc Monkey restores all modified interfaces to their original, active state.
- **Interface Protection:** A specific interface (e.g., ge-0/0/0) is protected from disruptions, ensuring critical network paths remain intact during tests.
- **Traffic Shaping:** Introduce random traffic shaping (bandwidth limitations) to specific interfaces to mimic real-world network conditions.
- **Randomized Interface Disruptions:** Disable and re-enable network interfaces (ge-) at random, simulating network instability.

---

## How It Works

Havoc Monkey randomly selects devices from your network configuration and performs one of the following actions on their interfaces:

- **Disable Interface:** Temporarily disables a selected ge- interface to simulate network failure.
- **Create Traffic Shaper:** Applies a traffic shaper (bandwidth limit) on an interface to simulate bandwidth constraints.

After performing these actions, the interface is restored, ensuring no lasting disruption. The tool repeats the process continuously until it is manually stopped.

---

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
[ACTION] Creating a traffic shaper on ge-0/0/0 of vSRX3 with a bandwidth limit of 350 Mbps
[RESULT] Traffic shaper applied on ge-0/0/0 of vSRX3
[WAIT] Waiting for 10.75 seconds before removing the traffic shaper from ge-0/0/0...
[ACTION] Removing the traffic shaper from ge-0/0/0 of vSRX3
[RESULT] Traffic shaper removed from ge-0/0/0 of vSRX3
[WAIT] Sleeping for 7.63 seconds before the next action...

```

Upon pressing `Ctrl+C`, Havoc Monkey gracefully restores all modified interfaces:

```python
[INFO] Havoc Monkey stopped by user.
[INFO] Enabling all modified interfaces...

[ACTION] Re-enabling ge-0/0/2 on vSRX1
[RESULT] ge-0/0/2 on vSRX1 enabled

[ACTION] Removing the traffic shaper from ge-0/0/0 of vSRX3
[RESULT] Traffic shaper removed from ge-0/0/0 of vSRX3

[INFO] All modified interfaces enabled.

```

---

# Toronto IX Traffic Simulation

This simulation generates traffic patterns over a 24-hour period, based on Toronto IX (TORIX) traffic statistics. The simulation is powered by a polynomial function that models real-world traffic variations seen at TORIX.

The data and graph are based on traffic statistics provided by [TORIX](https://www.torix.ca/traffic-statistics/)

___

## How It Works

The torix_simulation.py script generates traffic data according to a polynomial that represents Toronto's 24-hour traffic pattern. It uses the iperf3 library to simulate traffic between a client and a server, sending UDP traffic at rates determined by the polynomial at the current time of day.

The traffic rate is scaled, and random fluctuations are added to mimic real-world variability. The length of a simulated day can be adjusted, allowing faster or slower simulation of a 24-hour traffic cycle.

### Example Workflow:
1. Get Traffic Rate: The get_traffic_rate function calculates traffic using the polynomial equation and adds some random noise.
2. Send Traffic: The send_traffic function uses iperf3 to send UDP traffic at the calculated rate to a target server.
3. Control Simulation Speed: The simulated day length can be controlled by adjusting the SimulatedDayLengthSeconds variable.

___

## Setting Up iperf3 on Linux Devices

1. Install iperf3 on the server and client machines.

```bash
sudo apt-get install iperf3
```

2. Run iperf3 in server mode on the target device:

```bash
iperf3 -s
```

3. Run the simulation script on the client machine:


```bash
python3 torix_simulation.py
```

___

## Graphs

### TORIX Traffic Statistics

TORIX provides the following graph:

<img width="695" alt="image" src="https://github.com/user-attachments/assets/41216f28-cb9f-4b9c-8a15-76512d4463e5">

### TORIX Traffic Extracted Statistics

The graph generated by my software to replicate the TORIX data is shown below:

![image](https://github.com/user-attachments/assets/f96d65a9-7d5d-4c8a-9e65-9f6f0daf550b)

### TORIX Traffic Extrapolated Graph

The graph produced by my software, using a general polynomial with added noise, is shown below:

![image](https://github.com/user-attachments/assets/ebb356b7-80d8-4824-9c23-8b7571fa58de)


## License

Havoc Monkey and the Toronto IX traffic simulation are licensed under the MIT License.  See `LICENSE` for more details.
