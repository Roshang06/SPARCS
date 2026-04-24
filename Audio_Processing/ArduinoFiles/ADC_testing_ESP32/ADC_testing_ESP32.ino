// SPARCS tracker prototype code for reading from an electret microphone circuit.
const int read_pin = 34;

int value;

void setup() {
  Serial.begin(115200);
  delay(1000);
}

void loop() {
  value = analogRead(read_pin);

  Serial.print(0);
  Serial.print(",");
  Serial.print(2000);

  Serial.print(",");

  Serial.println(value);

  delay(5);
}