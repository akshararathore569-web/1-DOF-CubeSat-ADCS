import sys
import socket
import time
import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from collections import deque

# --- CONFIGURATION ---
# Set USE_HARDWARE_SERIAL = True when physical ESP32 is plugged into USB
USE_HARDWARE_SERIAL = False  
SERIAL_PORT = 'COM3'         # Update to your ESP32 COM port when hardware arrives
BAUD_RATE = 115200

# Buffer sizes for real-time plotting (last 100 data points)
MAX_LEN = 100
time_vec = deque(maxlen=MAX_LEN)
target_vec = deque(maxlen=MAX_LEN)
yaw_vec = deque(maxlen=MAX_LEN)
err_vec = deque(maxlen=MAX_LEN)

# Initialize Input Data Source (Hardware USB Serial or Software UDP)
ser = None
sock = None

if USE_HARDWARE_SERIAL:
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        print(f"[MODE: HARDWARE] Listening on USB Serial Port {SERIAL_PORT}")
    except Exception as e:
        print(f"Serial Connection Error: {e}")
else:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 4211))
    sock.setblocking(False)
    print("[MODE: SIMULATION] Listening for HIL Simulator UDP Telemetry on 127.0.0.1:4211")

# Set up Live Plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
fig.suptitle("Project 3: Hardware-in-the-Loop (HIL) Satellite ADCS Telemetry", fontsize=14, fontweight='bold')

line_target, = ax1.plot([], [], 'r--', label='Target Yaw (deg)')
line_yaw, = ax1.plot([], [], 'b-', linewidth=2, label='Estimated Yaw (deg)')
line_err, = ax2.plot([], [], 'g-', label='Control Error (deg)')

ax1.set_ylabel("Angle (Degrees)")
ax1.grid(True)
ax1.legend(loc='upper right')

ax2.set_xlabel("Time Step")
ax2.set_ylabel("Error (Degrees)")
ax2.grid(True)
ax2.legend(loc='upper right')

step = 0

def update(frame):
    global step
    line = ""

    # Read from Real USB Serial or Mock UDP Stream
    if USE_HARDWARE_SERIAL and ser and ser.in_waiting:
        try:
            line = ser.readline().decode('utf-8').strip()
        except Exception:
            pass
    elif not USE_HARDWARE_SERIAL and sock:
        try:
            data, _ = sock.recvfrom(1024)
            line = data.decode('utf-8').strip()
        except BlockingIOError:
            pass

    # Parse String: "Target:10.0,Yaw:8.5,Err:1.5,PWM:25.0"
    if "Target:" in line and "Yaw:" in line:
        try:
            parts = line.split(',')
            target = float(parts[0].split(':')[1])
            yaw = float(parts[1].split(':')[1])
            err = float(parts[2].split(':')[1])

            step += 1
            time_vec.append(step)
            target_vec.append(target)
            yaw_vec.append(yaw)
            err_vec.append(err)

            line_target.set_data(time_vec, target_vec)
            line_yaw.set_data(time_vec, yaw_vec)
            line_err.set_data(time_vec, err_vec)

            ax1.relim()
            ax1.autoscale_view()
            ax2.relim()
            ax2.autoscale_view()
        except Exception:
            pass

    return line_target, line_yaw, line_err

ani = animation.FuncAnimation(fig, update, interval=20, blit=False)
plt.tight_layout()
plt.show()