#include "ServoScanner.h"

ServoScanner::ServoScanner(
    uint8_t servoPin,
    int minServoAngle,
    int maxServoAngle
)
    : _servoPin(servoPin),
      _minServoAngle(minServoAngle),
      _maxServoAngle(maxServoAngle),
      _roverAngle(0)
{
}

void ServoScanner::begin()
{
    _servo.attach(_servoPin);

    // Start facing straight ahead.
    setRoverAngle(0);
}

void ServoScanner::setRoverAngle(int roverAngle)
{
    roverAngle = constrain(
        roverAngle,
        -90,
        90
    );

    _roverAngle = roverAngle;

    int servoAngle = roverToServoAngle(
        roverAngle
    );

    _servo.write(servoAngle);
}

int ServoScanner::getRoverAngle() const
{
    return _roverAngle;
}

int ServoScanner::roverToServoAngle(int roverAngle) const
{
    /*
     * Convert rover coordinates:
     *
     *     -90° = left
     *       0° = forward
     *     +90° = right
     *
     * into physical servo coordinates.
     *
     * The servo's physical range is defined by:
     *
     *     _minServoAngle
     *     _maxServoAngle
     */

    return map(
        roverAngle,
        -90,
        90,
        _minServoAngle,
        _maxServoAngle
    );
}