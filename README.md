# G-BungE Log Analysis

Python-based vehicle log parsing and analysis workflow for the GIST Baja / Formula EV team G-BungE.

For Korean documentation, see [README_KOR.md](README_KOR.md).

## Project Overview

This repository contains a Python analysis tool for real Baja EV Mk.4 driving logs from G-BungE, the student-built electric vehicle team at GIST. It parses binary vehicle log files and turns sparse CAN, GPS, motor-control, torque, power, and thermal data into practical plots for vehicle debugging and performance review.

The project keeps the original MATLAB reference scripts under `MatLab/`, but the daily workflow is centered on `main.py`: a CLI and interactive menu that lets the user choose log groups, split-session files, and analysis actions without editing source code for every run.

A web-based beta version is also included. It lets users select logs and
analysis actions in a browser while running the same Python analysis code behind
the scenes.

The log parser currently focuses on 2025 Mk.4 vehicle data, including:

- binary vehicle log records
- CAN motor-controller data
- GPS position, velocity, and course
- torque demand and actual torque
- Id/Iq vector-control current data
- RPM, voltage, current, and power-related signals
- motor temperature and cooling trend data

## Problem & Motivation

During Mk.4 testing and competition, the team needed to inspect behavior in low-speed, high-load driving where motor and inverter thermal stress, torque drop, and power limiting could affect drivability. The raw logs were useful, but repeated analysis was slow when each graph required manual script edits or MATLAB-style one-off execution.

This project moves that workflow toward a repeatable Python CLI:

- choose a log group such as test week or competition
- load one file or multiple split-session logs in order
- run the same analysis actions consistently across sessions
- keep analysis assumptions configurable from call sites
- filter missing or sparse signals before interpolation, regression, or trend fitting

The goal is not only to plot data, but to make real vehicle log review faster, more reproducible, and easier for future team members to extend.

## Key Features

- Binary log parsing into a shared `VehicleLog` container
- Split-session log loading for sessions saved across multiple `.log` files
- CLI commands and an interactive numbered menu
- GPS trajectory, velocity, slip-ratio, lap, and g-force analysis
- Torque demand, actual torque, RPM, and T-N envelope analysis
- Id/Iq, vector-control, field-weakening, and motor-control constraint plots
- Power, moving RMS, battery current, and current-efficiency analysis
- Motor temperature, thermal lag, temperature slope, and cooling regression analysis
- Defensive `NaN` / infinite-value filtering for sparse logs before fitting or interpolation
- Configurable analysis parameters such as bin width, current limit, window length, and minimum sample count
- MATLAB reference files preserved for comparison with the earlier workflow

## Example Results

Plot images are not yet committed. The current analysis actions are intended to produce results such as:

- **Torque / RPM analysis**: identifies torque drop, plateau regions, and mismatch between demand torque and actual torque.
- **Power vs RPM**: checks whether high-RPM power behavior matches expectations or shows limiting.
- **Id/Iq vs RPM**: inspects vector-control operation and field-weakening behavior at higher motor speeds.
- **Motor temperature profile**: shows thermal accumulation during low-speed, high-load driving.
- **Cooling trend regression**: estimates cooling behavior from valid low-load samples after filtering sparse values.
- **GPS trajectory and g-force map**: visualizes the driving path, approximate acceleration behavior, and possible lap segments.

Future documentation should add example plot images under `docs/images/` or a similar folder.

## My Contribution

- Refactored the workflow from manual MATLAB-style analysis toward a Python CLI and interactive menu.
- Organized log group selection and split-session loading so related log files can be analyzed as one driving session.
- Added or organized motor control, power, torque, thermal, cooling, GPS, and vehicle dynamics analysis actions.
- Added defensive handling for `NaN`, infinite, and sparse signals before interpolation, binning, or regression.
- Documented the CAN data mapping and practical assumptions used when interpreting vehicle logs.
- Preserved MATLAB reference material while making the Python path the main repeatable workflow.

## Repository Structure

```text
.
├── main.py                  # CLI entry point and interactive menu
├── logFetcher.py            # Binary log parser and VehicleLog container
├── logPostProcessor.py      # Plotting and analysis functions
├── requirements.txt         # Python dependencies
├── Logs/
│   ├── 2nd Test Week/       # Test-week driving logs
│   └── Main Competition/    # Competition driving logs
├── MatLab/                  # Original MATLAB reference workflow
│   └── Results/             # MATLAB reference outputs
├── docs/
│   ├── analysis_notes.md    # Purpose of each analysis category
│   └── future_work.md       # Improvement roadmap
├── web/
│   ├── index.html           # Static GitHub Pages landing page
│   └── server.py            # Local browser UI for running the Python CLI
└── README_KOR.md            # Korean documentation
```

## How to Run

### 1. Install dependencies

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

### 2. Start the interactive menu

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

1. Choose a log group.
2. Choose one or more log files.
3. Choose one or more plots/actions.

Selections accept:

- single values such as `1`
- comma-separated values such as `1,4,7`
- ranges such as `3-6`
- `all`

## Web Runner

The web runner is currently a beta interface for the existing CLI workflow.

To run the Python analysis workflow from a browser form, start the local web
server:

```bash
python3 web/server.py
```

Then open:

```text
http://127.0.0.1:8765
```

The web runner reuses `main.py`, `logFetcher.py`, and `logPostProcessor.py`. It
saves Matplotlib outputs as PNG files under `web_runs/` and displays them in the
browser. Generated plot output and Matplotlib cache files are ignored by Git.

`web/index.html` is a static landing page for GitHub Pages-style hosting. Static
hosting cannot execute the Python analysis code, so real log analysis still
requires the local Python server above.

## CLI Usage

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

Run split-session logs in chronological order:

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

Absolute log paths can also be passed directly. When a driving session was split into multiple files, pass the files to `--log` in chronological order.

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

See [docs/analysis_notes.md](docs/analysis_notes.md) for a short explanation of what each category is used for.

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

- Logs are resolved from `Logs/<group>/` unless an absolute path is passed.
- Split-session logs should be passed in chronological order.
- `NaN` usually means the signal was unavailable, not parsed, or not received at that timestamp. Treat it as missing coverage, not a physical value.
- Temperature and cooling analyses include defensive `NaN` / infinite-value filtering before interpolation or regression.
- Cooling and thermal regressions are skipped when there are not enough valid samples.
- Some units and scaling assumptions come from the current Mk.4 logger format and should be checked when the logger firmware changes.

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

## Notes for Future Work

- Add example plot images to make the analysis output visible from the README.
- Separate parser, analysis, and visualization modules more clearly.
- Add tests for binary parsing and CAN field mapping.
- Add a sample anonymized log file or synthetic log generator.
- Export analysis summaries to CSV or Markdown for easier report writing.

More details are tracked in [docs/future_work.md](docs/future_work.md).
