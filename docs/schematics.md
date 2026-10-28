# Hardware Circuit Pinout & Wiring Map

## 1. ESP32 DevKit to Sensors & Actuators

| Component | Component Pin | ESP32 GPIO Pin | Details / Notes |
| :--- | :--- | :--- | :--- |
| **MPU6050 IMU** | VCC | 3.3V / 5V | Power Supply |
| | GND | GND | Ground |
| | SDA | GPIO 21 | I2C Data Line (400kHz Fast I2C) |
| | SCL | GPIO 22 | I2C Clock Line |
| **A4988 Driver** | STEP | GPIO 25 | Stepper Directional Pulses |
| | DIR | GPIO 26 | Stepper Motion Vector Control |
| | MS1, MS2, MS3 | 3.3V | Configured for 1/16 Microstepping |
| | RESET & SLEEP | Tied together | Pulled HIGH to enable driver |
| **State LEDs** | RED LED (+) | GPIO 12 | Active Disturbance / Error Spike State |
| | GREEN LED (+) | GPIO 13 | Target Acquired / SNN Tracking Lock |
| | BLUE LED (+) | GPIO 14 | Air-Bearing Levitating / Search State |
| **Optical Laser** | VCC (+) | GPIO 17 | Controlled Optical Pointer Payload |