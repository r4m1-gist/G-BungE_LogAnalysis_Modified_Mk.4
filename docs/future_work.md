# Future Work

This roadmap keeps the project focused on practical vehicle log analysis while making it easier to understand as a portfolio project and maintain as a team tool.

## Documentation

- Add example plot images for torque/RPM, power/RPM, Id/Iq/RPM, temperature profile, cooling regression, and GPS trajectory.
- Add a short walkthrough that starts from one known log file and ends with a few interpreted plots.
- Document logger firmware assumptions and update the CAN mapping whenever the vehicle-side format changes.

## Code Structure

- Separate binary parsing, analysis calculations, and visualization into clearer modules.
- Keep `main.py` focused on CLI/menu orchestration.
- Move reusable analysis defaults into a small configuration layer.

## Reliability

- Add tests for fixed-width binary record counting.
- Add parser tests for each supported CAN source/key mapping.
- Add tests for sparse logs where key signals contain `NaN` or infinite values.

## Sample Data

- Add a small anonymized log file if team policy allows it.
- If real logs cannot be shared, add a synthetic log generator that produces GPS, torque, Id/Iq, power, and thermal signals with known behavior.

## Reporting

- Export selected analysis summaries to CSV.
- Export run-level summaries to Markdown for design reviews and competition reports.
- Save plot images automatically when requested from the CLI.
