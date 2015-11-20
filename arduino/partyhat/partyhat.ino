int ANALOG_PIN = 9;

void setup() {
  // The baud rate below MUST match the baud of the Bluetooth board.
  Serial.begin(115200);
}

void loop() {
  if (Serial.available() > 0) {
    analogWrite(9, Serial.read());
  }
}
