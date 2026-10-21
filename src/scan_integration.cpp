
#include <Arduino.h>

#include "scan_integration.h"
#include "HCSR04.h"
#include "ServoScanner.h"

// ============================================================
// Hardware configuration
// ============================================================

constexpr uint8_t SERVO_PIN = 9;
constexpr uint8_t TRIG_PIN = 7;
constexpr uint8_t ECHO_PIN = 6;

constexpr int MIN_SERVO_ANGLE = 10;
constexpr int MAX_SERVO_ANGLE = 170;

constexpr int MIN_SCAN_ANGLE = -90;
constexpr int MAX_SCAN_ANGLE = 90;
constexpr int SCAN_STEP_DEG = 5;

constexpr unsigned long SERVO_SETTLE_MS = 60;
constexpr unsigned long STARTUP_DELAY_MS = 500;

// ============================================================
// Hardware instances
// ============================================================

ServoScanner scanner(
    SERVO_PIN,
    MIN_SERVO_ANGLE,
    MAX_SERVO_ANGLE
);

HCSR04 sonar(TRIG_PIN, ECHO_PIN);

// ============================================================
// Scan point output
// Format: SCAN,<angle>,<distance>,<timestamp>
// ============================================================

void measureAndTransmit(int angle)
{
    float distance = sonar.measureDistanceCm();
    unsigned long timestamp = millis();

    Serial.print("SCAN,");
    Serial.print(angle);
    Serial.print(",");

    if (distance < 0.0f)
    {
        Serial.print("ERROR");
    }
    else
    {
        Serial.print(distance, 2);
    }

    Serial.print(",");
    Serial.println(timestamp);
}

// ============================================================
// Scan one position
// ============================================================

void scanPosition(int angle)
{
    scanner.setRoverAngle(angle);

    // Allow the servo to reach its commanded position.
    delay(SERVO_SETTLE_MS);

    measureAndTransmit(angle);
}

// ============================================================
// Main integration function
// ============================================================

void runScannerIntegration()
{
    sonar.begin();
    scanner.begin();

    // Position the sensor at the leftmost scan angle.
    scanner.setRoverAngle(MIN_SCAN_ANGLE);
    delay(STARTUP_DELAY_MS);

    while (true)
    {
        // Sweep left to right.
        for (
            int angle = MIN_SCAN_ANGLE;
            angle <= MAX_SCAN_ANGLE;
            angle += SCAN_STEP_DEG
        )
        {
            scanPosition(angle);
        }

        // Sweep right to left without repeating the endpoint.
        for (
            int angle = MAX_SCAN_ANGLE - SCAN_STEP_DEG;
            angle >= MIN_SCAN_ANGLE;
            angle -= SCAN_STEP_DEG
        )
        {
            scanPosition(angle);
        }
    }
}
