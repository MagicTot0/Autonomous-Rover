import math
import serial
import matplotlib.pyplot as plt


# ============================================================
# Configuration
# ============================================================

SERIAL_PORT = "COM3"
BAUD_RATE = 115200

MAX_DISTANCE_CM = 400.0

MIN_ANGLE_DEG = -90
MAX_ANGLE_DEG = 90


# ============================================================
# Serial communication
# ============================================================

def open_serial():
    """
    Open the Arduino serial connection.
    """

    print(f"Opening serial port {SERIAL_PORT}...")

    connection = serial.Serial(
        SERIAL_PORT,
        BAUD_RATE,
        timeout=1
    )

    print("Serial connection established.")

    return connection


def parse_scan_line(line):
    """
    Parse an Arduino SCAN message.

    Expected format:

        SCAN,<angle>,<distance>,<timestamp>

    Example:

        SCAN,0,37.42,1023

    Returns:

        (angle, distance, timestamp)

    or None if the line is invalid.
    """

    line = line.strip()

    if not line.startswith("SCAN,"):
        return None

    fields = line.split(",")

    if len(fields) != 4:
        return None

    try:
        angle = int(fields[1])

        if fields[2] == "ERROR":
            return None

        distance = float(fields[2])
        timestamp = int(fields[3])

    except ValueError:
        return None

    return angle, distance, timestamp


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

        # ----------------------------------------------------
        # Radar orientation
        # ----------------------------------------------------

        # 0° is straight ahead.
        self.ax.set_theta_zero_location("N")

        # Positive angles increase clockwise.
        self.ax.set_theta_direction(-1)

        # Display only the forward 180°.
        self.ax.set_thetamin(MIN_ANGLE_DEG)
        self.ax.set_thetamax(MAX_ANGLE_DEG)

        # ----------------------------------------------------
        # Distance range
        # ----------------------------------------------------

        self.ax.set_rlim(
            0,
            MAX_DISTANCE_CM
        )

        # Distance rings every 1 metre.
        distance_ticks = [
            100,
            200,
            300,
            400
        ]

        self.ax.set_rticks(distance_ticks)

        # Hide Matplotlib's automatic radial labels.
        self.ax.set_yticklabels([])

        # ----------------------------------------------------
        # Distance labels
        # ----------------------------------------------------

        # Place our own labels along the 0° direction.
        #
        # Because 0° points North in the radar coordinate
        # system, these are positioned slightly to the
        # right of the centre using a small angular offset.

        label_angle = math.radians(88)

        for distance in distance_ticks:

            self.ax.text(
                label_angle,
                distance,
                f"{distance / 100:.0f} m",
                ha="left",
                va="center",
                fontsize=9
            )

        # ----------------------------------------------------
        # Angle labels
        # ----------------------------------------------------

        self.ax.set_thetagrids(
            [-90, -45, 0, 45, 90],
            labels=[
                "-90°",
                "-45°",
                "0°",
                "45°",
                "90°"
            ]
        )

        # ----------------------------------------------------
        # Title
        # ----------------------------------------------------

        self.ax.set_title(
            "Autonomous Rover — HC-SR04 Scan",
            pad=20
        )

        # ----------------------------------------------------
        # Scan points
        # ----------------------------------------------------

        self.points, = self.ax.plot(
            [],
            [],
            "."
        )

    def update(self, scan):
        """
        Update the radar with a collection of measurements.
        """

        angles = []
        distances = []

        for angle_deg, distance_cm, timestamp_ms in scan:

            if not (
                MIN_ANGLE_DEG
                <= angle_deg
                <= MAX_ANGLE_DEG
            ):
                continue

            if distance_cm < 0:
                continue

            if distance_cm > MAX_DISTANCE_CM:
                continue

            angles.append(
                math.radians(angle_deg)
            )

            distances.append(
                distance_cm
            )

        self.points.set_data(
            angles,
            distances
        )

        self.fig.canvas.draw_idle()

    def is_open(self):
        return plt.fignum_exists(
            self.fig.number
        )



# ============================================================
# Main application
# ============================================================
def main():

    print("Autonomous Rover HC-SR04 Visualizer")
    print("------------------------------------")

    try:
        serial_connection = open_serial()

    except serial.SerialException as error:

        print()
        print("ERROR: Could not open the serial port.")
        print(error)
        print()
        print("Check:")
        print("  - Arduino is connected")
        print("  - SERIAL_PORT is correct")
        print("  - PlatformIO Serial Monitor is closed")

        return

    visualizer = RadarVisualizer()

    # Explicitly display the window before entering
    # the serial-reading loop.
    plt.show(block=False)

    scan = []

    try:

        while visualizer.is_open():

            line = (
                serial_connection
                .readline()
                .decode(
                    "utf-8",
                    errors="ignore"
                )
            )

            measurement = parse_scan_line(line)

            if measurement is None:
                plt.pause(0.01)
                continue

            scan.append(measurement)

            visualizer.update(scan)

            plt.pause(0.001)

    except KeyboardInterrupt:

        print("\nVisualizer stopped.")

    finally:

        serial_connection.close()

        print("Serial connection closed.")

        plt.close()


if __name__ == "__main__":
    main()