import socket
import math
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- UDP Socket Setup ---
UDP_LISTEN_IP = "127.0.0.1"
UDP_LISTEN_PORT = 4210
TELEMETRY_PORT = 4211

sock_listen = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_listen.bind((UDP_LISTEN_IP, UDP_LISTEN_PORT))
sock_listen.setblocking(False)

sock_telemetry = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# --- Dynamic System Variables ---
target_yaw = 0.0
yaw_angle = 0.0
yaw_velocity = 0.0
error_sum = 0.0
last_error = 0.0

# Physical Constants & Gain Tuning
Kp = 8.5
Ki = 0.01
Kd = 1.2
I_sat = 0.005  # Satellite Moment of Inertia (kg*m^2)
dt = 0.05      # 20 Hz loop update

# --- Base Cube Geometry ---
cube_vertices = np.array([
    [-0.5, -0.5, -0.5], [ 0.5, -0.5, -0.5], [ 0.5,  0.5, -0.5], [-0.5,  0.5, -0.5],
    [-0.5, -0.5,  0.5], [ 0.5, -0.5,  0.5], [ 0.5,  0.5,  0.5], [-0.5,  0.5,  0.5]
])

edges = [
    (0,1), (1,2), (2,3), (3,0),
    (4,5), (5,6), (6,7), (7,4),
    (0,4), (1,5), (2,6), (3,7)
]

# Set up 3D Scene
fig = plt.figure(figsize=(7, 7))
ax = fig.add_subplot(111, projection='3d')
ax.set_xlim([-1.2, 1.2])
ax.set_ylim([-1.2, 1.2])
ax.set_zlim([-1.2, 1.2])
ax.view_init(elev=25, azim=45)

# Initialize Line Objects for smooth updating
lines = [ax.plot([], [], [], color='blue', linewidth=2)[0] for _ in edges]
pointer_line, = ax.plot([], [], [], color='red', linewidth=3)
pointer_dot = ax.scatter([], [], [], color='red', s=50)

print("==================================================")
print(" HIL SIMULATOR (DYNAMIC 3D ENGINE ACTIVE) ")
print(" Listening for UDP Commands on 4210... ")
print(" Broadcasting Telemetry on 4211... ")
print("==================================================")

def update_physics_and_render(frame):
    global target_yaw, yaw_angle, yaw_velocity, error_sum, last_error

    # 1. Receive incoming UDP setpoint
    try:
        data, _ = sock_listen.recvfrom(1024)
        target_yaw = float(data.decode('utf-8'))
    except BlockingIOError:
        pass

    # 2. Environmental Disturbance Torque
    disturbance_torque = random.uniform(-0.0001, 0.0001)

    # 3. PID Control Law
    error = target_yaw - yaw_angle
    error_sum += error * dt
    d_error = (error - last_error) / dt
    pwm_output = (Kp * error) + (Ki * error_sum) + (Kd * d_error)
    last_error = error

    # 4. Rotational Dynamics Physics (Increased motor torque multiplier)
    motor_torque = pwm_output * 0.002
    total_torque = motor_torque + disturbance_torque
    angular_accel = total_torque / I_sat
    
    yaw_velocity += angular_accel * dt
    yaw_velocity *= 0.85  # Damping friction
    yaw_angle += (yaw_velocity * dt)

    # 5. Broadcast Telemetry to app.py
    telemetry_str = f"Target:{target_yaw:.2f},Yaw:{yaw_angle:.2f},Err:{abs(error):.2f},PWM:{pwm_output:.2f}"
    sock_telemetry.sendto(telemetry_str.encode('utf-8'), ("127.0.0.1", TELEMETRY_PORT))

    # 6. Transform and Update 3D Geometry
    rad = math.radians(yaw_angle)
    R = np.array([
        [math.cos(rad), -math.sin(rad), 0],
        [math.sin(rad),  math.cos(rad), 0],
        [0,              0,             1]
    ])
    
    rotated_vertices = np.dot(cube_vertices, R)

    # Update Cube Edges
    for idx, edge in enumerate(edges):
        pts = rotated_vertices[list(edge)]
        lines[idx].set_data(pts[:, 0], pts[:, 1])
        lines[idx].set_3d_properties(pts[:, 2])

    # Update Red Directional Laser
    nose = np.dot(np.array([0, 0.8, 0]), R)
    pointer_line.set_data([0, nose[0]], [0, nose[1]])
    pointer_line.set_3d_properties([0, nose[2]])

    ax.set_title(f"Target Yaw: {target_yaw:.1f}° | Actual Yaw: {yaw_angle:.1f}°")

ani = animation.FuncAnimation(fig, update_physics_and_render, interval=50, cache_frame_data=False)
plt.tight_layout()
plt.show()