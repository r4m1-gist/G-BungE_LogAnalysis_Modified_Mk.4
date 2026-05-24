# Analysis Notes

This document summarizes why each analysis category exists and what it is normally used to check in G-BungE Baja EV Mk.4 logs.

## Core / GPS

GPS plots help confirm where the vehicle drove, whether the recorded path is usable, and whether the run can be split into meaningful laps or segments. Velocity, course, and approximate g-force views are useful for matching vehicle behavior against track sections.

## Torque / Motor Control

Torque and motor-control plots are used to compare the driver's or controller's torque demand against actual torque, motor speed, and Id/Iq behavior. They are especially useful for finding torque plateau regions, high-RPM field weakening, current limits, or voltage-limit behavior.

## Power / Efficiency

Power and current plots help estimate how hard the drivetrain was being loaded during a run. They can reveal high-RPM power behavior, battery-current demand, moving RMS load, and rough current-efficiency trends.

## Thermal / Cooling

Thermal plots are used to inspect motor temperature accumulation during low-speed high-load driving and to estimate cooling behavior during low-load sections. Because thermal signals can be sparse, these analyses should filter invalid values before interpolation, slope estimation, or regression.

## Vehicle Dynamics

Vehicle dynamics plots provide a quick view of acceleration behavior using available accelerometer or GPS-derived signals. They are useful as a lightweight sanity check when reviewing acceleration, braking, and cornering sections.

## Data Quality Notes

- `NaN` means the signal was missing, unavailable, not parsed, or not received at that timestamp.
- A missing value should not be interpreted as zero torque, zero current, zero speed, or zero temperature.
- Split-session logs should be loaded in chronological order.
- Regression or bin-based plots need enough valid samples to produce meaningful results.
