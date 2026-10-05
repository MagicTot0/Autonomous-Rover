#include "HCSR04.h"

HCSR04::HCSR04(uint8_t trigPin, uint8_t echoPin)
    : _trigPin(trigPin),
      _echoPin(echoPin)
{
}

void HCSR04::begin()
{
    pinMode(_trigPin, OUTPUT);
    pinMode(_echoPin, INPUT);

    digitalWrite(_trigPin, LOW);
}

float HCSR04::measureDistanceCm()
{
    // Ensure the trigger starts LOW.
    digitalWrite(_trigPin, LOW);
    delayMicroseconds(2);

    // Send the 10 us trigger pulse required by the HC-SR04.
    digitalWrite(_trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(_trigPin, LOW);

    // Measure the duration of the returned echo pulse.
    unsigned long duration = pulseIn(
        _echoPin,
        HIGH,
        ECHO_TIMEOUT_US
    );

    // No echo received within the timeout.
    if (duration == 0)
    {
        return -1.0f;
    }

    // Convert echo travel time into distance.
    //
    // The pulse represents the round trip:
    // sensor -> object -> sensor
    //
    // Therefore divide by 2.
    float distanceCm =
        (duration * SOUND_SPEED_CM_PER_US) / 2.0f;

    // Reject measurements outside the useful HC-SR04 range.
    if (distanceCm < MIN_DISTANCE_CM ||
        distanceCm > MAX_DISTANCE_CM)
    {
        return -1.0f;
    }

    return distanceCm;
}

ScanPoint HCSR04::measure(uint16_t angleDeg)
{
    ScanPoint point;

    point.angle_deg = angleDeg;
    point.distance_cm = measureDistanceCm();
    point.timestamp_ms = millis();

    return point;
}