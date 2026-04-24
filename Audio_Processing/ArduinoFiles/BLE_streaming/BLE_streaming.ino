#include "BluetoothSerial.h"

// Check if Bluetooth is properly enabled
#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

BluetoothSerial SerialBT;

const int micPin = 34;
const int sampleRate = 8000; 
const unsigned long sampleInterval = 1000000 / sampleRate;

const int CHUNK_SIZE = 64; // Send 64 samples at once
uint16_t buffer[CHUNK_SIZE];
int bufferIndex = 0;

void setup() {
  Serial.begin(115200); // For local debugging
  
  // The name that will appear on your laptop
  SerialBT.begin("ESP32_Audio_Link"); 
  
  analogReadResolution(12);
  Serial.println("Bluetooth Started. Pair your device now.");
}

void loop() {
  static unsigned long lastSample = 0;
  unsigned long now = micros();

  if (now - lastSample >= sampleInterval) {
    lastSample = now;
    
    buffer[bufferIndex++] = analogRead(micPin);

    // Once the buffer is full, send the whole packet
    if (bufferIndex >= CHUNK_SIZE) {
      if (SerialBT.connected()) {
        SerialBT.write((uint8_t*)buffer, CHUNK_SIZE * 2);
      }
      bufferIndex = 0;
    }
  }
}