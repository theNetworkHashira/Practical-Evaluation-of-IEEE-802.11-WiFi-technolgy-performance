import pandas as pd
import numpy as np

# ==========================================
# CONFIGURATION & TWEAKABLE VARIABLES
# ==========================================

INPUT_FILE = "S0_R00_01(outside)-(Xiaomi).csv"
OUTPUT_FILE = "packet_matrix_output.csv"

TARGET_MAX_TIME = 5.0
WINDOW_SIZE = 0.1

TARGET_FREQUENCY = None

# ==========================================
# DATA PROCESSING
# ==========================================

print(f"Loading data from {INPUT_FILE}...")
df = pd.read_csv(INPUT_FILE)

# [MODIFIED] Force 'Time' to numeric and rebase to start at 0 so that
# TARGET_MAX_TIME means "first N seconds of the capture", not absolute clock time.
# This prevents an empty df_filtered (the root cause of the crash).
df['Time'] = pd.to_numeric(df['Time'], errors='coerce')
df = df.dropna(subset=['Time', 'Type/Subtype']).copy()
df['Time'] = df['Time'] - df['Time'].min()

# [MODIFIED] Combined the dropna for both columns above; kept the frequency filter intact.
if TARGET_FREQUENCY is not None:
    if 'Frequency' in df.columns:
        df = df[df['Frequency'] == TARGET_FREQUENCY].copy()
        print(f"Filtered data to {TARGET_FREQUENCY}GHz frequency.")
    else:
        print("Warning: 'Frequency' column not found in dataset.")


def classify_type(subtype):
    subtype_lower = str(subtype).lower()

    if any(kw in subtype_lower for kw in ['beacon', 'probe', 'authentication', 'association']):
        return 'Management'
    elif any(kw in subtype_lower for kw in ['ack', 'rts', 'cts', 'block ack']):
        return 'Control'
    elif any(kw in subtype_lower for kw in ['data', 'null function', 'qos']):
        return 'Data'

    return 'Other'


df['Main Type'] = df['Type/Subtype'].apply(classify_type)

df_filtered = df[df['Time'] <= TARGET_MAX_TIME].copy()

# [ADDED] Guard against an empty filtered frame — an empty pivot is what
# produced the InvalidIndexError(slice(None, None, None)) downstream.
if df_filtered.empty:
    raise SystemExit(
        f"No packets found within the first {TARGET_MAX_TIME}s of the capture. "
        f"Check TARGET_MAX_TIME, WINDOW_SIZE, and that 'Time' parsed correctly."
    )

# [MODIFIED] Added include_lowest=True so a packet at exactly t=0 falls into the first bin.
bins = np.arange(0, TARGET_MAX_TIME + WINDOW_SIZE, WINDOW_SIZE)
labels = [f"{round(b, 1)}s" for b in bins[1:]]
df_filtered['Time Window'] = pd.cut(
    df_filtered['Time'], bins=bins, labels=labels,
    right=False, include_lowest=True,
)

print("Generating matrix...")

# [MODIFIED] Added observed=True to silence the FutureWarning AND to avoid the
# empty-categorical pivot that broke the merge. Added .reset_index() so that
# 'Main Type' and 'Type/Subtype' become real columns (the merge below needs
# them as columns, not as the pivot's index — this was the structural bug
# that surfaced as InvalidIndexError).
matrix = (
    pd.pivot_table(
        df_filtered,
        index=['Main Type', 'Type/Subtype'],
        columns='Time Window',
        aggfunc='size',
        fill_value=0,
        observed=True,
    )
    .reset_index()
)

all_subtypes = df[['Main Type', 'Type/Subtype']].drop_duplicates()

matrix_full = pd.merge(
    all_subtypes, matrix, on=['Main Type', 'Type/Subtype'], how='left'
).fillna(0)

# [MODIFIED] Replaced the fragile `if 's' in col` check (which also matched
# 'Type/Subtype') with an explicit match against the known bin labels.
count_cols = [c for c in matrix_full.columns if c in labels]
matrix_full[count_cols] = matrix_full[count_cols].astype(int)

matrix_full['Type_Cat'] = pd.Categorical(
    matrix_full['Main Type'],
    categories=['Management', 'Control', 'Data', 'Other'],
    ordered=True
)
matrix_full = matrix_full.sort_values(['Type_Cat', 'Type/Subtype']).drop('Type_Cat', axis=1)

matrix_full.to_csv(OUTPUT_FILE, index=False)
print(f"Success! Matrix saved to {OUTPUT_FILE}")