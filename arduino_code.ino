// Smart Traffic Management System for Emergency Vehicles
// Arduino code for controlling traffic lights based on ultrasonic sensor distance

#define TRIG_PIN_1 2
#define ECHO_PIN_1 3
#define TRIG_PIN_2 4
#define ECHO_PIN_2 5
#define TRIG_PIN_3 6
#define ECHO_PIN_3 7

#define GREEN_LED_1 8
#define RED_LED_1 9
#define GREEN_LED_2 10
#define RED_LED_2 11
#define GREEN_LED_3 12
#define RED_LED_3 13

bool processedNode1 = false;
bool processedNode2 = false;
bool processedNode3 = false;

void setup() {
  pinMode(TRIG_PIN_1, OUTPUT);
  pinMode(ECHO_PIN_1, INPUT);
  pinMode(TRIG_PIN_2, OUTPUT);
  pinMode(ECHO_PIN_2, INPUT);
  pinMode(TRIG_PIN_3, OUTPUT);
  pinMode(ECHO_PIN_3, INPUT);

  pinMode(GREEN_LED_1, OUTPUT);
  pinMode(RED_LED_1, OUTPUT);
  pinMode(GREEN_LED_2, OUTPUT);
  pinMode(RED_LED_2, OUTPUT);
  pinMode(GREEN_LED_3, OUTPUT);
  pinMode(RED_LED_3, OUTPUT);

  Serial.begin(9600);
}

void loop() {
  // Step 1: Node 1 logic
  if (!processedNode1) {
    float distance1 = getDistance(TRIG_PIN_1, ECHO_PIN_1);
    Serial.print("Node 1 Distance: ");
    Serial.println(distance1);

    if (distance1 < 20) { // Threshold for Node 1 (ambulance is near)
      activateTrafficLight(GREEN_LED_1, RED_LED_1);
      processedNode1 = true; // Move to Node 2 logic after Node 1 is processed
    } else {
      // If distance is not below threshold, turn red light on and keep waiting
      activateTrafficLight(RED_LED_1, GREEN_LED_1);
    }
    delay(5000);
    if(distance1 < 10){
        activateTrafficLight(RED_LED_1,GREEN_LED_1);
    }
    
  }

  // Step 2: Node 2 logic (after Node 1 is processed)
  if (processedNode1 && !processedNode2) {
    float distance2 = getDistance(TRIG_PIN_2, ECHO_PIN_2);
    Serial.print("Node 2 Distance: ");
    Serial.println(distance2);

    if (distance2 < 20) { // Threshold for Node 2 (ambulance is near)
      activateTrafficLight(GREEN_LED_2, RED_LED_2);
      processedNode2 = true; // Move to Node 3 logic after Node 2 is processed
    } else {
      // If distance is not below threshold, turn red light on and keep waiting
      activateTrafficLight(RED_LED_2, GREEN_LED_2);
    }
    delay(5000);
    if(distance2 < 10){
        activateTrafficLight(RED_LED_2,GREEN_LED_2);
    }
    
  }

  // Step 3: Node 3 logic (after Node 2 is processed)
  if (processedNode2 && !processedNode3) {
    float distance3 = getDistance(TRIG_PIN_3, ECHO_PIN_3);
    Serial.print("Node 3 Distance: ");
    Serial.println(distance3);

    if (distance3 < 20) { // Threshold for Node 3 (ambulance is near)
      activateTrafficLight(GREEN_LED_3, RED_LED_3);
      processedNode3 = true; // All nodes processed after Node 3 is processed
    } else {
      // If distance is not below threshold, turn red light on and keep waiting
      activateTrafficLight(RED_LED_3, GREEN_LED_3);
    }
    delay(5000);
    if(distance3 < 10){
        activateTrafficLight(RED_LED_3,GREEN_LED_3);
    }
  }

  delay(500); // Small delay for sensor readings to avoid overloading
}

// Function to calculate distance using the HC-SR04 ultrasonic sensor
float getDistance(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH);
  return duration * 0.034 / 2; // Convert to cm
}

// Function to activate the corresponding green and red lights
void activateTrafficLight(int greenLed, int redLed) {
  digitalWrite(greenLed, HIGH);
  digitalWrite(redLed, LOW);
}

