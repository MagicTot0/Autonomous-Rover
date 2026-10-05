#pragma once

#include <stdint.h>

struct ScanPoint
{
    uint16_t angle_deg;
    float distance_cm;
    uint32_t timestamp_ms;
};