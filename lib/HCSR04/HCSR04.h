#pragma once

#include <Arduino.h>
#include "ScanPoint.h"

class HCSR04
{
public:
    HCSR04(uint8_t trigPin, uint8_t echoPin);

    void begin();

    float measureDistanceCm();

    ScanPoint measure(uint16_t angleDeg);

private:
    uint8_t _trigPin;
    uint8_t _echoPin;

    static constexpr float SOUND_SPEED_CM_PER_US = 0.0343f;
    static constexpr float MIN_DISTANCE_CM = 2.0f;
    static constexpr float MAX_DISTANCE_CM = 400.0f;
    static constexpr unsigned long ECHO_TIMEOUT_US = 25000UL;
};