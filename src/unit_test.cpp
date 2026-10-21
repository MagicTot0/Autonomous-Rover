
#include <Arduino.h>

#include "unit_test.h"
#include "ServoScanner.h"
#include "HCSR04.h"

// ============================================================
// Hardware configuration
// ============================================================

constexpr uint8_t SERVO_PIN = 9;
constexpr uint8_t TRIG_PIN = 7;
constexpr uint8_t ECHO_PIN = 6;

constexpr int MIN_SERVO_ANGLE = 10;
constexpr int MAX_SERVO_ANGLE = 170;

constexpr float MIN_EXPECTED_CHANGE_CM = 5.0f;

// ============================================================
// Hardware instances
// ============================================================

static ServoScanner scanner(
    SERVO_PIN,
    MIN_SERVO_ANGLE,
    MAX_SERVO_ANGLE
);

static HCSR04 sonar(TRIG_PIN, ECHO_PIN);

// ============================================================
// Serial input helper
// ============================================================

char waitForInput()
{
    while (true)
    {
        if (Serial.available() > 0)
        {
            char input = Serial.read();

            if (input != '\r' && input != '\n')
            {
                return input;
            }
        }
    }
}

// ============================================================
// Test 1: Servo
// ============================================================

bool testServo()
{
    Serial.println();
    Serial.println("========== SERVO TEST ==========");

    scanner.begin();
    delay(500);

    for (int angle = -90; angle <= 90; angle += 5)
    {
        scanner.setRoverAngle(angle);
        delay(100);
    }

    scanner.setRoverAngle(0);
    delay(500);

    Serial.println("Did the servo sweep and return to centre?");
    Serial.println("Enter Y or N:");

    while (true)
    {
        char answer = waitForInput();

        if (answer == 'Y' || answer == 'y')
        {
            Serial.println("SERVO: PASS");
            return true;
        }

        if (answer == 'N' || answer == 'n')
        {
            Serial.println("SERVO: FAIL");
            return false;
        }

        Serial.println("Please enter Y or N:");
    }
}

// ============================================================
// Test 2: HC-SR04 state change
// ============================================================

bool testHCSR04()
{
    Serial.println();
    Serial.println("========== HC-SR04 TEST ==========");

    sonar.begin();

    Serial.println("STEP 1: Place an object about 20 cm away.");
    Serial.println("Enter C when ready:");

    while (waitForInput() != 'C' && Serial.available() == 0)
    {
        // Wait for user confirmation.
    }

    float firstDistance = sonar.measureDistanceCm();

    Serial.print("First reading: ");
    Serial.print(firstDistance);
    Serial.println(" cm");

    Serial.println();
    Serial.println("STEP 2: Move the object about 10-20 cm.");
    Serial.println("Enter C when ready:");

    while (waitForInput() != 'C')
    {
        // Wait for user confirmation.
    }

    float secondDistance = sonar.measureDistanceCm();

    Serial.print("Second reading: ");
    Serial.print(secondDistance);
    Serial.println(" cm");

    bool validReadings =
        firstDistance >= 2.0f &&
        firstDistance <= 400.0f &&
        secondDistance >= 2.0f &&
        secondDistance <= 400.0f;

    bool stateChanged =
        validReadings &&
        abs(firstDistance - secondDistance) >= MIN_EXPECTED_CHANGE_CM;

    if (stateChanged)
    {
        Serial.println("HC-SR04: PASS - distance changed.");
        return true;
    }

    Serial.println("HC-SR04: FAIL");

    if (!validReadings)
    {
        Serial.println("Reason: One or both readings were invalid.");
    }
    else
    {
        Serial.println("Reason: Distance did not change enough.");
    }

    return false;
}

// ============================================================
// Main test sequence
// ============================================================

void runComponentTests()
{
    Serial.println();
    Serial.println("=== AUTONOMOUS ROVER COMPONENT TESTS ===");

    bool servoPassed = testServo();
    bool sensorPassed = testHCSR04();

    Serial.println();
    Serial.println("========== SUMMARY ==========");
    Serial.println(servoPassed ? "Servo: PASS" : "Servo: FAIL");
    Serial.println(sensorPassed ? "HC-SR04: PASS" : "HC-SR04: FAIL");
}
