DEVICE_MAC = "90:7B:C6:62:15:5E"

TIMEOUT = 8
CHAR_UUID = "02a6c0d1-0451-4000-b000-fb3210111989"

measure_types = {
    "level": ["5800"],
    "distance_only": ["0500"],  # length, continuous_big
    "distance_minmax": ["0900", "0100"],  # continuous, continuous_minmax
    "wall_area": ["3901", "3d01"],
    "indirect_right": ["2900"],
    "indirect_bottom": ["2d00"],
    "indirect_double": ["3101", "3500"],
    "area": ["0d01", "1100"],
    "volume": ["1501", "1901", "1d00"],
}

mode_enable = {
    "level": ["c05502f108ac"],
    "length": ["c05502f101ee"],
    "continuous": ["c05502f102a2"],
    "continuous_big": ["c05502f11a28"],
    "continuous_minmax": ["c05502f14a58"],
    "wall_area": ["c05502f11cb0"],
    "indirect_right": ["c05502f14e2a", "c05502f10a46"],
    "indirect_bottom": ["c05502f10be0"],
    "indirect_double": ["c05502f10d78", "c05502f1519e"],
    "area": ["c05502f11964", "c05502f1043a"],
    "volume": ["c05502f10776", "c05502f14914", "c05502f19468"],
    "stake_out": ["c05502f14cc0"],
}

mode_extra = {
    "mode_menu": ["c05502f13e86"],
    "delete_mem": ["c05502f19682", "c05502f1f4aa"],
    "help": ["c05502f1d004"],
    "pro360": ["c05502f1f232"],
    "set": ["c05502f1ce16"],
    "app_factory": ["c05502f14582"],
    "game": ["c05502f1ca64"],
    "reboot": [
        "c05502f11d16",
        "c05502f12132",
        "c05502f11d16",
        "c05502f13f20",
        "c05502f15374",
        "c05502f169c8",
        "c05502f195ce",
        "c05502f19724",
        "c05502f19958",
        "c05502f1af72",
        "c05502f1bdf6",
        "c05502f1c928",
        "c05502f1cfb0",
        "c05502f1d1a2",
        "c05502f11d16",
        "c05502f11ffc",
        "c05502f13f20",
        "c05502f1431a",
        "c05502f14424",
        "c05502f15374",
        "c05502f169c8",
        "c05502f195ce",
        "c05502f19724",
        "c05502f19958",
        "c05502f1af72",
        "c05502f1b7f8",
        "c05502f1bdf6",
        "c05502f1c928",
        "c05502f1cfb0",
        "c05502f1d1a2",
    ],
}


RESPONSES = {
    "noise": {
        "c011003a": "keepalive",
        "03000a": "invalid_request?",
        "000082": "invalid_trigger?",
    },
    "measures": {
        data_mode_hex: measure_name for measure_name, hex_codes in measure_types.items() for data_mode_hex in hex_codes
    },
}

PAYLOADS = {
    "output_on": "c0550201001a",
    "trigger": "c05601001e",
}

for bucket in [mode_enable, mode_extra]:
    for mode_name, enable_payloads in bucket.items():
        PAYLOADS[mode_name] = enable_payloads[0]
        PAYLOADS[mode_name] = enable_payloads[0]

PAYLOADS_TR = {idx: payload_name for idx, payload_name in enumerate(PAYLOADS)}
