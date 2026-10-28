# 1-DOF CubeSat Attitude Determination and Control System (ADCS)

An end-to-end hardware and software architecture for a single-degree-of-freedom satellite reaction wheel attitude control system, integrating ESP32 embedded firmware, neuromorphic event-based perception, and a real-time Hardware-in-the-Loop (HIL) telemetry dashboard.

---

## System Overview

This project bridges embedded systems, real-time control loops, and neuromorphic computing to simulate space-grade attitude adjustment.
[Event Camera / SNN Tracker] ---> (UDP Stream) ---> [ESP32 Firmware / PID Control] ---> [Reaction Wheel Hardware]
^                                                                                   |
|--------------------------- (HIL Telemetry Stream @ 50 Hz) <-----------------------|
---

## Repository Structure

* **`/firmware`**: PlatformIO C++ source code running on the ESP32, handling sensor inputs, motor drivers, and closed-loop attitude stabilization.
* **`/perception`**: Python-based neuromorphic processing pipeline utilizing spiking neural networks (`snntorch`) for asynchronous spatial trajectory tracking.
* **`/telemetry_dashboard`**: Python/Flask HIL simulation environment and UDP bridge managing real-time data visualization at 50 Hz.
* **`/docs`**: System schematics, electrical wiring topologies (including common-ground star splices for noise mitigation), and hardware documentation.

---

## Electrical & Power Topology
* **Input Voltage**: 12V DC primary bus.
* **Regulation**: Step-down 5V buck converter for logic-level components.
* **Noise Mitigation**: 3-way common ground star splice layout to isolate switching noise from sensitive analog sensor and ESP32 ADC rails.

---

## Software Pipeline & Telemetry
The telemetry dashboard streams live state estimates over UDP, allowing real-time tuning of control parameters and visualization of phase portraits during simulated orbital maneuvers
---

## Integrated System Context
This repository houses the core control, hardware, and simulation infrastructure. It pairs directly with our neuromorphic perception pipeline to form a complete, modular aerospace testbench:
* **Control & Hardware Subsystem:** [`1-DOF-CubeSat-ADCS`](https://github.com/akshararathore569-web/1-DOF-CubeSat-ADCS)
* **Perception & Vision Subsystem:** [`neuromorphic-event-tracker`](https://github.com/akshararathore569-web/neuromorphic-event-tracker)