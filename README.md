# G-BungE Log Analysis

Python-based log parsing and analysis workflow for the GIST Baja / Formula EV team.

This repository is based on `GBungE_logger_python` and keeps the original MATLAB reference files, but the day-to-day workflow is centered on Python. The main difference from the older code path is that you do not need to uncomment functions by hand every time you want a graph. You can select logs and analyses from a CLI or an interactive menu.

## What This Repo Does

- Parses binary vehicle log files into a shared `VehicleLog` container
- Runs GPS, torque, motor-control, power, thermal, and cooling analyses
- Supports both interactive selection and repeatable CLI commands
- Loads split-session logs in order so one driving session can be analyzed as a single run
- Keeps the original MATLAB scripts as reference material under `MatLab/`

## Repository Layout

```text
.
├── main.py                # CLI entry point and interactive menu
├── logFetcher.py          # Binary log parser and VehicleLog container
├── logPostProcessor.py    # Plotting and analysis functions
├── Logs/
│   ├── 2nd Test Week/
│   └── Main Competition/
└── MatLab/
    └── Results/           # MATLAB reference outputs
```

## Install

macOS / Linux:

```bash
python3 -m pip install -r requirements.txt
```

Windows:

```powershell
py -m pip install -r requirements.txt
```

If `py` is not available:

```powershell
python -m pip install -r requirements.txt
```

## Log Organization

By default, project-relative logs live under:

```text
Logs/<group name>/<timestamp>.log
```

Examples:

```text
Logs/2nd Test Week/2025-08-17 05-31-36.log
Logs/Main Competition/2025-08-30 08-32-10.log
```

You can also pass absolute log paths directly.

## Quick Start

Interactive menu:

```bash
python3 main.py
```

or, if executable permission is set:

```bash
./main.py
```

Windows:

```powershell
py main.py
```

The interactive flow is:

1. Choose a log group
2. Choose one or more log files
3. Choose one or more plots/actions

Selections accept:

- single values such as `1`
- comma-separated values such as `1,4,7`
- ranges such as `3-6`
- `all`

## Common CLI Usage

Show help:

```bash
python3 main.py --help
```

List available log groups and files:

```bash
python3 main.py --list-logs
```

List available plot/action names:

```bash
python3 main.py --list-plots
```

Run one plot on one log:

```bash
python3 main.py \
  --group "2nd Test Week" \
  --log "2025-08-17 05-31-36.log" \
  --plot gps-only
```

Run multiple analyses on the same session:

```bash
python3 main.py \
  --group "2nd Test Week" \
  --log "2025-08-17 05-31-36.log" \
  --plot torque-performance \
  --plot vector-control \
  --plot power-and-temp
```

Run split-session logs in order:

```bash
python3 main.py \
  --group "2nd Test Week" \
  --log "2025-08-17 05-31-36.log" "2025-08-17 05-44-54.log" \
  --plot torque-performance \
  --plot vector-control
```

Fail immediately when a selected log is missing:

```bash
python3 main.py \
  --group "Main Competition" \
  --log "2025-08-30 08-32-10.log" \
  --plot temperature-profile \
  --strict
```

## Analysis Categories

The interactive menu groups actions by purpose so the long list stays readable.

### Core / GPS

- `gps-only`
- `gps-velocity-and-slip`
- `gps-gforce-map`
- `split-laps`
- `laps-slideshow`

### Torque / Motor Control

- `torque-performance`
- `vector-control`
- `field-weakening`
- `advanced-id-iq-analysis`
- `id-iq-vs-rpm`
- `auto-field-weakening-trend`
- `torque-vs-iq`
- `motor-control-constraints`
- `torque-vs-temperature`
- `tn-curve-envelope`

### Power / Efficiency

- `power-and-temp`
- `moving-rms`
- `power-vs-rpm`
- `power-flow`
- `current-efficiency`

### Thermal / Cooling

- `temperature-profile`
- `power-vs-temp-slope`
- `cooling-trend-regression`
- `thermal-lag`
- `cooling-trend-high-temp`

### Vehicle Dynamics

- `vehicle-dynamics-mv-avg`

## CAN Data Mapping

The current parser is focused on 2025 Mk.4 vehicle logs.

| Source | Key | Data |
| --- | --- | --- |
| 1 | 0x0A | Actual torque, actual current, velocity |
| 1 | 0x0B | Ud, Uq, Vmod, Vcap |
| 1 | 0x0C | L, Vlim, Iflux, Iqmax |
| 1 | 0x0D | Motor temperature, battery current, torque demand, actual torque |
| 1 | 0x0E | Vtgt, Id, Iq |
| 5 | - | Accelerometer |
| 6 | 0 | GPS position |
| 6 | 1 | GPS velocity and course |
| 6 | 2 | GPS time |

## Practical Notes

- Logs are resolved from `Logs/<group>/` unless you pass an absolute path.
- When a single driving session was split into multiple `.log` files, pass them to `--log` in chronological order.
- Temperature and cooling analyses in the Python path include defensive `NaN` / infinite-value filtering before interpolation or regression. This avoids the common issue where preallocated empty samples pollute thermal trend fitting.
- Cooling and thermal regressions are skipped when there are not enough valid samples.
- `NaN` usually means the signal was unavailable, not parsed, or not received at that timestamp. Treat it as missing coverage, not a physical value.

## Tuning Analysis Parameters

Some plots in `logPostProcessor.py` intentionally include configurable assumptions such as:

- current limits
- RPM bin widths
- minimum samples per bin
- field-weakening thresholds
- thermal window lengths

Treat those values as analysis configuration, not fixed vehicle truth.

If one graph needs different thresholds for a specific run, prefer adjusting the call site in `main.py` rather than rewriting the plotting function itself. That keeps the visualizer reusable across different sessions.

Example:

```python
visualizer.plot_id_iq_vs_rpm(
    rpm_bin_width=100.0,
    min_samples_per_bin=10,
    current_limit=None,
)

visualizer.plot_auto_field_weakening_trend(
    fw_current_limit=None,
    rpm_bin_width=100.0,
    min_samples_per_bin=10,
)

visualizer.plot_torque_vs_iq(
    iq_bin_width=10.0,
    min_samples_per_bin=8,
    use_abs_iq=False,
    min_abs_iq=5.0,
)
```

For sparse logs, wider bins or lower minimum sample counts usually work better.

## Dependencies

`requirements.txt` currently installs:

- `matplotlib`
- `numpy`
- `scikit-learn`
- `scipy`
