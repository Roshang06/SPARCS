#include "BluetoothSerial.h"

// Check if Bluetooth is properly enabled
#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

BluetoothSerial SerialBT;

const int micPin = 34;
const int sampleRate = 8000; 
const unsigned long sampleInterval = 1000000 / sampleRate;

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

  // Ensure we only sample at the specific rate
  if (now - lastSample >= sampleInterval) {
    lastSample = now;

    uint16_t sample = analogRead(micPin);

    // Only send if a device is actually connected to save power/cycles
    if (SerialBT.connected()) {
      SerialBT.write((uint8_t*)&sample, 2);
    }
  }
}