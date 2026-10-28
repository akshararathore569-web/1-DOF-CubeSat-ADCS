# Optical Event-Guided Reaction Sphere

An Air-Bearing Satellite Attitude Determination & Control System (ADCS) testbed driven by an ESP32 microcontroller, real-time closed-loop PID control, and spiking neural network (SNN) event-based target tracking.

## System Architecture

* **Hardware Layer:** Air-bearing levitation sphere, NEMA 17 reaction wheel assembly, MPU6050 IMU sensor.
* **Firmware Layer:** Dual-core ESP32 C++ application (FreeRTOS).
  * **Core 1:** 500 Hz high-rate PID loop execution & MPU6050 sensor polling.
  * **Core 0:** Non-blocking Wi-Fi UDP command processing & state-aware LED indicators.
* **Software-in-the-Loop (HIL) Simulation Suite:**
  * `hil_simulator.py`: Dynamic 3D Matplotlib visualizer & rotational dynamics simulator.
  * `app.py`: Real-time telemetry dashboard (UDP/Serial streaming).
  * `snn_tracker.py`: Neuromorphic Leaky Integrate-and-Fire (LIF) spike stream generator.

## Software Setup & Requirements

### Prerequisites
Install all required dependencies:
```bash
pip install -r requirements.txt