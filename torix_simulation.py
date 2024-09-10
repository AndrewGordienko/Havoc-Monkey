import numpy as np
import iperf3
import random
import time
from datetime import datetime

# Polynomial for Toronto traffic over a 24-hour day
Polynomial = np.poly1d([2.58297002e-10, -3.21800750e-08, 1.70814458e-06, -5.03712815e-05,
                        9.00908764e-04, -9.99421172e-03, 6.73894053e-02, -2.60642628e-01,
                        5.43893686e-01, -6.61274018e-01, 1.51700690e+00])

ScalingFactor = 100  # Adjust traffic rate
TargetIP = "100.67.31.243" # Adjust IP to fit your network
SimulatedDayLengthSeconds = 10  # Real-world seconds to simulate 24 hours of traffic
SendInterval = 1  # Send traffic every 1 second

# # Optional: Visualization of the polynomial (you can uncomment this if needed)
# import matplotlib.pyplot as plt
# plt.figure(figsize=(10, 6))
# plt.plot(hours, traffic_rates, label="Traffic Polynomial", color='blue')
# plt.title('Toronto Traffic Polynomial Over a Day', fontsize=14)
# plt.xlabel('Time of Day (hours)', fontsize=12)
# plt.ylabel('Traffic Rate', fontsize=12)
# plt.grid(True)
# plt.legend()
# plt.show()

def get_traffic_rate(current_second):
    current_hour = (current_second / 3600) * 24  # Convert seconds to hours in a day
    base_rate = Polynomial(current_hour)
    fluctuation = random.uniform(-0.1, 0.1)
    rate = max(0, base_rate + fluctuation * base_rate)  # Ensure rate is non-negative
    return rate * ScalingFactor

def send_traffic(rate_mbps, duration):
    if rate_mbps <= 0:
        print(f"[INFO] Skipping transmission: rate is non-positive ({rate_mbps:.2f} Mbps)")
        return

    client = iperf3.Client()
    client.server_hostname = TargetIP
    client.protocol = 'udp'
    client.bandwidth = int(rate_mbps * 1e6)  # Convert Mbps to bps
    client.duration = duration
    client.socket_bufsize = 100000
    client.blksize = 8192

    print(f"[ACTION] Sending traffic at {rate_mbps:.2f} Mbps to {TargetIP}")
    result = client.run()

    if result.error:
        print(f"[ERROR] iperf3 test failed: {result.error}")
    else:
        print(f"[RESULT] Sent {result.Mbps:.2f} Mbps to {TargetIP}")

start_time = datetime.now()

while True:
    try:
        elapsed_time = datetime.now() - start_time
        simulated_seconds_per_day = 86400 / SimulatedDayLengthSeconds  # Scale real time to simulate 24 hours
        current_simulated_second = elapsed_time.total_seconds() * simulated_seconds_per_day

        traffic_rate_mbps = get_traffic_rate(current_simulated_second)
        send_traffic(traffic_rate_mbps, duration=1)

        time.sleep(SendInterval)

    except KeyboardInterrupt:
        print("[INFO] Traffic generation stopped by user.")
        break
