
# Havoc Monkey

**Havoc Monkey** is a robust network testing tool designed to simulate network disruptions and test the resilience of network infrastructure, built upon the work of [Chaos Monkey](https://github.com/Netflix/chaosmonkey) by Netflix. Through randomized network interface toggling, latency injection, and network surges, Havoc Monkey ensures your systems are prepared for unexpected failures. Designed for virtual environments like vSRX routers, it provides powerful, automated stress testing in real time. Additional software like `torix_simulation.py` offers a powerful tool to generate background traffic, enabling you to thoroughly test your system's performance.

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

```bash
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

```bash
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

This simulation generates traffic patterns over 24 hours, based on Toronto IX (TORIX) traffic statistics. The simulation is powered by a polynomial function that models real-world traffic variations seen at TORIX.

The data and graph are based on traffic statistics provided by [TORIX](https://www.torix.ca/traffic-statistics/)

___

## Features

- **Realistic Traffic Modeling:** Simulates 24-hour traffic patterns using a polynomial equation to replicate TORIX traffic data, with added noise for variability.
- **Customizable Simulation Speed:** Adjust the length of the simulated day to speed up or slow down the traffic generation cycle.
- **Automated Traffic Scaling:** Scales traffic rates automatically based on the polynomial output, ensuring realistic traffic loads.
- **Seamless iperf3 Integration:** Uses 'iperf3' to send UDP traffic, providing real-time feedback and easy network performance monitoring.

## How It Works

The `torix_simulation.py` script simulates traffic patterns based on Toronto's 24-hour traffic data. It performs the following actions:

- **Generate Traffic Data:** Uses a polynomial equation to calculate traffic rates for different times of the day.
- **Send UDP Traffic:** Utilizes the iperf3 library to send traffic between a client and server, with rates determined by the current time in the simulation.
- **Add Random Fluctuations:** Introduces noise to the traffic data to mimic real-world variability.
- **Adjust Simulation Speed:** Allows customization of the simulation day length, enabling faster or slower simulations of a full 24-hour traffic cycle.

The simulation repeats continuously until manually stopped, with real-time traffic data feedback.
___

### Installation:

Havoc Monkey requires iperf3 and the numpy library to send traffic between devices.

1. Clone the repository (if not done previously):

   ```bash
   git clone https://github.com/AndrewGordienko/havoc-monkey.git
   cd havoc-monkey
   ```

2. Install the required Python dependencies:

   ```bash
   sudo apt-get install iperf3
   python3 -m pip install numpy
   ```

3. Run iperf3 in server mode on the target device:

   ```bash
   iperf3 -s
   ```

4. Run the simulation script on the client machine:


   ```bash
   python3 torix_simulation.py
   ```
___

## Configuration

Toronto IX Traffic Simulation is highly configurable through Python variables.

### Python variables

You can modify the behavior of the Toronto IX Traffic Simulation by adjusting the following Python variables in the script:

- **`Polynomial`:** Represents the polynomial equation modeling TORIX traffic over 24 hours.
- **`ScalingFactor`:** Controls how much traffic is sent relative to the polynomial's output. A higher factor increases traffic rates.
- **`TargetIP`:** Specifies the target server to which UDP traffic is sent.
- **`SimulatedDayLengthSeconds`:** Defines the number of real-world seconds that represent a full 24-hour simulated traffic cycle. For example, setting this to 10 means a simulated day lasts for 10 real-world seconds.
- **`SendInterval`:** Specifies how often traffic is sent (in seconds). For example, setting this to 1 means traffic is sent every second.
___

## Example

Here’s a quick example of Toronto IX Traffic Simulation in action:

### Client side

```bash
[ACTION] Sending traffic at 160.67 Mbps to 100.67.31.243
[RESULT] Sent 160.53 Mbps to 100.67.31.243
[ACTION] Sending traffic at 3701655725303.95 Mbps to 100.67.31.243
[RESULT] Sent 22432.60 Mbps to 100.67.31.243
[ACTION] Sending traffic at 6797574205732984.00 Mbps to 100.67.31.243
[RESULT] Sent 22958.53 Mbps to 100.67.31.243
[ACTION] Sending traffic at 448469928608254336.00 Mbps to 100.67.31.243
[RESULT] Sent 21743.10 Mbps to 100.67.31.243
[ACTION] Sending traffic at 9172089712020254720.00 Mbps to 100.67.31.243
[RESULT] Sent 23276.65 Mbps to 100.67.31.243
[ACTION] Sending traffic at 89393774597265473536.00 Mbps to 100.67.31.243
[RESULT] Sent 22285.40 Mbps to 100.67.31.243
[ACTION] Sending traffic at 516931515021396410368.00 Mbps to 100.67.31.243
[RESULT] Sent 22914.91 Mbps to 100.67.31.243
[ACTION] Sending traffic at 2550948839878784188416.00 Mbps to 100.67.31.243
[RESULT] Sent 22065.74 Mbps to 100.67.31.243
```
### Server side

```bash
-----------------------------------------------------------
Server listening on 5201 (test #1)
-----------------------------------------------------------
Accepted connection from 100.67.31.243, port 58836
[  5] local 100.67.31.243 port 5201 connected to 100.67.31.243 port 62451
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-1.00   sec  19.1 MBytes   161 Mbits/sec  0.003 ms  0/2450 (0%)  
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-1.00   sec  19.1 MBytes   161 Mbits/sec  0.003 ms  0/2450 (0%)  receiver
-----------------------------------------------------------
Server listening on 5201 (test #2)
-----------------------------------------------------------
Accepted connection from 100.67.31.243, port 58837
[  5] local 100.67.31.243 port 5201 connected to 100.67.31.243 port 51900
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-1.00   sec  1.05 GBytes  8.99 Gbits/sec  0.002 ms  204794/341946 (60%)  
[  5]   1.00-1.00   sec   392 KBytes  10.3 Gbits/sec  0.004 ms  144/195 (74%)  
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-1.00   sec  1.05 GBytes  8.99 Gbits/sec  0.004 ms  204938/342141 (60%)  receiver
-----------------------------------------------------------
Server listening on 5201 (test #3)
-----------------------------------------------------------
Accepted connection from 100.67.31.243, port 58838
[  5] local 100.67.31.243 port 5201 connected to 100.67.31.243 port 53350
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-1.00   sec  1020 MBytes  8.55 Gbits/sec  0.001 ms  219779/350311 (63%)  
[  5]   1.00-1.00   sec   368 KBytes  9.60 Gbits/sec  0.003 ms  0/53 (0%)  
- - - - - - - - - - - - - - - - - - - - - - - - -
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-1.00   sec  1020 MBytes  8.56 Gbits/sec  0.003 ms  219779/350364 (63%)  receiver
```
___

## Graphs

### TORIX Traffic Statistics

TORIX provides the following graph:

<img width="600" alt="image" src="https://github.com/user-attachments/assets/41216f28-cb9f-4b9c-8a15-76512d4463e5">

### TORIX Traffic Extracted Statistics

The graph generated by my software to replicate the TORIX data is shown below:

<img width="600" alt="image" src="https://github.com/user-attachments/assets/f96d65a9-7d5d-4c8a-9e65-9f6f0daf550b">

### TORIX Traffic Extrapolated Graph

The graph produced by my software, using a general polynomial with added noise, is shown below:

<img width="600" alt="image" src="https://github.com/user-attachments/assets/ebb356b7-80d8-4824-9c23-8b7571fa58de">

___

## License

Havoc Monkey and the Toronto IX traffic simulation are licensed under the MIT License.  See `LICENSE` for more details.
