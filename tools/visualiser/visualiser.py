
"""
Autonomous Rover — HC-SR04 Radar Visualizer

Serial protocol:
    SCAN,<angle>,<distance>,<timestamp>

Example:
    SCAN,-90,37.42,1023

Install dependencies:
    pip install pyserial matplotlib
"""

import math
import serial
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from collections import deque


# ============================================================
# Configuration
# ============================================================

SERIAL_PORT = "COM3"
BAUD_RATE = 115200
SERIAL_TIMEOUT = 1

MIN_ANGLE_DEG = -90.0
MAX_ANGLE_DEG = 90.0
MAX_DISTANCE_CM = 200.0

MAX_VISIBLE_PASSES = 5
DIAGNOSTICS = True

PASS_COLORS = [
    "deepskyblue",
    "tomato",
    "limegreen",
    "gold",
    "magenta",
]


# ============================================================
# Serial parsing
# ============================================================

def parse_scan_line(line):
    """
    Parse:
        SCAN,<angle>,<distance>,<timestamp>

    Returns:
        (angle, distance, timestamp), or None if invalid.
    """

    line = line.strip()

    if not line:
        return None

    fields = [field.strip() for field in line.split(",")]

    if len(fields) != 4:
        return None

    if fields[0] != "SCAN":
        return None

    angle_text = fields[1]
    distance_text = fields[2]
    timestamp_text = fields[3]

    if distance_text.upper() == "ERROR":
        return None

    try:
        angle = float(angle_text)
        distance = float(distance_text)
        timestamp = int(timestamp_text)
    except (ValueError, TypeError, OverflowError):
        return None

    if not all(math.isfinite(value) for value in (angle, distance)):
        return None

    if not MIN_ANGLE_DEG <= angle <= MAX_ANGLE_DEG:
        return None

    if distance < 0:
        return None

    return angle, distance, timestamp


# ============================================================
# Radar visualizer
# ============================================================

class RadarVisualizer:

    def __init__(self):

        self.fig = plt.figure(figsize=(11, 7))

        # Radar area
        self.ax = self.fig.add_axes(
            [0.07, 0.15, 0.68, 0.75],
            projection="polar"
        )

        # Clear screen button
        button_ax = self.fig.add_axes(
            [0.30, 0.035, 0.25, 0.065]
        )

        self.clear_button = Button(
            button_ax,
            "Clear screen"
        )

        self.clear_button.on_clicked(self.clear_screen)

        # Most recent completed and active passes
        self.passes = deque()
        self.current_pass = None
        self.next_pass_number = 1

        # Sweep tracking
        self.last_angle = None
        self.last_delta_direction = 0
        self.direction = 0

        # Require two consecutive angle changes in the
        # opposite direction before declaring a new pass.
        self.reversal_count = 0
        self.required_reversal_count = 2

        self._configure_axes()

        self.fig.canvas.manager.set_window_title(
            "Autonomous Rover — HC-SR04 Visualizer"
        )

    def _configure_axes(self):

        self.ax.set_theta_zero_location("N")
        self.ax.set_theta_direction(-1)

        self.ax.set_thetamin(MIN_ANGLE_DEG)
        self.ax.set_thetamax(MAX_ANGLE_DEG)

        self.ax.set_rlim(0, MAX_DISTANCE_CM)

        self.ax.set_rticks([50, 100, 150, 200])
        self.ax.set_yticklabels([
            "0.5 m",
            "1.0 m",
            "1.5 m",
            "2.0 m"
        ])

        self.ax.set_rlabel_position(135)

        self.ax.set_thetagrids(
            [-90, -45, 0, 45, 90],
            labels=[
                "-90°",
                "-45°",
                "0°",
                "+45°",
                "+90°"
            ]
        )

        self.ax.set_title(
            "Autonomous Rover — HC-SR04 Scan",
            pad=20
        )

        self.ax.grid(True, alpha=0.4)

    # --------------------------------------------------------
    # Pass management
    # --------------------------------------------------------

    def _start_new_pass(self, direction):

        number = self.next_pass_number
        self.next_pass_number += 1

        color = PASS_COLORS[
            (number - 1) % len(PASS_COLORS)
        ]

        artist = self.ax.scatter(
            [],
            [],
            s=24,
            color=color,
            label=f"Pass {number}",
            zorder=3
        )

        self.current_pass = {
            "number": number,
            "direction": direction,
            "color": color,
            "measurements": [],
            "artist": artist
        }

        self.passes.append(self.current_pass)

        # Remove the oldest pass when exceeding the limit.
        while len(self.passes) > MAX_VISIBLE_PASSES:

            old_pass = self.passes.popleft()
            old_pass["artist"].remove()

        self._refresh_legend()

        if DIAGNOSTICS:

            if direction > 0:
                direction_text = "-90° to +90°"
            else:
                direction_text = "+90° to -90°"

            print(
                f"[PASS] Pass {number} started: "
                f"{direction_text}, colour={color}"
            )

    def _refresh_legend(self):

        old_legend = self.ax.get_legend()

        if old_legend is not None:
            old_legend.remove()

        if not self.passes:
            return

        handles = []
        labels = []

        for scan_pass in self.passes:

            handles.append(scan_pass["artist"])

            if scan_pass["direction"] > 0:
                direction_text = "→"
            else:
                direction_text = "←"

            labels.append(
                f"Pass {scan_pass['number']} {direction_text}"
            )

        self.ax.legend(
            handles,
            labels,
            loc="upper left",
            bbox_to_anchor=(1.05, 1.0),
            title="Scan passes",
            fontsize=8
        )

    # --------------------------------------------------------
    # Sweep direction detection
    # --------------------------------------------------------

    def _process_angle(self, angle):

        if self.last_angle is None:

            self.last_angle = angle
            return

        delta = angle - self.last_angle

        # Ignore small fluctuations or repeated angles.
        if abs(delta) < 1.0:
            return

        observed_direction = 1 if delta > 0 else -1

        if self.direction == 0:

            # Initial direction is established from the first
            # meaningful angle movement.
            self.direction = observed_direction

            self._start_new_pass(self.direction)

        elif observed_direction == self.direction:

            # Movement has returned to the established direction.
            self.reversal_count = 0

        else:

            # Possible new pass: servo has reversed direction.
            self.reversal_count += 1

            if self.reversal_count >= self.required_reversal_count:

                self.direction = observed_direction
                self.reversal_count = 0

                self._start_new_pass(self.direction)

        self.last_angle = angle

    # --------------------------------------------------------
    # Live data update
    # --------------------------------------------------------

    def update(self, measurement):

        if measurement is None:
            return

        angle, distance, timestamp = measurement

        # Detect pass changes even when a measurement is
        # outside the displayed distance range.
        self._process_angle(angle)

        # Filter readings outside the 2 m display range.
        if distance > MAX_DISTANCE_CM:

            if DIAGNOSTICS:
                print(
                    f"[FILTER] {angle:.1f}°: "
                    f"{distance:.2f} cm exceeds 200 cm"
                )

            return

        if self.current_pass is None:
            return

        # Store this reading in the active pass.
        self.current_pass["measurements"].append(
            (angle, distance, timestamp)
        )

        measurements = self.current_pass["measurements"]

        angles = [
            math.radians(item[0])
            for item in measurements
        ]

        distances = [
            item[1]
            for item in measurements
        ]

        # Update this pass only. Other passes retain their colours.
        self.current_pass["artist"].set_offsets(
            list(zip(angles, distances))
        )

        if DIAGNOSTICS:
            print(
                f"[DATA] Pass {self.current_pass['number']} | "
                f"Angle: {angle:6.1f}° | "
                f"Distance: {distance:7.2f} cm | "
                f"Timestamp: {timestamp}"
            )

        self.fig.canvas.draw_idle()

    # --------------------------------------------------------
    # Clear screen
    # --------------------------------------------------------

    def clear_screen(self, event=None):

        self.passes.clear()
        self.current_pass = None
        self.next_pass_number = 1

        self.last_angle = None
        self.last_delta_direction = 0
        self.direction = 0
        self.reversal_count = 0

        self.ax.clear()
        self._configure_axes()

        self.fig.canvas.draw_idle()

        if DIAGNOSTICS:
            print("[UI] Screen cleared.")

    def is_open(self):

        return plt.fignum_exists(self.fig.number)


# ============================================================
# Main application
# ============================================================

def main():

    print("Autonomous Rover HC-SR04 Visualizer")
    print("------------------------------------")
    print(f"Serial port: {SERIAL_PORT}")
    print(f"Baud rate: {BAUD_RATE}")
    print(f"Maximum range: {MAX_DISTANCE_CM:.0f} cm")
    print()

    visualizer = RadarVisualizer()

    try:

        connection = serial.Serial(
            SERIAL_PORT,
            BAUD_RATE,
            timeout=SERIAL_TIMEOUT
        )

        # Clear startup messages from the serial buffer.
        connection.reset_input_buffer()

        print("Serial connection established.")
        print("Waiting for SCAN messages...")

    except (serial.SerialException, OSError) as error:

        print("\nERROR: Could not open the serial port.")
        print(error)
        print("\nCheck:")
        print("  - Arduino is connected")
        print("  - SERIAL_PORT is correct")
        print("  - PlatformIO Serial Monitor is closed")

        plt.close(visualizer.fig)
        return

    try:

        while visualizer.is_open():

            raw_line = connection.readline()

            if not raw_line:
                plt.pause(0.01)
                continue

            line = raw_line.decode(
                "utf-8",
                errors="replace"
            ).strip()

            if not line:
                continue

            measurement = parse_scan_line(line)

            if measurement is None:

                if DIAGNOSTICS:
                    print(f"[IGNORED] {line!r}")

                plt.pause(0.001)
                continue

            visualizer.update(measurement)

            # Keep the Matplotlib interface responsive.
            plt.pause(0.001)

    except KeyboardInterrupt:

        print("\n[INFO] Visualizer stopped.")

    except (serial.SerialException, OSError) as error:

        print(f"\n[SERIAL ERROR] {error}")

    finally:

        if connection.is_open:
            connection.close()

        print("[INFO] Serial connection closed.")
        plt.close("all")


if __name__ == "__main__":
    main()
