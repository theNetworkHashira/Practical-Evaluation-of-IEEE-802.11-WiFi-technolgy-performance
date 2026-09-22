# Practical Evaluation of IEEE 802.11 WiFi technology performance

**Student:** Haruna Muhammad Idris  
**Supervisor:** Prof. Dr. Gal Zoltan  
**Institution:** University of Debrecen  
**Measurement location:** Faculty of Informatics building (IK)  
**Measurement period:** Summer

## Overview

This project analyses an expanded set of IEEE 802.11 Wi-Fi packet captures to compare a Xiaomi smartphone operating as a software access point (SoftAP) with infrastructure access point (AP) capture conditions.

The project combines:

- Passive monitor-mode Wi-Fi capture.
- Python-based CSV processing.
- IEEE 802.11 frame classification.
- Comparative statistical analysis.
- Source MAC address analysis.
- Frame subtype analysis.
- RTS–CTS–Data–ACK pattern screening.
- Frame-length volume analysis.
- Timeline visualization.

The analysis was designed to process similarly structured comma-separated values (CSV) files automatically and produce repeatable tables and visualizations.

## Measurement Context

The captures were collected at the Faculty of Informatics building (IK) during the summer. At the time of measurement, almost no students were present on campus, and only a few instructors generated background traffic.

This produced a relatively quiet wireless environment. The low-traffic condition made it easier to inspect frame-level behaviour and identify recurring frame patterns. However, it also limits the generalizability of the results. The observations should not be interpreted as representing normal high-density semester activity without additional measurements.

## Dataset

The expanded dataset contains 24 unique capture files:

| Mode | Files | Total captured frames | Mean frames/file | Median frames/file |
|---|---:|---:|---:|---:|
| Infrastructure AP | 12 | 17,680 | 1,473.3 | 1,136.0 |
| Xiaomi SoftAP | 12 | 8,060 | 671.7 | 599.5 |

The supplied naming rule was used for the initial grouping:

- Filenames containing `Xiaomi` were treated as SoftAP captures.
- Corresponding filenames without `Xiaomi` were treated as infrastructure AP captures.

This naming-based classification should ideally be confirmed using capture notes, target basic service set identifiers (BSSIDs), and experimental records.

### Xiaomi SoftAP capture files

- `S0_R00a_01-outside-Xiaomi.csv`
- `S0_R00b_01-inside-Xiaomi.csv`
- `S0_R01_01-Xiaomi.csv`
- `S0_R03_01-Xiaomi.csv`
- `S0_R08_01-Xiaomi.csv`
- `S1_R02_01-Xiaomi.csv`
- `S1_R06_01-Xiaomi.csv`
- `S1_R30_01-Xiaomi.csv`
- `S2_R01_01-Xiaomi.csv`
- `S2_R02_01-Xiaomi.csv`
- `S2_R06_01-Xiaomi.csv`
- `S2_R31_01-Xiaomi.csv`

### Infrastructure AP capture files

- `S0_R00_01-outside.csv`
- `S0_R00b_01-inside.csv`
- `S0_R01_01.csv`
- `S0_R03_01.csv`
- `S0_R08_01.csv`
- `S1_R02_01.csv`
- `S1_R06_01.csv`
- `S1_R30_01.csv`
- `S2_R01_01.csv`
- `S2_R02_01.csv`
- `S2_R06_01.csv`
- `S2_R31_01.csv`

## Research Questions

The project investigates the following questions:

1. Does the Xiaomi SoftAP condition exhibit a different management, control, and data-frame composition from the infrastructure AP condition?
2. Is the Xiaomi control-to-data ratio higher across repeated scenarios?
3. Which frame subtypes provide the clearest signatures of each mode?
4. How do scenario and physical environment affect the observed frame composition?
5. Which conclusions are supported by the supplied captures, and which require a controlled follow-up experiment?

## Research Question Outcomes

### 1. Frame composition differences

The Xiaomi SoftAP and infrastructure AP capture environments exhibited different IEEE 802.11 frame compositions.

Across the 12 infrastructure AP captures, the average file contained:

| Frame class | Mean frames per AP capture |
|---|---:|
| Management | 1,095.4 |
| Data | 257.8 |
| Control | 110.9 |
| Other | 9.3 |

Across the 12 Xiaomi SoftAP captures, the average file contained:

| Frame class | Mean frames per Xiaomi capture |
|---|---:|
| Control | 424.1 |
| Management | 184.6 |
| Data | 52.4 |
| Other | 10.6 |

The infrastructure AP capture environments were management-dominant, while Xiaomi SoftAP captures were control-dominant.

| Metric | Infrastructure AP | Xiaomi SoftAP |
|---|---:|---:|
| Mean management frames per file | 1,095.4 | 184.6 |
| Mean control frames per file | 110.9 | 424.1 |
| Mean data frames per file | 257.8 | 52.4 |
| Mean management-frame rate | 52.13 frames/s | 12.07 frames/s |
| Mean control-frame rate | 4.29 frames/s | 27.65 frames/s |
| Mean data-frame rate | 12.25 frames/s | 3.40 frames/s |

The observed infrastructure AP environment contained substantially more management traffic and data activity. The Xiaomi SoftAP condition contained substantially more control activity relative to both data and management traffic.

** The 24 supplied captures show a distinct difference in observed MAC-layer composition. Infrastructure AP environments were management-dominant, whereas Xiaomi SoftAP captures were control-dominant. The difference remained visible when raw counts and duration-normalized frame rates were compared.**

### 2. Control-to-data ratio across repeated scenarios

The control-to-data ratio was calculated as:

**Control-to-data ratio = Number of Control frames / Number of Data frames**

A value below 1 indicates fewer control frames than data frames. A value above 1 indicates more control frames than data frames.

| Measure | Infrastructure AP | Xiaomi SoftAP |
|---|---:|---:|
| Mean control-to-data ratio | 0.324 | 13.379 |
| Median control-to-data ratio | 0.183 | 10.012 |
| Minimum ratio | 0.048 | 2.274 |
| Maximum ratio | 1.782 | 50.100 |

The median result is important because it reduces the influence of unusually high or low individual captures. The Xiaomi median control-to-data ratio was approximately 54.7 times larger than the AP median ratio.

| Paired capture files | AP control/data ratio | Xiaomi control/data ratio | Xiaomi relative to AP |
|---|---:|---:|---:|
| `S0_R00_01-outside.csv` / `S0_R00a_01-outside-Xiaomi.csv` | 0.406 | 5.066 | 12.5x |
| `S0_R00b_01-inside.csv` / `S0_R00b_01-inside-Xiaomi.csv` | 0.124 | 2.274 | 18.4x |
| `S0_R01_01.csv` / `S0_R01_01-Xiaomi.csv` | 0.062 | 7.729 | 124.7x |
| `S1_R02_01.csv` and `S2_R02_01.csv` / `S1_R02_01-Xiaomi.csv` and `S2_R02_01-Xiaomi.csv` | 0.146 | 15.455 | 105.9x |
| `S0_R03_01.csv` / `S0_R03_01-Xiaomi.csv` | 0.272 | 23.545 | 86.5x |
| `S1_R06_01.csv` and `S2_R06_01.csv` / `S1_R06_01-Xiaomi.csv` and `S2_R06_01-Xiaomi.csv` | 0.066 | 29.550 | 447.7x |
| `S0_R08_01.csv` / `S0_R08_01-Xiaomi.csv` | 1.782 | 14.071 | 7.9x |
| `S1_R30_01.csv` / `S1_R30_01-Xiaomi.csv` | 0.298 | 6.204 | 20.8x |
| `S2_R31_01.csv` / `S2_R31_01-Xiaomi.csv` | 0.455 | 3.917 | 8.6x |

For `S1_R02_01.csv` and `S2_R02_01.csv`, the AP value is the mean of the two AP captures, while the Xiaomi value is the mean of `S1_R02_01-Xiaomi.csv` and `S2_R02_01-Xiaomi.csv`. The same averaging approach was used for the R06 entries because both S1 and S2 capture sets were present.

The Xiaomi SoftAP capture had a higher control-to-data ratio than the corresponding AP capture in every paired scenario.

**Across every paired scenario in the dataset, the Xiaomi SoftAP capture had a higher observed control-to-data ratio than the infrastructure AP capture. **

The result demonstrates a repeated MAC-layer pattern. It does not independently prove lower throughput or poorer user performance because throughput, latency, loss, retry rate, and traffic load were not controlled in the current captures.

### 3. Frame subtype signatures

The clearest Xiaomi SoftAP signature was the combination of frequent RTS, CTS, and CF-End frames.

| Xiaomi subtype | Total observed frames | Files containing subtype | Mean rate |
|---|---:|---:|---:|
| Request-to-Send (RTS) | 2,644 | 12/12 | 14.36 frames/s |
| Clear-to-Send (CTS) | 1,268 | 12/12 | 6.86 frames/s |
| CF-End | 952 | 12/12 | 5.19 frames/s |
| Beacon | 1,880 | 12/12 | 10.26 frames/s |
| Data | 627 | 12/12 | 3.39 frames/s |
| Acknowledgement | 225 | 12/12 | 1.24 frames/s |
| Probe Response | 229 | 12/12 | 1.25 frames/s |

The clearest infrastructure AP-environment signature was strong beacon activity, followed by Data and Probe Response traffic.

| AP subtype | Total observed frames | Files containing subtype | Mean rate |
|---|---:|---:|---:|
| Beacon | 11,798 | 12/12 | 46.86 frames/s |
| Data | 2,917 | 12/12 | 11.66 frames/s |
| Probe Response | 1,147 | 12/12 | 4.45 frames/s |
| Clear-to-Send | 463 | 8/12 | 1.97 frames/s |
| Acknowledgement | 450 | 12/12 | 1.83 frames/s |
| Block Ack | 304 | 3/12 | 3.25 frames/s in files where observed |
| Probe Request | 199 | 8/12 | 1.22 frames/s |
| Request-to-Send | 92 | 2/12 | 1.52 frames/s in files where observed |

The principal subtype contrasts were:

| Frame subtype | AP total | Xiaomi total |
|---|---:|---:|
| RTS | 92 | 2,644 |
| CTS | 463 | 1,268 |
| CF-End | Not observed in subtype summary | 952 |
| Beacon | 11,798 | 1,880 |
| Probe Response | 1,147 | 229 |
| Data | 2,917 | 627 |

> The clearest Xiaomi SoftAP frame signature was repeated RTS, CTS, and CF-End activity. RTS and CF-End appeared in all 12 Xiaomi files, whereas RTS appeared in only two AP files and CF-End was not present in the AP subtype summary.

> The clearest infrastructure AP-environment signature was high beacon density. Beacon frames appeared in all AP captures at a mean rate of 46.86 frames/s, compared with 10.26 frames/s for Xiaomi captures.

The CF-End frame is a strong candidate for an implementation or configuration signature of the tested Xiaomi SoftAP.- Its repeated presence does not, on its own, prove full Point Coordination Function operation. Raw PCAP/PCAPNG frame-field inspection and controlled reproduction would be required to establish its exact origin and role.

### 4. Scenario and physical-environment effects

The results show that scenario and physical environment changed the magnitude of the observed frame composition, but did not remove the core Xiaomi SoftAP versus AP difference.

The inside-versus-outside comparison used the following capture pairs:

- Inside: `S0_R00b_01-inside.csv` and `S0_R00b_01-inside-Xiaomi.csv`
- Outside: `S0_R00_01-outside.csv` and `S0_R00a_01-outside-Xiaomi.csv`

| Capture location and files | AP control/data | Xiaomi control/data | AP management/data | Xiaomi management/data |
|---|---:|---:|---:|---:|
| `S0_R00b_01-inside.csv` / `S0_R00b_01-inside-Xiaomi.csv` | 0.124 | 2.274 | 4.252 | 1.479 |
| `S0_R00_01-outside.csv` / `S0_R00a_01-outside-Xiaomi.csv` | 0.406 | 5.066 | 5.488 | 2.774 |

The control-to-data ratio increased outside for both modes. Xiaomi remained substantially more control-heavy in both contexts.

> Physical context changed the observed frame mix in both modes; however, the Xiaomi SoftAP control-heavy signature remained visible in `S0_R00b_01-inside-Xiaomi.csv` and `S0_R00a_01-outside-Xiaomi.csv`.

Several Xiaomi captures had particularly high control-to-data ratios:

| Xiaomi capture file or paired set | Control/data ratio | Observed Data frames |
|---|---:|---:|
| `S1_R06_01-Xiaomi.csv` and `S2_R06_01-Xiaomi.csv` | 29.550 | 27.5 mean |
| `S0_R03_01-Xiaomi.csv` | 23.545 | 33 |
| `S1_R02_01-Xiaomi.csv` and `S2_R02_01-Xiaomi.csv` | 15.455 | 33 mean |
| `S0_R08_01-Xiaomi.csv` | 14.071 | 28 |

The capture `S0_R08_01.csv` was an important high-activity AP scenario.

| `S0_R08_01.csv` metric | Observed value |
|---|---:|
| Total frames | 3,997 |
| Management frames | 2,581 |
| Control frames | 907 |
| Data frames | 509 |
| Beacon frames | 2,274 |
| CTS frames | 413 |
| Block Ack frames | 301 |
| Control/data ratio | 1.782 |

`S0_R08_01.csv` demonstrates that infrastructure AP environments can also become highly active and contain substantial control traffic. However, `S0_R08_01-Xiaomi.csv` still had a much higher control-to-data ratio of 14.071.

The observed frame mix depends on multiple factors:

**Observed frame mix = f(device mode, implementation, environment, traffic, capture position)**

The expression is conceptual rather than a fitted mathematical model. It highlights that the measured pattern may be influenced by device implementation, physical location, nearby networks, traffic level, channel conditions, and adapter position.

### 5. Correlation findings

The correlation analysis was performed across the 24 capture files. 

| Variables | Interpretation |
|---|---|
| Management frames and Data frames | Captures with more management traffic generally also contained more observed Data frames |
| Management frames and total captured bytes | Management activity was strongly associated with total observed byte volume |
| Management frames and total frame count | Management activity strongly contributed to total observed frame volume |
| Higher control/data ratio and lower Data-frame count | Control-heavy captures tended to contain fewer observed Data frames |
| Control frames and total frame count | Control activity contributed to total frame volume, but less consistently than management traffic |

The relationship between control-to-data ratio and Data-frame count can be expressed as:

> In the supplied capture set, high control-to-data ratios tended to occur in captures with relatively few observed Data frames. This relationship is correlational and does not prove that control traffic caused lower data transmission.

Possible contributing factors include:

- SoftAP firmware or chipset behaviour.
- RTS/CTS threshold configuration.
- Hidden-node protection.
- Low offered data load.
- Different application traffic patterns.
- Capture loss or incomplete monitor-mode visibility.
- Channel contention.
- Interference.
- Physical device placement.

The observed frame mix can also be represented conceptually as:

**Observed frame mix = f(device mode, implementation, physical environment, offered traffic, channel conditions, capture position)**

This is a conceptual expression rather than a fitted statistical model. It means that the observed Management, Control, Data, and Other frame counts may be influenced simultaneously by device mode, firmware, chipset, physical environment, nearby networks, traffic conditions, channel conditions, and the monitor-mode adapter position.

### 6. Conclusions supported by the captures

The following conclusions are directly supported by the supplied CSV files:

1. Xiaomi SoftAP captures had a higher observed control-to-data ratio than AP captures in every paired scenario.
2. Xiaomi SoftAP captures were control-intensive relative to their observed data traffic.
3. AP capture environments were management-intensive relative to Xiaomi SoftAP captures.
4. RTS, CTS, and CF-End were recurring Xiaomi subtype signatures.
5. Beacon and Probe Response activity were stronger in the AP capture environments.
6. AP captures contained substantially more observed Beacon frames: 11,798 compared with 1,880 in Xiaomi captures.
7. AP beacon activity remained higher after duration normalization, with mean rates of 46.86 frames/s for AP and 10.26 frames/s for Xiaomi.
8. Scenario and environment altered the size of the observed difference but did not reverse the repeated Xiaomi control-heavy pattern.
9. `S0_R08_01.csv` represented a high-activity environment with substantial Beacon, CTS, and Block Ack activity.
10. High control-to-data ratios were associated with low observed Data-frame counts in the capture set.


> Note: The infrastructure AP environments contained substantially more observed Beacon activity. However, without filtering by the target AP’s BSSID or source MAC address, this indicates higher overall environmental beacon activity rather than transmissions from a single access point.

### 7. Conclusions requiring controlled follow-up experiments

The following claims require additional controlled testing and should not be presented as conclusions of the current dataset:

| Claim | Reason additional testing is needed |
|---|---|
| Xiaomi SoftAP is less efficient than infrastructure AP | Throughput, latency, retries, jitter, and PHY-aware airtime were not measured |
| RTS/CTS activity caused lower Xiaomi Data traffic | The present result is correlational, not causal |
| CF-End proves Xiaomi implements Point Coordination Function | Raw frame fields, firmware behaviour, and reproduction on other devices must be verified |
| All Xiaomi devices behave like the tested Xiaomi SoftAP | The experiment represents a specific device and configuration condition |
| All SoftAP implementations are more control-heavy than APs | Other smartphones, consumer routers, and Linux SoftAP implementations were not tested |
| AP mode always provides better user performance | No end-user performance metrics were collected |
| Total captured bytes represent physical airtime | PHY rate, modulation, coding, preamble, aggregation, retry, and channel-width information are required |
| The target AP generated every captured management frame | Monitor mode may capture neighbouring BSSIDs and unrelated APs on the selected channel |

A controlled follow-up experiment should keep the following parameters constant:

- Channel and channel width.
- Physical location.
- Capture duration.
- Client device.
- Number of connected clients.
- Offered TCP and UDP traffic.
- Capture-adapter position and antenna orientation.
- Security mode and AP/SoftAP settings.

The follow-up should measure:

- Throughput.
- Latency.
- Jitter.
- Packet loss.
- Retry frames.
- RTS, CTS, ACK, and Block Ack rate.
- Data-frame size distribution.
- Target-BSSID-filtered frame composition.
- PHY rate and transmission-duration parameters.

### 8. Research-question outcome summary

 **RQ1 was answered affirmatively.** The Xiaomi SoftAP and infrastructure AP captures exhibited different frame compositions. Xiaomi captures were control-dominant, whereas AP capture environments were management-dominant.

 **RQ2 was answered affirmatively.** Xiaomi had a higher control-to-data ratio in every paired scenario. The median ratio was 10.012 for Xiaomi compared with 0.183 for AP.

 **RQ3 identified distinct subtype signatures.** Xiaomi was characterized by recurring RTS, CTS, and CF-End frames. AP environments were characterized by high Beacon and Probe Response activity, more observed ordinary Data frames, and occasional Block Ack activity.

 **RQ4 showed that environment affected magnitude but not the main repeated pattern.** Indoor/outdoor context and the scenarios represented by `S0_R01_01.csv`, `S1_R02_01.csv`, `S2_R02_01.csv`, `S0_R03_01.csv`, `S1_R06_01.csv`, `S2_R06_01.csv`, `S0_R08_01.csv`, `S1_R30_01.csv`, and `S2_R31_01.csv` changed observed counts and rates. Xiaomi nevertheless remained control-heavy relative to AP in every paired observation. `S0_R08_01.csv` showed that infrastructure environments can also become highly active and control-rich.

 **RQ5 established the evidence boundary.** The captures support repeated descriptive conclusions about observed MAC-layer patterns. Controlled experiments are needed to identify causes, measure performance effects, isolate target BSSIDs, validate CF-End behaviour, and generalize beyond the tested Xiaomi SoftAP condition.

## Automated Analysis Tool

A Python analysis program was developed with assistance from a large language model (LLM). The program processes similarly structured CSV files through command-line arguments.

The analysis pipeline:

1. Reads the SoftAP and infrastructure AP CSV files.
2. Validates the required input columns.
3. Converts frame length and capture time to numeric values.
4. Classifies frame descriptions into broad IEEE 802.11 categories.
5. Assigns each capture a mode label.
6. Computes comparative metrics.
7. Exports CSV result tables.
8. Generates rectangular PNG visualizations.
9. Creates metadata files describing the generated figures.

### Required CSV columns

The current implementation requires the following columns:

| Column | Purpose |
|---|---|
| `Type/Subtype` | Wi-Fi frame subtype description |
| `Source` | Source MAC address or exported source identifier |
| `Length` | Captured frame length in bytes |
| `Time` | Capture timestamp in seconds |

Optional columns such as `Destination`, retry flags, sequence numbers, channel, data rate, channel width, and signal information can support future analysis extensions.

## Frame Classification

The current classifier maps exported Wireshark subtype text into four broad classes.

| Class | Examples |
|---|---|
| Management | Beacon, Probe Request, Probe Response, Association, Authentication, Action |
| Control | Request-to-Send, Clear-to-Send, Acknowledgement, Block Ack, Block Ack Request, CF-End |
| Data | Data, QoS Data, Null Function, QoS Null Function |
| Other | Labels not matched by the classification rules |

This is a transparent text-label classification. For a final publication-quality analysis, the classification should be confirmed from raw packet-capture files and IEEE 802.11 Frame Control fields.

## Implemented Metrics

### Frame-class counts

The program counts Management, Control, Data, and Other frames separately for the two capture modes.

### Frame rates

To reduce the influence of unequal capture duration, rates can be expressed as:

**Frame rate = Number of observed frames / Capture duration in seconds**

### Control-to-data ratio

The control-to-data ratio is calculated as:

**Control-to-data ratio = Number of Control frames / Number of Data frames**

This represents the observed amount of control coordination relative to observed data frames. It is not, by itself, a direct efficiency score.

### Management-to-data ratio

The management-to-data ratio is calculated as:

**Management-to-data ratio = Number of Management frames / Number of Data frames**

This helps describe whether a capture contains relatively more discovery, advertisement, and connection-maintenance activity compared with data traffic.

### Per-source-MAC analysis

The tool groups frame counts by:

**Mode + Source + Frame class**

This helps identify which observed source identifiers contribute to management, control, data, or other traffic.

### Pseudo-airtime or captured-byte volume

The current pseudo-airtime metric is calculated as the sum of frame lengths:

**Pseudo-airtime proxy = Sum of captured frame lengths in bytes**

This is only a relative captured-byte measure. It is not physical airtime because actual airtime depends on transmission rate, modulation and coding, channel width, preamble, guard interval, aggregation, retransmissions, and inter-frame spacing.

### RTS–CTS–Data–ACK pattern screening

The current sequence detector searches for adjacent rows matching:

**Request-to-Send → Clear-to-Send → Data or QoS Data → Acknowledgement or Block Ack**

This is an exploratory screening method. It does not yet validate transmitter and receiver addresses, sequence numbers, retry flags, or precise timing constraints.

## Timeline Visualization

The analysis program generates subtype event timelines for the SoftAP and infrastructure AP captures.

The timeline provides:

- Capture time on the horizontal axis.
- Frame subtype on the vertical axis.
- A separate colour for each subtype.
- A separate marker shape for each subtype.
- Small vertical point offsets to reduce overlap.
- Rectangular publication-style dimensions.
- One-second vertical grid intervals.
- Hover information for timestamp, subtype, frame class, source, destination, and frame length when available.

The timeline shows when frame events were observed. It does not prove that nearby frames belong to the same protocol exchange.

## Main Observations

Across the expanded dataset:

- The mean control-frame count was 110.9 per infrastructure AP file and 424.1 per Xiaomi file.
- The mean data-frame count was 257.8 per infrastructure AP file and 52.4 per Xiaomi file.
- The mean management-frame count was 1,095.4 per infrastructure AP file and 184.6 per Xiaomi file.
- The mean control-to-data ratio was 0.324 for infrastructure AP and 13.379 for Xiaomi.
- The median control-to-data ratio was 0.183 for infrastructure AP and 10.012 for Xiaomi.
- The Xiaomi control-to-data ratio was higher in every paired scenario.
- Xiaomi captures repeatedly contained Request-to-Send, Clear-to-Send, and CF-End frames.
- Infrastructure AP captures contained substantially more observed Beacon activity.
- Infrastructure AP captures contained 11,798 observed Beacon frames compared with 1,880 in Xiaomi captures.
- The approximate mean Beacon rate was 46.86 frames per second for infrastructure AP and 10.26 frames per second for Xiaomi.

## Bounded Interpretation

Within the supplied capture dataset, the Xiaomi SoftAP condition has a consistently control-intensive observed frame signature. The infrastructure AP capture condition has a management-intensive observed signature and generally more observed data-frame activity.

This is a descriptive result about the supplied captures. It does not prove that:

- Every Xiaomi phone behaves in the same way.
- Every SoftAP implementation is inefficient.
- Xiaomi SoftAP provides lower throughput.
- Infrastructure AP mode is always better.
- CF-End frames prove complete Point Coordination Function operation.
- Total frame length is equal to physical airtime.

The observed differences may be influenced by traffic load, capture duration, location, visible neighbouring networks, channel selection, target BSSID filtering, client population, and monitor-mode observability.

## Responsible Capture and Privacy

The captures were collected for academic analysis of Wi-Fi MAC-layer behaviour. A TP-Link USB Wi-Fi Network Interface Controller (NIC) supporting monitor mode was used because ordinary client mode does not expose the complete set of management and control frames required for the analysis.

The adapter was used as a passive observation instrument. It was not used for:

- Frame injection.
- Deauthentication.
- Jamming.
- Credential collection.
- Unauthorized network access.
- Traffic manipulation.
- Payload decryption.
- Exploitation.

## Capture Limitations

The monitor-mode adapter observes only frames that reach its antenna and can be decoded reliably. It does not observe every transmission in the environment.

Important limitations include:

- Frames may be missed because of distance, obstruction, weak signal, interference, or receiver limitations.
- Monitor mode generally observes one selected channel at a time.
- Networks operating on other channels are not included.
- USB buffering, drivers, collisions, and high frame rates may cause packet loss.
- The absence of a complete RTS–CTS–Data–ACK sequence does not prove that the exchange did not occur.
- RSSI values may reflect driver or export limitations.
- The available CSV data does not contain enough PHY information for physical airtime calculation.
- Filename-based mode labels should be confirmed using capture documentation and BSSID information.
- Frame counts do not equal application throughput.


## Installation

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Or install the core dependencies directly:

```bash
pip install pandas plotly kaleido
```

## Usage

Example command:

```bash
python src/wifi_mode_analysis.py \
    --softap "softAP_capture1.csv" \
    --ap "AP_capture1.csv" \
    --outdir "outputs/example_run"
```

On Windows PowerShell, use the backtick for line continuation:

```powershell
python .\src\wifi_mode_analysis.py `
    --softap "softAP_capture1.csv" `
    --ap "AP_capture1.csv" `
    --outdir "outputs\example_run"
```

## Generated Outputs

The program can generate:

```text
frame_class_counts_by_mode.csv
key_subtype_counts_by_mode.csv
control_to_data_ratio_by_mode.csv
per_mac_class_counts.csv
pseudo_airtime_by_class.csv
rts_cts_data_ack_sequences_by_mode.csv
frame_class_mix.png
key_subtypes_by_mode.png
control_to_data_ratio.png
cumulative_softap.png
cumulative_ap.png
pseudo_airtime_by_class.png
frame_subtype_timeline_softap.png
frame_subtype_timeline_ap.png
```

Metadata files with the suffix `.meta.json` are also generated for the charts.

## Limitations of the Current Software

The current implementation has several limitations:

1. Mode labels are assigned from command-line input or filename conventions.
2. Classification depends on the text exported in the `Type/Subtype` field.
3. Selected subtype counting may be sensitive to exact Wireshark label spelling.
4. The sequence detector examines adjacent rows rather than validated exchanges.
5. The pseudo-airtime measure is not PHY-aware.
6. Raw frame counts are affected by duration and traffic load.
7. The current analysis does not establish application throughput.
8. Monitor-mode captures provide only a partial observation of the channel.
9. The available dataset is not sufficient for universal claims about SoftAP systems.

## Future Work

1. Repeat each paired scenario 10–20 times in a high-traffic environment, specifically the Faculty of Informatics building during the academic semester.
2. Use the same channel, location, client, duration, and traffic load.
3. Generate matched Transmission Control Protocol (TCP) and User Datagram Protocol (UDP) traffic with `iperf3`.
4. Record throughput, latency, jitter, packet loss, retries, data rate, and channel width.
5. Compare Xiaomi with other phone models, consumer routers, and Linux-based SoftAP systems.
