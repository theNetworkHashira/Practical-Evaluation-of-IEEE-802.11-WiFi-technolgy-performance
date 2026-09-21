# Data Format

Required columns:

- `Type/Subtype`: Wireshark frame subtype description.
- `Source`: source MAC address or exported source identifier.
- `Length`: captured frame length in bytes.
- `Time`: capture timestamp in seconds.

Recommended future columns include `Destination`, retry flags, sequence numbers, channel, data rate, channel width, and capture identifier.
