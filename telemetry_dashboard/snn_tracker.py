import socket
import time
import math
import random

# --- UDP Socket Setup ---
UDP_TARGET_IP = "127.0.0.1"
UDP_TARGET_PORT = 4210

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# --- SNN Simulation Parameters ---
threshold = 1.0
decay = 0.85
membrane_potential = 0.0

print("==================================================")
print(" SNN EVENT-BASED TARGET TRACKER SIMULATOR ")
print(" Processing Neuromorphic Spike Streams... ")
print(f" Streaming Setpoints to UDP Port {UDP_TARGET_PORT}... ")
print("==================================================")

t = 0.0

try:
    while True:
        # 1. Simulate incoming event-camera spike stream (Moving target in field of view)
        simulated_visual_event = math.sin(t) * 30.0 + random.uniform(-1.5, 1.5)
        
        # 2. Integrate visual spikes into LIF Neuron Membrane Potential
        membrane_potential = (membrane_potential * decay) + (simulated_visual_event * 0.2)

        # 3. Fire target setpoint when membrane potential crosses threshold
        if abs(membrane_potential) > threshold:
            target_yaw = round(membrane_potential * 1.5, 2)
            
            # Broadcast setpoint over UDP
            sock.sendto(str(target_yaw).encode('utf-8'), (UDP_TARGET_IP, UDP_TARGET_PORT))
            print(f"[SNN SPIKE FIRED] Target Yaw -> {target_yaw:.2f}° | Membrane V: {membrane_potential:.2f}")
            
            # Reset membrane potential post-spike
            membrane_potential = 0.0

        t += 0.1
        time.sleep(0.1)  # 10 Hz SNN firing rate

except KeyboardInterrupt:
    print("\nSNN Tracker stopped cleanly.")