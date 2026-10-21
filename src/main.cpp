#include <Arduino.h>
#include <Servo.h>
#include "unit_test.h"
#include "scan_integration.h"

Servo servo;

void setup()
{
        Serial.begin(115200);

    //runComponentTests(); tests components 

    runScannerIntegration(); // sensor + gyro integration

}

void loop()
{
}