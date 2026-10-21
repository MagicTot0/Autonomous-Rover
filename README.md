Autonomous Rover

An Arduino-based autonomous rover developed as an embedded systems engineering project.

The project explores the progressive development of a small autonomous robotic platform, from low-level sensor and motor control to environment mapping and autonomous navigation. Particular attention is given to modular software architecture, communication, interoperability, and cybersecurity.

The project is developed incrementally, with each subsystem tested independently before being integrated into the complete rover.

Objectives

The main objectives of the project are to:

Build a functional two-wheel differential-drive rover.
Implement a front-facing sweeping ultrasonic sensor.
Measure wheel movement using wheel encoders.
Develop odometry from wheel encoder data.
Build an environment map from sensor observations.
Implement SLAM and autonomous navigation.
Develop a modular communication architecture.
Explore interoperability through standardized interfaces between subsystems.
Introduce cybersecurity mechanisms for rover communications.
Maintain professional engineering documentation throughout development.

Hardware

Microcontroller
Arduino UNO

Current sensors
HC-SR04 ultrasonic distance sensor
SG90 servo motor for ultrasonic sensor sweeping
SM-S2309S gyroscope/IMU — optional future sensor

Mobility
Two DC motors for differential drive
Wheel encoders — planned
Motor driver — to be selected

Additional hardware will be introduced as required by the project.

Software

Firmware
C/C++
Arduino framework
PlatformIO
Visual Studio Code

Data processing and visualization
Python
Serial communication
Data visualization and mapping tools

Development
Git
GitHub
Markdown documentation


Interoperability

Interoperability is explored primarily through defined interfaces and communication protocols.

The project aims to prevent higher-level software from being tightly coupled to individual hardware implementations.

For example, the mapping system should consume a generic distance measurement interface rather than depending directly on the HC-SR04 implementation.

This makes it possible to replace or extend hardware with minimal changes to higher-level software.

Cybersecurity

The rover will eventually include communication security mechanisms appropriate to its architecture.

Potential threats include:

Unauthorized control commands.
Modified sensor data.
Replayed commands.
Unauthorized devices communicating with the rover.
Eavesdropping on external communications.

Repository Structure
AutonomousRover/
│
├── platformio.ini
│
├── src/
│   └── main.cpp
│
├── include/
│
├── lib/
│
├── test/
│
├── python/
│   ├── radar_visualizer/
│   ├── mapping/
│   └── tools/
│
├── docs/
│   ├── architecture.md
│   ├── hardware.md
│   ├── interoperability.md
│   ├── cybersecurity.md
│   └── slam.md
│
├── media/
│   ├── photos/
│   └── demonstrations/
│
├── README.md
├── ROADMAP.md
├── CHANGELOG.md
└── LICENSE


Main directories
Directory	Purpose
src/	    Main rover firmware
include/	Project-wide header files
lib/	    Reusable firmware modules
test/	    Automated and subsystem tests
python/	    Visualization, mapping, and development tools
docs/	    Detailed technical documentation
media/	    Project photographs and demonstrations

PlatformIO manages the firmware project structure, while Python tools and documentation remain separate from the embedded firmware.

Documentation

Detailed documentation will be added as the project develops.

Document	        Description
architecture.md	    System architecture and subsystem relationships
hardware.md	        Hardware, wiring, pin assignments, and electrical considerations
interoperability.md	Interfaces and communication standards
cybersecurity.md	Threat model and security architecture
slam.md	            Mapping, localization, and SLAM implementation

Additional subsystem documentation may be added when the project becomes sufficiently complex to warrant it.