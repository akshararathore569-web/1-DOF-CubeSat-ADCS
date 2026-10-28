import socket
import time

# ESP32 IP Address & UDP Port
ESP32_IP = "127.0.0.1"  # Replace with actual ESP32 IP once connected to Wi-Fi
ESP32_PORT = 4210

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_target_angle(target_angle_deg):
    """
    Pipes the target angle (in degrees) calculated by the Neuromorphic Event Tracker
    directly over Wi-Fi UDP to the ESP32 Core 0 task.
    """
    message = f"{target_angle_deg:.2f}".encode('utf-8')
    sock.sendto(message, (ESP32_IP, ESP32_PORT))
    print(f"Piped setpoint -> {target_angle_deg:.2f}° to ESP32 at {ESP32_IP}:{ESP32_PORT}")

if __name__ == "__main__":
    print("Testing UDP Bridge... Streaming test setpoint trajectory.")
    test_angles = [0.0, 15.0, 30.0, 15.0, 0.0, -15.0, -30.0, 0.0]
    for angle in test_angles:
        send_target_angle(angle)
        time.sleep(2.0)