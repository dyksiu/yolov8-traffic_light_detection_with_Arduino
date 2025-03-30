void setup() {
  Serial.begin(9600);
  pinMode(8, OUTPUT);  // Red
  pinMode(9, OUTPUT);  // Yellow
  pinMode(10, OUTPUT); // Green
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n'); 

    // Ustawienie stanu niskiego na wszystkich diodach
    digitalWrite(8, LOW);
    digitalWrite(9, LOW);
    digitalWrite(10, LOW);

    // Wykrycie czy przeslano dany znak
    if (command.indexOf('R') >= 0) {
      digitalWrite(8, HIGH);  // Red
    }
    if (command.indexOf('Y') >= 0) {
      digitalWrite(9, HIGH);  // Yellow
    }
    if (command.indexOf('G') >= 0) {
      digitalWrite(10, HIGH); // Green
    }

    // Jeśli "N" (nic), nie włączaj niczego (już wszystko OFF)
  }
}
