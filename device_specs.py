from collections import namedtuple

DEVICE_MAC = "90:7B:C6:62:15:5E"

TIMEOUT = 8
CHAR_UUID = "02a6c0d1-0451-4000-b000-fb3210111989"

PREVENT_LASER_SLEEP = 17  # 20s for automatic laser idle

MeasurementResponse = namedtuple("Measurement", ["name", "response_hex_code", "val0", "val1", "val2", "from_mode"])
measurement_responses = [
    # angle_pitch, angle_roll, distance are meaningful and represent the latest measurements
    # everything else is either computed, (sum of) previous values, or useless
    MeasurementResponse("level_upright", "c0551021", "angle", None, None, ["level"]),
    MeasurementResponse("level", "c0551058", "angle_roll", "angle_pitch", None, ["level"]),
    MeasurementResponse("distance_only", "c0551005", "distance", None, None, ["length", "continuous_big"]),
    MeasurementResponse(
        "distance_minmax", "c0551009", "distance", "distance_min", "distance_max", ["continuous_minmax"]
    ),
    MeasurementResponse("wall_area", "c0551039", None, "distance", None, ["wall_area"]),
    MeasurementResponse("wall_area", "c055103d", "area", "distance", "prev_distance_sum", ["wall_area"]),
    MeasurementResponse(
        "indirect_right", "c0551029", "computed_distance", "distance", "angle_pitch", ["indirect_right"]
    ),
    MeasurementResponse(
        "indirect_bottom", "c055102d", "computed_distance", "distance", "angle_pitch", ["indirect_bottom"]
    ),
    MeasurementResponse("indirect_double", "c0551031", None, "distance", "angle_pitch", ["indirect_double"]),
    MeasurementResponse(
        "indirect_double", "c0551035", "computed_distance", "distance", "angle_diff", ["indirect_double"]
    ),
    MeasurementResponse("area", "c055100d", None, "distance", None, ["area"]),
    MeasurementResponse("area", "c0551011", "area", "prev_distance", "distance", ["area"]),
    MeasurementResponse("volume", "c0551015", None, "distance", None, ["volume"]),
    MeasurementResponse("volume", "c0551019", None, "distance", None, ["volume"]),
    MeasurementResponse("volume", "c055101d", "volume", "distance", None, ["volume"]),
]

StatusResponse = namedtuple("Status", ["name", "response_hex_code"])
status_responses = [
    StatusResponse("keepalive", "c011003a"),
    StatusResponse("invalid_request", "03000a"),
    StatusResponse("laser off", "c055100100"),
    StatusResponse("laser on", "c055100101"),
]

ActionPayload = namedtuple("Mode", ["name", "trigger_hex_code"])
general_actions = [
    ActionPayload("output_on", ["c0550201001a"]),
    ActionPayload("trigger", ["c05601001e"]),
]

modes = [
    ActionPayload("level", ["c05502f108ac"]),
    ActionPayload("length", ["c05502f101ee"]),
    ActionPayload("continuous_big", ["c05502f11a28"]),
    ActionPayload("continuous_minmax", ["c05502f102a2", "c05502f14a58"]),
    ActionPayload("wall_area", ["c05502f11cb0"]),
    ActionPayload("indirect_right", ["c05502f14e2a", "c05502f10a46"]),
    ActionPayload("indirect_bottom", ["c05502f10be0"]),
    ActionPayload("indirect_double", ["c05502f10d78", "c05502f1519e"]),
    ActionPayload("area", ["c05502f11964", "c05502f1043a"]),
    ActionPayload("volume", ["c05502f10776", "c05502f14914", "c05502f19468"]),
    ActionPayload("stake_out", ["c05502f14cc0"]),
]

modes_extra = [
    ActionPayload("mode_menu", ["c05502f13e86"]),
    ActionPayload("delete_mem", ["c05502f19682", "c05502f1f4aa"]),
    ActionPayload("help", ["c05502f1d004"]),
    ActionPayload("pro360", ["c05502f1f232"]),
    ActionPayload("set", ["c05502f1ce16"]),
    ActionPayload("app_factory", ["c05502f14582"]),
    ActionPayload("game", ["c05502f1ca64"]),
    ActionPayload(
        "reboot",
        [
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
    ),
]

RESPONSES = {
    "status": {item.response_hex_code: item.name for item in status_responses},
    "measure": {item.response_hex_code: item.name for item in measurement_responses},
}


PAYLOADS = {item.name: item.trigger_hex_code[0] for bucket in [general_actions, modes, modes_extra] for item in bucket}

PAYLOADS_TR = {idx: payload_name for idx, payload_name in enumerate(PAYLOADS)}
