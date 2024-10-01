#include <Servo.h>

// Definir los servomotores
Servo servo1;
Servo servo2;
Servo servo3;
Servo servoGripper;

// Definir los pines de los servomotores
const int servo1Pin = 3;
const int servo2Pin = 5;
const int servo3Pin = 6;
const int servoGripperPin = 9;

void setup() {
  // Adjuntar los servomotores a sus pines
  servo1.attach(servo1Pin);
  servo2.attach(servo2Pin);
  servo3.attach(servo3Pin);
  servoGripper.attach(servoGripperPin);

  // Inicializar la comunicación serie
  Serial.begin(115200);
}

void loop() {
  // Leer los comandos de la interfaz serial
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }
}

void processCommand(String command) {
  // Procesar los comandos recibidos
  if (command.startsWith("X")) {
    int angle1 = command.substring(1, command.indexOf("Y")).toInt();
    int angle2 = command.substring(command.indexOf("Y") + 1, command.indexOf("Z")).toInt();
    int angle3 = command.substring(command.indexOf("Z") + 1).toInt();
    moveServos(angle1, angle2, angle3);
  } else if (command == "M3") {
    // Tomar (cerrar el gripper)
    servoGripper.write(0);
  } else if (command == "M4") {
    // Soltar (abrir el gripper)
    servoGripper.write(90);
  }
}

void moveServos(int angle1, int angle2, int angle3) {
  // Mover los servos a los ángulos especificados
  servo1.write(angle1);
  servo2.write(angle2);
  servo3.write(angle3);
}

