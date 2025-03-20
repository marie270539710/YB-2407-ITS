#include <Servo.h> //includes the servo library
#include <LiquidCrystal_I2C.h> //includes LiquidCrystal_I2C library

#define IR_entry 13
#define IR_exit 11

LiquidCrystal_I2C lcd(0x27, 16, 2);

Servo servo_entry, servo_exit;

// 2 = P1
// 3 = P2
// 4 = D1
// 5 = P4
// 6 = P3
// 7 = E1
// Index 0 is unused so that index 1 corresponds to "P1", 2 to "P2", etc.
const char* parking_ids[] = {"P1", "P2", "D1", "P4", "P3", "EV"};

int IR_parking[6] = {2, 3, 4, 5, 6, 7};
int parking_slot = 6;
int parking_free = 0;
int servo_pos = 90;
//int sensorValue = analogRead(A0);

String Msg_parking = "";
String Msg_available = "";

void setup()
{
  servo_entry.attach(12);
  servo_exit.attach(10);
  
  //Inital position at 0 for both motors
  servo_entry.write(servo_pos);
  servo_exit.write(servo_pos);
  
  // Initialize the LED display
  lcd.init();
  lcd.setCursor(0,0);
  lcd.backlight();
  lcd.display();
  
  pinMode(IR_entry, INPUT); 
  pinMode(IR_exit, INPUT); 

}

void loop()
{
  Serial.begin(9600);
  
  // Print text on display
  lcd.setCursor(0,0);
  lcd.print("   ABCS SMART   ");
  lcd.setCursor(0,1);
  lcd.print(" Parking System "); 
  delay(1000);
  
  // Check parking slots
  checkParkingSlots();

  // Display available parking slots
  lcd.setCursor(0,0);
  lcd.print("Free Slots: ");
  lcd.print(parking_free);
  lcd.setCursor(0,1);
  lcd.print(Msg_parking);
  lcd.print("          ");
  delay(1000);
  
  Serial.println("AVAILABLE: " + Msg_available);
  delay(1000);
  //Serial.println(sensorValue);
  
  if (digitalRead(IR_entry)==0) {
    if(parking_free==0) {
    	lcd.setCursor(0,0);
  		lcd.print("Please wait...");
  		lcd.print("          ");
  		delay(1000);
    } else {
      lcd.setCursor(0,0);
  		lcd.print("Entry");
      servo_entry.write(servo_pos-90);
      delay(500);
    }
  } else {
    servo_entry.write(servo_pos);
  }
  
  if (digitalRead(IR_exit)==0) {
    lcd.print("Exit");
    servo_exit.write(servo_pos-90);
    delay(500);
  } else {
    servo_exit.write(servo_pos);
  }
}

void checkParkingSlots() {
  // Reset to total number of available slots
  parking_free = 6; 
  Msg_parking = "";
  Msg_available = "";
  
  for (int i = 0; i < parking_slot; i++) {
    //if (checkParkingAvailable(IR_parking[i]) == 1) { // condition for ultrasonic sensor
    if (digitalRead(IR_parking[i]) == 0) { // condition for ir sensor
      Serial.print("Slot ");
      Serial.print(i+1);
      Serial.println(" is occupied");
      parking_free--; // Deduct from free parking slots
    } else {
      //Msg_parking = Msg_parking + "#" + String(i+1) + " | ";
      Msg_parking = Msg_parking + parking_ids[i] + "|";
      Msg_available = Msg_available + String(i+1) + "|";
    }
  }
  
  if(parking_free == 0) {
    Msg_parking = "FULL PARKING!";
  }
}

int checkParkingAvailable(int ir_car) {
  long Duration, Cm;
  
  pinMode(ir_car, OUTPUT);
  digitalWrite(ir_car, HIGH);
  
  pinMode(ir_car, INPUT);
  Duration = pulseIn(ir_car, HIGH);

  Cm = Duration / 29 / 2;
  if(Cm < 100) {
    return 1;
  } else {
    return 0;
  }
}