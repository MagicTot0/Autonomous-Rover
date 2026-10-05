#include <Arduino.h>
#include "HCSR04.h"

constexpr uint8_t TRIG_PIN = 7;
constexpr uint8_t ECHO_PIN = 6;

HCSR04 sonar(TRIG_PIN, ECHO_PIN);

void setup()
{
    Serial.begin(115200);

    sonar.begin();

    Serial.println("HC-SR04 sensor subsystem");
    Serial.println("READY");
}

void loop()
{
    ScanPoint point = sonar.measure(0);

    if (point.distance_cm < 0.0f)
    {
        Serial.print("SCAN,");
        Serial.print(point.angle_deg);
        Serial.print(",ERROR,");
        Serial.println(point.timestamp_ms);
    }
    else
    {
        Serial.print("SCAN,");
        Serial.print(point.angle_deg);
        Serial.print(",");
        Serial.print(point.distance_cm, 2);
        Serial.print(",");
        Serial.println(point.timestamp_ms);
    }

    delay(100);
}