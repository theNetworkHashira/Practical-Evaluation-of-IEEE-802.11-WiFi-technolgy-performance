# Wi-Fi capture analysis tools

This project contains two independent workflows:

- `matrix_maker-2.py` prepares a time-window matrix from one Wi-Fi capture.
- `plot3d_matrix-3.py` reads a compatible long-format CSV and creates an interactive 3D Plotly visualization.
- `wifi_mode_analysis_advanced.py` is a separate standalone program for comparing SoftAP and AP captures. It does not use the matrix-maker output or the 3D plot script.

## Requirements

Install Python 3 and the required packages:

```bash
pip install pandas numpy plotly kaleido
```

`kaleido` is required by the advanced analysis script to export charts as PNG files.

## Matrix and 3D plot workflow

### 1. Create the packet matrix

Place the input capture CSV in the same directory as `matrix_maker-2.py`, or edit the configuration variables near the top of the script:

```python
INPUT_FILE = "S0_R00_01(outside)-(Xiaomi).csv"
OUTPUT_FILE = "packet_matrix_output.csv"
TARGET_MAX_TIME = 5.0
WINDOW_SIZE = 0.1
TARGET_FREQUENCY = None
```

Run:

```bash
python matrix_maker-2.py
```

The script reads the capture, converts `Time` to numeric values, rebases time to zero, classifies frame subtypes as Management, Control, Data, or Other, and counts packets in fixed time windows. It writes the result to `packet_matrix_output.csv`.

The generated matrix contains `Main Type`, `Type/Subtype`, and one column for each time window. The matrix-maker script therefore produces a wide matrix intended for matrix-style analysis.

### 2. Create the 3D visualization

Important: the current `plot3d_matrix-3.py` expects a long-format CSV with these columns:

- `TimeBin`, such as `0.0-0.1`.
- `Type/Subtype`.
- `Count`.
- `Percentage`.
- `Hex`, containing a color value such as `#1f77b4`.

Run it by passing the compatible CSV as a command-line argument:

```bash
python plot3d_matrix-3.py input_long_format.csv
```

The script converts the beginning of `TimeBin` into a numeric time coordinate, then plots:

- X axis: time-bin start in seconds.
- Y axis: Wi-Fi frame subtype.
- Z axis: packet count.
- Marker size: packet count.
- Marker color: the value in `Hex`.

It saves an interactive HTML file next to the input CSV, using the name `<input-name>_3d_scatter.html`, and also attempts to open the figure in the default Plotly display environment.

### Relationship between the two scripts

Conceptually, `matrix_maker-2.py` creates the time-window packet-count data that can be visualized in 3D. However, the two current scripts do not use exactly the same CSV schema:

- `matrix_maker-2.py` writes a wide matrix with columns such as `0.0s`, `0.1s`, and `0.2s`.
- `plot3d_matrix-3.py` expects long-format rows with `TimeBin`, `Count`, `Percentage`, and `Hex`.

Therefore, the output of `matrix_maker-2.py` cannot be passed directly to `plot3d_matrix-3.py` without a conversion step or changes to one of the scripts. The intended pipeline is:

```text
Wi-Fi capture CSV -> matrix_maker-2.py -> time-window packet counts -> long-format conversion -> plot3d_matrix-3.py -> interactive HTML plot
```

If the plotting script is updated to read the matrix format directly, it should reshape the time-window columns from wide format to long format before plotting.

## Standalone SoftAP/AP analysis

`wifi_mode_analysis_advanced.py` compares two captures: one made in SoftAP mode and one made in normal AP/infrastructure mode.

The input CSV files must contain at least these columns:

```text
Type/Subtype, Source, Length, Time
```

Run the analysis as follows:

```bash
python wifi_mode_analysis_advanced.py \
  --softap "softAP_capture1.csv" \
  --ap "AP_capture1.csv" \
  --outdir "output/softap_vs_ap"
```

Arguments:

- `--softap`: path to the SoftAP capture CSV.
- `--ap`: path to the AP capture CSV.
- `--outdir`: directory where tables, PNG charts, and metadata files are saved. It defaults to `output`.

The script validates and normalizes both captures, classifies frame subtypes, and produces CSV summaries and charts. Outputs include frame-class counts, selected subtype counts, control-to-data ratios, per-source class counts, pseudo-airtime estimates, RTS/CTS/DATA/ACK sequence counts, cumulative timelines, and subtype event timelines.

The pseudo-airtime result is only a relative byte-volume proxy based on frame length. The simple RTS/CTS/DATA/ACK detector looks for adjacent rows after sorting by time; it does not prove that the frames belong to the same exchange without further address, sequence-number, and timing checks.

## Troubleshooting

- If the matrix script reports that no packets were found, check the `Time` column, `TARGET_MAX_TIME`, and the input filename.
- If a frequency filter is enabled, confirm that the input contains a `Frequency` column and that its values match `TARGET_FREQUENCY`.
- If the 3D plot script reports missing columns, provide a long-format CSV containing `TimeBin`, `Type/Subtype`, `Count`, `Percentage`, and `Hex`.
- If the standalone analyzer reports missing columns, add or rename the required fields: `Type/Subtype`, `Source`, `Length`, and `Time`.
- If PNG export fails, install or update `kaleido` and verify that Plotly is installed correctly.
