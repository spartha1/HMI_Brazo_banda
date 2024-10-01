#include <Servo.h>      // Incluye la biblioteca para controlar servos
#include <AFMotor.h>    // Incluye la biblioteca para controlar motores de corriente continua

#define LINE_BUFFER_LENGTH 512    // Define la longitud máxima del búfer para almacenar comandos seriales

//motor de banda
int speedMotor = 250;
int movimiento = 0; // 0= stop, 1= izquierda, 2= derecha

//Definsimos servos
Servo servo1;
Servo servo2;
Servo servo3;
Servo servo4;
Servo servo5;
Servo servo6;

//pines para banda
const byte dirPin1 = 12;
const byte dirPin2 = 13;
const byte dirPin3 = 2;
const byte dirPin4 = 3;
const byte speedPin1 = 5;
const byte speedPin2 = 4;

//pines para servos
const byte servoPin1 = 6;
const byte servoPin2 = 7;
const byte servoPin3 = 8;
const byte servoPin4 = 9;
const byte servoPin5 = 10;
const byte servoPin6 = 11;

//pin de sensor
int infrarrojo = A0;
int valor = 0;

//para comandos de visual
String inputString = "";
bool stringComplete = false;
bool obstacleDetected = false;
unsigned long obstacleDetectedTime = 0;

// Variables para el motor 2
unsigned long motor2StartTime = 0;
bool motor2Running = false;

void setup() {
  Serial.begin(9600);

  // configuracion de infrarojo
  pinMode(infrarrojo, INPUT);

  //Configuracion de banda
  pinMode(dirPin1, OUTPUT);
  pinMode(dirPin2, OUTPUT);
  pinMode(speedPin1, OUTPUT);
  pinMode(speedPin2, OUTPUT);

  //Configuracion de servos
  servo1.attach(servoPin1);
  servo1.write(30);
  servo2.attach(servoPin2);
  servo2.write(30);
  servo3.attach(servoPin3);
  servo3.write(30);
  servo4.attach(servoPin4);
  servo4.write(30);
  servo5.attach(servoPin5);
  servo5.write(30);
  servo6.attach(servoPin6);
  servo6.write(30);
}

void loop() {
  if (stringComplete) {
    inputString.trim();  //quita espacios o caracteres especiales
    Serial.print(inputString);  //imprime el comando en el monitor serial

    //procesar comandos
    processCommand();

    // limpiar el string
    inputString = "";
    stringComplete = false;
  }
  
  valor = digitalRead(infrarrojo);
  if (valor == LOW && !obstacleDetected) {
    Serial.println("Obstaculo detectado");
    detenerMotor();
    obstacleDetected = true;
    obstacleDetectedTime = millis();
  }
  if (obstacleDetected && millis() - obstacleDetectedTime >= 10000) {
    reanudarMovimiento();
    obstacleDetected = false;
  }

  // Detener el motor 2 después de 3 segundos
  if (motor2Running && millis() - motor2StartTime >= 3000) {
    detenerMotor2();
    motor2Running = false;
  }
}

void processCommand() {
  if (inputString.indexOf("$S1") != -1) {
    String turn = inputString.substring(3);
    MoveServo(servo1, turn.toInt());
  } else if (inputString.indexOf("$S2") != -1) {
    String turn = inputString.substring(3);
    MoveServo(servo2, turn.toInt());
  } else if (inputString.indexOf("$S3") != -1) {
    String turn = inputString.substring(3);
    MoveServo(servo3, turn.toInt());
  } else if (inputString.indexOf("$S4") != -1) {
    String turn = inputString.substring(3);
    MoveServo(servo4, turn.toInt());
  } else if (inputString.indexOf("$S5") != -1) {
    String turn = inputString.substring(3);
    MoveServo(servo5, turn.toInt());
  } else if (inputString.indexOf("$S6") != -1) {
    String turn = inputString.substring(3);
    MoveServo(servo6, turn.toInt());
  } else if (inputString.equals("$Bizq")) {
    moverMotor(LOW, HIGH);
    movimiento = 1;
  } else if (inputString.equals("$Bder")) {
    moverMotor(HIGH, LOW);
    movimiento = 2;
  } else if (inputString.equals("$Bstop")) {
    detenerMotor();
    movimiento = 0;
  } else if (inputString.equals("$Rizq")) {
    moverMotor2(LOW, HIGH);
    movimiento = 1;
  } else if (inputString.equals("$Rder")) {
    moverMotor2(HIGH, LOW);
    movimiento = 2;
  } else if (inputString.equals("$Rparar")) {
    detenerMotor2();
    movimiento = 0;
  }
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '\n') {
      stringComplete = true;
    } else {
      //se adiere al inputString
      inputString += inChar;
    }
  }
}

void MoveServo(Servo& servo, int targetPosition) {
  int currentPos = servo.read();
  if (currentPos < targetPosition) {
    for (int pos = currentPos; pos <= targetPosition; pos++) {
      servo.write(pos);
      delay(15); // Ajusta este valor para un movimiento más lento o más rápido
    }
  } else {
    for (int pos = currentPos; pos >= targetPosition; pos--) {
      servo.write(pos);
      delay(15); // Ajusta este valor para un movimiento más lento o más rápido
    }
  }
}

void detenerMotor() {
  digitalWrite(dirPin1, LOW);
  digitalWrite(dirPin2, LOW);
}

void detenerMotor2() {
  digitalWrite(dirPin3, LOW);
  digitalWrite(dirPin4, LOW);
}

void moverMotor(int direccion1, int direccion2) {
  analogWrite(speedPin1, speedMotor);
  digitalWrite(dirPin1, direccion1);
  digitalWrite(dirPin2, direccion2);
}

void moverMotor2(int direccion3, int direccion4) {
  analogWrite(speedPin2, speedMotor);
  digitalWrite(dirPin3, direccion3);
  digitalWrite(dirPin4, direccion4);
  motor2StartTime = millis();  // Registrar el tiempo de inicio
  motor2Running = true;        // Indicar que el motor 2 está funcionando
}

void reanudarMovimiento() {
  if (movimiento == 1) {
    moverMotor(LOW, HIGH);
  } else if (movimiento == 2) {
    moverMotor(HIGH, LOW);
  }
}

