import math
import random
import time

import matplotlib.pyplot as plt
import numpy as np


# ============================================================
# Configuration
# ============================================================

MAX_DISTANCE_CM = 400.0

# Angular field of view.
# 0° = straight ahead
# -90° = left
# +90° = right
MIN_ANGLE_DEG = -90
MAX_ANGLE_DEG = 90

# Set to True while developing without the Arduino.
SIMULATION_MODE = True

# Serial settings used later.
SERIAL_PORT = "COM3"
BAUD_RATE = 115200


# ============================================================
# Simulation
# ============================================================

def simulate_scan():
    """
    Generate simulated HC-SR04 scan data.

    Returns:
        list of (angle_deg, distance_cm, timestamp_ms)
    """

    scan = []

    timestamp = int(time.time() * 1000)

    for angle in range(MIN_ANGLE_DEG, MAX_ANGLE_DEG + 1, 3):

        # Default distance: far away.
        distance = 300.0

        # Simulated obstacle directly ahead.
        if -10 <= angle <= 10:
            distance = 80.0 + random.uniform(-3, 3)

        # Simulated obstacle on the left.
        elif -55 <= angle <= -40:
            distance = 140.0 + random.uniform(-5, 5)

        # Simulated obstacle on the right.
        elif 40 <= angle <= 55:
            distance = 190.0 + random.uniform(-5, 5)

        # Add small measurement noise.
        distance += random.uniform(-1.5, 1.5)

        scan.append(
            (angle, distance, timestamp)
        )

    return scan


# ============================================================
# Visualization
# ============================================================

class RadarVisualizer:

    def __init__(self):
        self.fig = plt.figure(figsize=(9, 5))

        self.ax = self.fig.add_subplot(
            111,
            projection="polar"
        )

        # Put 0° at the top.
        self.ax.set_theta_zero_location("N")

        # Positive angles go clockwise.
        self.ax.set_theta_direction(-1)

        # Only display the front 180°.
        self.ax.set_thetamin(MIN_ANGLE_DEG)
        self.ax.set_thetamax(MAX_ANGLE_DEG)

        # Distance range.
        self.ax.set_rlim(
            0,
            MAX_DISTANCE_CM
        )

        self.ax.set_title(
            "Autonomous Rover — HC-SR04 Scan"
        )

        # Measurement points.
        self.points, = self.ax.plot(
            [],
            [],
            "."
        )

    def update(self, scan):
        """
        Update the radar with a list of ScanPoint-like tuples.
        """

        angles = []
        distances = []

        for angle_deg, distance_cm, timestamp_ms in scan:

            if distance_cm < 0:
                continue

            if not (
                MIN_ANGLE_DEG
                <= angle_deg
                <= MAX_ANGLE_DEG
            ):
                continue

            if distance_cm > MAX_DISTANCE_CM:
                continue

            angle_rad = math.radians(angle_deg)

            angles.append(angle_rad)
            distances.append(distance_cm)

        self.points.set_data(
            angles,
            distances
        )

        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def show(self):
        plt.show()


# ============================================================
# Main
# ============================================================

def main():

    visualizer = RadarVisualizer()

    if SIMULATION_MODE:

        print("Running in simulation mode.")

        while plt.fignum_exists(
            visualizer.fig.number
        ):

            scan = simulate_scan()

            visualizer.update(scan)

            plt.pause(0.5)

    else:

        print("Serial mode not implemented yet.")

    visualizer.show()


if __name__ == "__main__":
    main()