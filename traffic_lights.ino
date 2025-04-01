#include <LiquidCrystal.h> 

// LCD UZYTE PINY: RS, E, D4, D5, D6, D7 + A i K + KONTRAST
LiquidCrystal lcd(2, 3, 4, 5, 6, 7);

// DIODY LED
const int greenLed = 8;
const int redLed = 10;
const int yellowLed = 9;

// PORT SZEREGOWY 
String inputString = "";
bool stringComplete = false;

void setup() {
  lcd.begin(16, 2);
  Serial.begin(9600);

  // PRZYPISANIE LED DO WYJSC
  pinMode(greenLed, OUTPUT);
  pinMode(redLed, OUTPUT);
  pinMode(yellowLed, OUTPUT);

  lcd.setCursor(0, 0);
  lcd.print("Oczekiwanie...");
}

void loop() {
  if (stringComplete) {
    lcd.clear();

    int separator = inputString.indexOf(':');
    if (separator > 0) {
      String label = inputString.substring(0, separator);
      String confidence = inputString.substring(separator + 1);

      // WYSWIETLANIE NA LCD
      lcd.setCursor(0, 0);
      lcd.print("Klasa: " + label);
      lcd.setCursor(0, 1);
      lcd.print("Conf: " + confidence + "%");

      // RESET DIOD
      digitalWrite(greenLed, LOW);
      digitalWrite(redLed, LOW);
      digitalWrite(yellowLed, LOW);

      // LOGIKA:
      // -> obsluga diod w zaleznosci od wykrytego label'a
      // -> przypisany char do danego label'a wysylany przez serial port
      if (label == "G") {
        digitalWrite(greenLed, HIGH);
      } else if (label == "R") {
        digitalWrite(redLed, HIGH);
      } else if (label == "Y") {
        digitalWrite(yellowLed, HIGH);
      } else if (label == "RY") {
        digitalWrite(redLed, HIGH);
        digitalWrite(yellowLed, HIGH);
      }
    } else {
      lcd.setCursor(0, 0);
      lcd.print("Zly format");
    }

    inputString = "";
    stringComplete = false;
  }
}

// ODCZYT DANYCH Z PYTHONA PRZEZ SERIAL PORT
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      stringComplete = true;
    } else {
      inputString += inChar;
    }
  }
}
