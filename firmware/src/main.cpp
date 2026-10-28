#include <Arduino.h>
#include <Wire.h>
#include <WiFi.h>
#include <WiFiUdp.h>
#include <Stepper.h>

// --- Pin Allocations ---
#define MPU6050_ADDR 0x68
#define LED_RED_PIN   12  // Error / Active Disturb
#define LED_GREEN_PIN 13  // Target Acquired / SNN Lock
#define LED_BLUE_PIN  14  // Levitating / Search State

// --- Stepper Motor Configuration (28BYJ-48 + ULN2003) ---
const int stepsPerRevolution = 2048; 
// Clean non-tangling pin mapping: 1N1->D21, 1N2->D19, 1N3->D18, 1N4->D5
Stepper myStepper(stepsPerRevolution, 21, 19, 18, 5);

// --- Shared Thread-Safe Variables ---
portMUX_TYPE timerMux = {}; // Updated for modern ESP32 toolchains
volatile float g_yawAngle = 0.0;
volatile float g_targetYaw = 0.0;
volatile float g_controlOutput = 0.0;
volatile uint8_t g_systemState = 0; // 0: Search, 1: Locked, 2: Disturbed

// --- Control Parameters ---
float Kp = 14.2, Ki = 0.02, Kd = 1.8;
float errorSum = 0.0, lastError = 0.0;

// --- Wi-Fi Configuration ---
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
WiFiUDP udp;
unsigned int localUdpPort = 4210;

// --- Task Handles ---
TaskHandle_t ControlTaskHandle;

// ==========================================
// CORE 1: High-Speed Control & Sensor Fusion
// ==========================================
void ControlTask(void * parameter) {
  TickType_t xLastWakeTime = xTaskGetTickCount();
  const TickType_t xFrequency = pdMS_TO_TICKS(2); // 500 Hz Control Loop

  for (;;) {
    // 1. Read MPU6050 Z-Gyro Data
    Wire.beginTransmission(MPU6050_ADDR);
    Wire.write(0x47); // GYRO_ZOUT_H
    Wire.endTransmission(false);
    Wire.requestFrom(MPU6050_ADDR, 2, true);
    
    int16_t rawGyroZ = Wire.read() << 8 | Wire.read();
    float gyroZ = rawGyroZ / 131.0; // deg/s

    // 2. State Estimation
    portENTER_CRITICAL(&timerMux);
    g_yawAngle += gyroZ * 0.002; // dt = 2ms
    float localTarget = g_targetYaw;
    float currentYaw = g_yawAngle;
    portEXIT_CRITICAL(&timerMux);

    // 3. PID Math
    float err = localTarget - currentYaw;
    errorSum += err * 0.002;
    float dErr = (err - lastError) / 0.002;
    float output = (Kp * err) + (Ki * errorSum) + (Kd * dErr);
    lastError = err;

    portENTER_CRITICAL(&timerMux);
    g_controlOutput = output;
    portEXIT_CRITICAL(&timerMux);

    // 4. Actuate ULN2003 Stepper Motor Driver
    if (abs(output) > 0.5) {
      // Scale output response to small steps based on PID sign
      int stepsToMove = (output > 0) ? 2 : -2;
      myStepper.step(stepsToMove);
    }

    vTaskDelayUntil(&xLastWakeTime, xFrequency);
  }
}

// ==========================================
// CORE 0: Setup & Telemetry / Wi-Fi Stack
// ==========================================
void setup() {
  Serial.begin(115200);
  Wire.begin();
  Wire.setClock(400000); // 400kHz Fast I2C

  pinMode(LED_RED_PIN, OUTPUT);
  pinMode(LED_GREEN_PIN, OUTPUT);
  pinMode(LED_BLUE_PIN, OUTPUT);

  // Initialize Stepper Motor Speed (RPM)
  myStepper.setSpeed(12);

  // Initialize MPU6050 Power State
  Wire.beginTransmission(MPU6050_ADDR);
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission(true);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
  }
  udp.begin(localUdpPort);

  // Pin Control Task to Core 1
  xTaskCreatePinnedToCore(
    ControlTask,          /* Task function */
    "ControlTask",        /* Name */
    10000,                /* Stack size */
    NULL,                 /* Parameter */
    1,                    /* Priority */
    &ControlTaskHandle,   /* Handle */
    1                     /* Core 1 */
  );
}

void loop() {
  // 1. Process Incoming UDP Setpoints from Neuromorphic Event Tracker
  char packetBuffer[255];
  int packetSize = udp.parsePacket();
  if (packetSize) {
    int len = udp.read(packetBuffer, 255);
    if (len > 0) packetBuffer[len] = 0;
    
    float receivedTarget = atof(packetBuffer);
    portENTER_CRITICAL(&timerMux);
    g_targetYaw = receivedTarget;
    portEXIT_CRITICAL(&timerMux);
  }

  // 2. Dynamic LED State Indicator Logic
  portENTER_CRITICAL(&timerMux);
  float err = abs(g_targetYaw - g_yawAngle);
  portEXIT_CRITICAL(&timerMux);

  if (err < 2.0) {
    // Target Acquired / Locked (Green)
    digitalWrite(LED_GREEN_PIN, HIGH);
    digitalWrite(LED_BLUE_PIN, LOW);
    digitalWrite(LED_RED_PIN, LOW);
  } else if (err < 10.0) {
    // Active Correcting / Floating Search (Blue)
    digitalWrite(LED_GREEN_PIN, LOW);
    digitalWrite(LED_BLUE_PIN, HIGH);
    digitalWrite(LED_RED_PIN, LOW);
  } else {
    // Large Disturbance / Error Spike (Red)
    digitalWrite(LED_GREEN_PIN, LOW);
    digitalWrite(LED_BLUE_PIN, LOW);
    digitalWrite(LED_RED_PIN, HIGH);
  }

  // 3. Stream Telemetry to Serial for Project Dashboard
  Serial.print("Target:"); Serial.print(g_targetYaw);
  Serial.print(",Yaw:"); Serial.print(g_yawAngle);
  Serial.print(",Err:"); Serial.print(err);
  Serial.print(",PWM:"); Serial.println(g_controlOutput);

  delay(20); // 50 Hz Telemetry Stream
}