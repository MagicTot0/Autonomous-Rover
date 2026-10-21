#pragma once

#include <Arduino.h>
#include <Servo.h>

class ServoScanner
{
public:
    ServoScanner(
        uint8_t servoPin,
        int minServoAngle,
        int maxServoAngle
    );

    void begin();

    void setRoverAngle(int roverAngle);

    int getRoverAngle() const;

private:
    uint8_t _servoPin;

    int _minServoAngle;
    int _maxServoAngle;

    int _roverAngle;

    Servo _servo;

    int roverToServoAngle(int roverAngle) const;
};