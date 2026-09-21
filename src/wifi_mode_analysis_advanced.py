"""
Advanced Wi-Fi frame analysis: compare SoftAP vs AP captures.

Features:
    - Classification into Management / Control / Data / Other.
    - Comparative metrics between SoftAP and AP captures.
    - Per-MAC breakdowns.
    - Simple RTS/CTS/Data/ACK sequence mining.
    - Pseudo-airtime analysis based on frame length.
    - Subtype-specific event timelines.
    - One-second timeline grid lines.
    - Rectangular publication-style PNG output.
    - Safe Windows output-path handling.

Usage:
    python wifi_mode_analysis_advanced_final_rectangular.py \
        --softap "softAP_capture1.csv" \
        --ap "AP_capture1.csv" \
        --outdir "output2/S0_R00_01(outside) soft VS infra"

Dependencies:
    pip install pandas plotly kaleido

Expected CSV columns:
    Type/Subtype, Source, Length, Time

Notes:
    - Pseudo-airtime is a relative byte-volume proxy, not actual PHY airtime.
    - The timeline visualizes event timing; it does not prove frame-exchange
      relationships without address, sequence-number, and timing validation.
"""

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# ----------------------------------------------------------------------
# Safe filesystem handling
# ----------------------------------------------------------------------

WINDOWS_INVALID_CHARS = r'[<>:"/\\|?*\x00-\x1f]'
WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def sanitize_path_component(value: str) -> str:
    """Make one directory or filename component safe on Windows."""
    value = re.sub(WINDOWS_INVALID_CHARS, "_", str(value))
    value = value.rstrip(" .")

    if not value:
        value = "output"

    if value.upper() in WINDOWS_RESERVED_NAMES:
        value = f"_{value}_"

    return value


def safe_output_directory(outdir: str) -> Path:
    """Create the requested output directory safely."""
    raw_path = Path(outdir).expanduser()

    if raw_path.is_absolute():
        safe_parts = [sanitize_path_component(part) for part in raw_path.parts]
        safe_path = Path(raw_path.anchor, *safe_parts[1:])
    else:
        safe_path = Path(
            *[sanitize_path_component(part) for part in raw_path.parts]
        )

    safe_path.mkdir(parents=True, exist_ok=True)
    return safe_path


def output_file(outdir: Path, filename: str) -> Path:
    """Return a safe output path inside the selected directory."""
    return outdir / sanitize_path_component(filename)


# ----------------------------------------------------------------------
# Classification logic
# ----------------------------------------------------------------------


def classify_frame(type_subtype: str) -> str:
    """Map Wireshark Type/Subtype text to a high-level frame class."""
    text = str(type_subtype).lower()

    if (
        "beacon" in text
        or "probe" in text
        or "association" in text
        or "reassociation" in text
        or "disassociation" in text
        or "authentication" in text
        or "deauthentication" in text
        or "action" in text
    ):
        return "Management"

    if (
        "clear-to-send" in text
        or "request-to-send" in text
        or "acknowledgement" in text
        or "block ack" in text
        or "cf-end" in text
        or "control-frame" in text
    ):
        return "Control"

    if "data" in text or "qos" in text or "null function" in text:
        return "Data"

    return "Other"


def normalize_capture(df: pd.DataFrame, mode_label: str) -> pd.DataFrame:
    """Validate and normalize an input capture."""
    required = {"Type/Subtype", "Source", "Length", "Time"}
    missing = required.difference(df.columns)

    if missing:
        raise ValueError(
            "Missing required CSV columns: "
            + ", ".join(sorted(missing))
        )

    result = df.copy()
    result["Type/Subtype"] = result["Type/Subtype"].astype(str).str.strip()
    result["Source"] = result["Source"].astype(str).str.strip()
    result["Length"] = pd.to_numeric(
        result["Length"], errors="coerce"
    ).fillna(0)
    result["Time"] = pd.to_numeric(result["Time"], errors="coerce")
    result["Class"] = result["Type/Subtype"].apply(classify_frame)
    result["Mode"] = mode_label
    return result


# ----------------------------------------------------------------------
# Metrics
# ----------------------------------------------------------------------


def compute_class_counts(softap: pd.DataFrame, ap: pd.DataFrame) -> pd.DataFrame:
    combined = pd.concat([softap, ap], ignore_index=True)
    return combined.groupby(["Mode", "Class"]).size().reset_index(name="Count")


def compute_key_subtype_counts(
    softap: pd.DataFrame,
    ap: pd.DataFrame,
) -> pd.DataFrame:
    key_types = [
        "Clear-to-send",
        "Request-to-send",
        "CF-End (Control-frame)",
        "Beacon frame",
        "Probe Request",
        "Probe Response",
        "Action",
        "QoS Data",
        "QoS Null function (No data)",
        "802.11 Block Ack Req",
        "802.11 Block Ack",
    ]

    soft_subset = softap[softap["Type/Subtype"].isin(key_types)].copy()
    ap_subset = ap[ap["Type/Subtype"].isin(key_types)].copy()

    soft_subset["Mode"] = "SoftAP"
    ap_subset["Mode"] = "AP"

    combined = pd.concat([soft_subset, ap_subset], ignore_index=True)
    return (
        combined.groupby(["Mode", "Type/Subtype"])
        .size()
        .reset_index(name="Count")
    )


def compute_control_to_data_ratio(class_counts: pd.DataFrame) -> pd.DataFrame:
    ratio_df = class_counts.pivot(
        index="Mode",
        columns="Class",
        values="Count",
    ).fillna(0)

    data_counts = ratio_df.get(
        "Data",
        pd.Series(1, index=ratio_df.index, dtype=float),
    ).replace(0, 1)

    ratio_df["Control_to_Data"] = ratio_df.get("Control", 0) / data_counts
    return ratio_df.reset_index()[["Mode", "Control_to_Data"]]


def compute_per_mac_class_counts(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["Mode", "Source", "Class"])
        .size()
        .reset_index(name="Count")
    )


def compute_pseudo_airtime_by_class(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["Mode", "Class"])["Length"]
        .sum()
        .reset_index(name="PseudoAirtime")
    )


def detect_rts_cts_data_ack_sequences(
    df: pd.DataFrame,
    mode_label: str,
) -> Dict[str, int]:
    """Detect adjacent RTS-CTS-DATA-ACK subtype patterns."""
    temporary = df.dropna(subset=["Time"]).sort_values("Time")
    types = temporary["Type/Subtype"].tolist()

    data_candidates = {"Data", "QoS Data"}
    ack_candidates = {"Acknowledgement", "802.11 Block Ack"}
    sequence_count = 0

    for index in range(len(types) - 3):
        t0, t1, t2, t3 = types[index:index + 4]
        if (
            t0 == "Request-to-send"
            and t1 == "Clear-to-send"
            and t2 in data_candidates
            and t3 in ack_candidates
        ):
            sequence_count += 1

    return {
        "Mode": mode_label,
        "RTS_CTS_DATA_ACK_sequences": sequence_count,
    }


# ----------------------------------------------------------------------
# General plot utilities
# ----------------------------------------------------------------------


def save_fig_with_meta(
    fig,
    out_png: Path,
    caption: str,
    description: str,
) -> None:
    """Apply rectangular dimensions and save a PNG plus metadata."""
    out_png.parent.mkdir(parents=True, exist_ok=True)

    # These dimensions apply to all ordinary output charts.
    fig.update_layout(
        width=1800,
        height=850,
        font=dict(size=14),
        title_font_size=18,
        margin=dict(
            l=100,
            r=50,
            t=100,
            b=100,
        ),
    )

    fig.write_image(str(out_png))

    metadata_path = Path(str(out_png) + ".meta.json")
    with metadata_path.open("w", encoding="utf-8") as file:
        json.dump(
            {
                "caption": caption,
                "description": description,
            },
            file,
            indent=2,
        )


def plot_frame_class_mix(class_counts: pd.DataFrame, outdir: Path) -> None:
    fig = px.bar(
        class_counts,
        x="Class",
        y="Count",
        color="Mode",
        barmode="group",
        title="Frame class mix (SoftAP vs AP)",
    )
    fig.update_xaxes(title_text="Class")
    fig.update_yaxes(title_text="Frames")
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5,
        )
    )

    save_fig_with_meta(
        fig,
        output_file(outdir, "frame_class_mix.png"),
        "Distribution of frame classes by mode",
        "Grouped bar chart comparing frame classes.",
    )


def plot_key_subtypes_by_mode(
    subtype_counts: pd.DataFrame,
    outdir: Path,
) -> None:
    fig = px.bar(
        subtype_counts,
        x="Type/Subtype",
        y="Count",
        color="Mode",
        barmode="group",
        title="Key 802.11 subtypes by mode",
    )
    fig.update_xaxes(title_text="Subtype", tickangle=45)
    fig.update_yaxes(title_text="Frames")
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.20,
            xanchor="center",
            x=0.5,
        )
    )

    save_fig_with_meta(
        fig,
        output_file(outdir, "key_subtypes_by_mode.png"),
        "Counts of selected 802.11 subtypes by mode",
        "Grouped bar chart comparing selected subtype counts.",
    )


def plot_control_to_data_ratio(
    ratio_df: pd.DataFrame,
    outdir: Path,
) -> None:
    fig = px.bar(
        ratio_df,
        x="Mode",
        y="Control_to_Data",
        title="Control-to-data frame ratio (SoftAP vs AP)",
    )
    fig.update_xaxes(title_text="Mode")
    fig.update_yaxes(title_text="Ctrl/Data")
    fig.update_layout(showlegend=False)

    save_fig_with_meta(
        fig,
        output_file(outdir, "control_to_data_ratio.png"),
        "Ratio of control to data frames by mode",
        "Bar chart showing control frames per data frame.",
    )


def plot_cumulative_time_series(
    df: pd.DataFrame,
    mode_label: str,
    outdir: Path,
) -> None:
    temporary = df.dropna(subset=["Time"]).sort_values("Time").copy()
    temporary["Time_bin"] = temporary["Time"].round(2)

    time_counts = (
        temporary.groupby(["Time_bin", "Class"])
        .size()
        .reset_index(name="Count")
    )
    time_counts["Cumulative"] = (
        time_counts.groupby("Class")["Count"].cumsum()
    )

    fig = px.line(
        time_counts,
        x="Time_bin",
        y="Cumulative",
        color="Class",
        title=f"Cumulative frames over time ({mode_label})",
    )
    fig.update_xaxes(title_text="Time (s)")
    fig.update_yaxes(title_text="Cumulative frames")
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5,
        )
    )

    save_fig_with_meta(
        fig,
        output_file(outdir, f"cumulative_{mode_label.lower()}.png"),
        f"Cumulative frame classes over time in {mode_label}",
        f"Cumulative frame-class chart for {mode_label}.",
    )


def plot_pseudo_airtime_by_class(
    airtime_df: pd.DataFrame,
    outdir: Path,
) -> None:
    fig = px.bar(
        airtime_df,
        x="Class",
        y="PseudoAirtime",
        color="Mode",
        barmode="group",
        title="Pseudo-airtime by frame class (SoftAP vs AP)",
    )
    fig.update_xaxes(title_text="Class")
    fig.update_yaxes(title_text="Pseudo-airtime (bytes)")
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5,
        )
    )

    save_fig_with_meta(
        fig,
        output_file(outdir, "pseudo_airtime_by_class.png"),
        "Pseudo-airtime per frame class and mode",
        "Summed frame length as a relative byte-volume proxy.",
    )


# ----------------------------------------------------------------------
# Subtype event timeline
# ----------------------------------------------------------------------


def normalize_subtype_label(value: object) -> str:
    if pd.isna(value):
        return "Unknown"

    value = str(value).strip()
    return value if value else "Unknown"


def prepare_timeline_data(df: pd.DataFrame) -> pd.DataFrame:
    timeline = df.copy()
    timeline["Time"] = pd.to_numeric(timeline["Time"], errors="coerce")
    timeline["Subtype"] = timeline["Type/Subtype"].apply(
        normalize_subtype_label
    )

    return (
        timeline.dropna(subset=["Time"])
        .sort_values("Time", kind="stable")
        .reset_index(drop=True)
    )


def stable_color_for_subtype(subtype: str) -> str:
    digest = hashlib.md5(subtype.encode("utf-8")).hexdigest()
    hue = int(digest[:8], 16) % 360
    return f"hsl({hue}, 70%, 45%)"


def build_subtype_style(subtypes) -> Dict[str, Dict[str, object]]:
    symbols = [
        "circle",
        "square",
        "diamond",
        "triangle-up",
        "triangle-down",
        "triangle-left",
        "triangle-right",
        "pentagon",
        "hexagon",
        "star",
        "hexagram",
        "bowtie",
        "hourglass",
        "cross",
        "x",
        "asterisk",
        "circle-open",
        "square-open",
        "diamond-open",
        "triangle-up-open",
        "triangle-down-open",
        "star-open",
    ]

    return {
        subtype: {
            "color": stable_color_for_subtype(subtype),
            "symbol": symbols[index % len(symbols)],
        }
        for index, subtype in enumerate(subtypes)
    }


def calculate_vertical_jitter(
    timeline: pd.DataFrame,
    subtype_order,
    jitter_fraction: float = 0.30,
) -> pd.DataFrame:
    row_index = {
        subtype: index
        for index, subtype in enumerate(subtype_order)
    }

    timeline = timeline.copy()
    timeline["SubtypeRow"] = timeline["Subtype"].map(row_index).astype(float)
    timeline["YPosition"] = timeline["SubtypeRow"]

    for subtype, group in timeline.groupby("Subtype", sort=False):
        number_of_points = len(group)

        if number_of_points == 1:
            offsets = [0.0]
        else:
            offsets = [
                ((position / (number_of_points - 1)) - 0.5)
                * 2
                * jitter_fraction
                for position in range(number_of_points)
            ]

        for index, offset in zip(group.index, offsets):
            timeline.loc[index, "YPosition"] += offset

    return timeline


def plot_frame_subtype_timeline(
    df: pd.DataFrame,
    mode_label: str,
    outdir: Path,
) -> None:
    timeline = prepare_timeline_data(df)

    if timeline.empty:
        print(
            f"Skipping timeline for {mode_label}: "
            "no valid timestamped frames."
        )
        return

    subtype_order = (
        timeline.groupby("Subtype")["Time"]
        .min()
        .sort_values()
        .index
        .tolist()
    )

    timeline = calculate_vertical_jitter(timeline, subtype_order)
    subtype_style = build_subtype_style(subtype_order)
    figure = go.Figure()

    for subtype in subtype_order:
        subset = timeline[timeline["Subtype"] == subtype]
        style = subtype_style[subtype]

        custom_columns = ["Subtype", "Class"]
        for column in ["Source", "Destination", "Length"]:
            if column in subset.columns:
                custom_columns.append(column)

        customdata = subset[custom_columns].to_numpy()
        index_map = {
            column: index
            for index, column in enumerate(custom_columns)
        }

        hover_lines = [
            "Time: %{x:.6f} s",
            f"Subtype: %{{customdata[{index_map['Subtype']}]}}",
            f"Class: %{{customdata[{index_map['Class']}]}}",
        ]

        if "Source" in index_map:
            hover_lines.append(
                f"Source: %{{customdata[{index_map['Source']}]}}"
            )
        if "Destination" in index_map:
            hover_lines.append(
                "Destination: "
                f"%{{customdata[{index_map['Destination']}]}}"
            )
        if "Length" in index_map:
            hover_lines.append(
                f"Length: %{{customdata[{index_map['Length']}]}} bytes"
            )

        figure.add_trace(
            go.Scatter(
                x=subset["Time"],
                y=subset["YPosition"],
                mode="markers",
                name=subtype,
                marker=dict(
                    color=style["color"],
                    symbol=style["symbol"],
                    size=10,
                    opacity=0.90,
                    line=dict(color="white", width=0.8),
                ),
                customdata=customdata,
                hovertemplate="<br>".join(hover_lines)
                + "<extra></extra>",
            )
        )

    time_min = float(timeline["Time"].min())
    time_max = float(timeline["Time"].max())
    time_span = max(time_max - time_min, 1.0)

    # Increase 0.12 for even more horizontal padding.
    padding = max(time_span * 0.12, 1.0)
    x_range = [
        max(0, time_min - padding),
        time_max + padding,
    ]

    figure.update_layout(
        # Wide rectangular dimensions for the subtype timeline.
        width=3000,
        height=max(750, 90 + 55 * len(subtype_order)),
        title=f"Wi-Fi Frame Subtype Event Timeline ({mode_label})",
        xaxis=dict(
            title="Time (seconds)",
            range=x_range,
            showgrid=True,
            tickmode="linear",
            tick0=0,
            dtick=1,
            tickformat=".0f",
            gridcolor="rgba(180, 180, 180, 0.45)",
            gridwidth=1,
            zeroline=False,
        ),
        yaxis=dict(
            title="Frame subtype",
            tickmode="array",
            tickvals=list(range(len(subtype_order))),
            ticktext=subtype_order,
            range=[-0.7, len(subtype_order) - 0.3],
            showgrid=True,
            zeroline=False,
        ),
        legend=dict(
            title="Frame subtype",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(size=11),
        ),
        font=dict(size=14),
        title_font_size=22,
        hovermode="closest",
        template="plotly_white",
        margin=dict(l=210, r=40, t=145, b=90),
    )

    save_fig_with_meta(
        figure,
        output_file(
            outdir,
            f"frame_subtype_timeline_{mode_label.lower()}.png",
        ),
        f"Subtype-specific Wi-Fi frame events in {mode_label}",
        (
            "Timeline of timestamped 802.11 frame subtype events. Each "
            "subtype has its own color and marker shape. Points receive "
            "small vertical offsets within their subtype row."
        ),
    )


# ----------------------------------------------------------------------
# Top-level driver
# ----------------------------------------------------------------------


def run_analysis(softap_path: str, ap_path: str, outdir: str) -> None:
    output_dir = safe_output_directory(outdir)

    softap_raw = pd.read_csv(softap_path)
    ap_raw = pd.read_csv(ap_path)

    softap = normalize_capture(softap_raw, "SoftAP")
    ap = normalize_capture(ap_raw, "AP")

    class_counts = compute_class_counts(softap, ap)
    subtype_counts = compute_key_subtype_counts(softap, ap)
    ratio_df = compute_control_to_data_ratio(class_counts)

    combined = pd.concat([softap, ap], ignore_index=True)
    per_mac_counts = compute_per_mac_class_counts(combined)
    airtime_df = compute_pseudo_airtime_by_class(combined)

    sequence_softap = detect_rts_cts_data_ack_sequences(softap, "SoftAP")
    sequence_ap = detect_rts_cts_data_ack_sequences(ap, "AP")

    class_counts.to_csv(
        output_file(output_dir, "frame_class_counts_by_mode.csv"),
        index=False,
    )
    subtype_counts.to_csv(
        output_file(output_dir, "key_subtype_counts_by_mode.csv"),
        index=False,
    )
    ratio_df.to_csv(
        output_file(output_dir, "control_to_data_ratio_by_mode.csv"),
        index=False,
    )
    per_mac_counts.to_csv(
        output_file(output_dir, "per_mac_class_counts.csv"),
        index=False,
    )
    airtime_df.to_csv(
        output_file(output_dir, "pseudo_airtime_by_class.csv"),
        index=False,
    )

    sequence_df = pd.DataFrame([sequence_softap, sequence_ap])
    sequence_df.to_csv(
        output_file(output_dir, "rts_cts_data_ack_sequences_by_mode.csv"),
        index=False,
    )

    plot_frame_class_mix(class_counts, output_dir)
    plot_key_subtypes_by_mode(subtype_counts, output_dir)
    plot_control_to_data_ratio(ratio_df, output_dir)
    plot_cumulative_time_series(softap, "SoftAP", output_dir)
    plot_cumulative_time_series(ap, "AP", output_dir)
    plot_pseudo_airtime_by_class(airtime_df, output_dir)
    plot_frame_subtype_timeline(softap, "SoftAP", output_dir)
    plot_frame_subtype_timeline(ap, "AP", output_dir)

    print(f"Output directory: {output_dir.resolve()}")
    print("Rows in SoftAP capture:", len(softap))
    print("Rows in AP capture:", len(ap))
    print("Frame class counts by mode:")
    print(class_counts)
    print("Control/Data ratios:")
    print(ratio_df)
    print("RTS-CTS-DATA-ACK sequences per mode:")
    print(sequence_df)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Advanced Wi-Fi frame analysis comparing SoftAP and AP "
            "captures, with rectangular charts and one-second timeline grids."
        )
    )
    parser.add_argument(
        "--softap",
        required=True,
        help="Path to SoftAP capture CSV.",
    )
    parser.add_argument(
        "--ap",
        required=True,
        help="Path to AP capture CSV.",
    )
    parser.add_argument(
        "--outdir",
        default="output",
        help="Output directory for tables and charts.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    run_analysis(arguments.softap, arguments.ap, arguments.outdir)








