const int micPin = 34;
const int sampleRate = 8000; // 8 kHz speech-quality audio

void setup() {
  Serial.begin(921600);
  analogReadResolution(12);
}

void loop() {

  static unsigned long lastSample = 0;
  unsigned long now = micros();

  if (now - lastSample >= 1000000 / sampleRate) {

    lastSample = now;

    uint16_t sample = analogRead(micPin);

    Serial.write((uint8_t*)&sample, 2);  // send raw binary
  }
}