# https://github.com/ketan/Bosch-GLM50C-Rangefinder/blob/main/python/main.py
# https://github.com/lz1asl/CaveSurvey/issues/150

import asyncio
import json
import struct
import time
from collections import defaultdict
from pathlib import Path

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from prompt_toolkit import PromptSession

from device_specs import (
    CHAR_UUID,
    DEVICE_MAC,
    PAYLOADS,
    PREVENT_LASER_SLEEP,
    RESPONSES,
    TIMEOUT,
)

LOGFILE = Path("hunt.log")
LOGFILE.unlink(missing_ok=True)


def response_parser(data: bytearray) -> tuple[dict, str | None]:
    data_str = data.hex()

    status = next((RESPONSES["status"][code] for code in RESPONSES["status"] if data_str.startswith(code)), None)

    response = {
        "header": data_str[:6],
        "type": data_str[6:8],
        "subtype": data_str[8:10],
        "count": -1,
        "val0": -1,
        "val1": -1,
        "val2": -1,
        "measure_type": RESPONSES["measure"].get(data_str[:8]),
    }

    if len(data[5:7]) == 2:
        response["count"] = struct.unpack("<H", data[5:7])[0]
    if len(data[7:11]) == 4:
        response["val0"] = struct.unpack("<f", data[7:11])[0]
    if len(data[11:15]) == 4:
        response["val1"] = struct.unpack("<f", data[11:15])[0]
    if len(data[15:19]) == 4:
        response["val2"] = struct.unpack("<f", data[15:19])[0]

    return response, status


def notification_handler(char: BleakGATTCharacteristic, data: bytearray):
    if state["preventing_laser_sleep"]:
        print("received response but ignoring (preventing laser from sleeping)")
        return

    response, status = response_parser(data)

    if status in ["keepalive", "invalid_request"]:
        return

    print("\n", end="")
    if status:
        print(f"\tpotential status: {status.upper()}")
    if response["measure_type"]:
        print(f"\tmeasure type: {response['measure_type'].upper()}")

    data_hex = data.hex()
    if data_hex.startswith("c055100100"):  # laser off
        state["turned_off_payloads"].append(hex(state["current_payload"]))
        state["need_back_on"] = True
        return

    if measure_type := RESPONSES["measure"].get(data_hex[:8]):
        print(f"\tMEASUREMENT response {measure_type.upper()}")

    print(f"\t\t{data_hex}")
    print("\t\theader\ttype\tsub\tcount\tval1\tval2\tval3")
    print(
        f"\t\t{response['header']}\t{response['type']}\t{response['subtype']}\t{response['count']}\t{response['val0']:.3f}\t{response['val1']:.3f}\t{response['val2']:.3f}"
    )

    if measure_type == "distance_only":
        state["need_back_on"] = True
        state["triggered_at_payloads"].append(hex(state["current_payload"]))

    state["response_log"][data_hex[:10]].append((hex(state["current_payload"]), data_hex))


async def main():
    print("starting scan... ", end="", flush=True)
    device = await BleakScanner.find_device_by_address(DEVICE_MAC, timeout=TIMEOUT, cb=dict(use_bdaddr=True))
    if device is None:
        print(f"could not find device with address {DEVICE_MAC}")
        return

    prompt_session = PromptSession()

    print("connecting to device... ", end="", flush=True)
    async with BleakClient(device) as client:
        print("connected")
        await client.start_notify(CHAR_UUID, notification_handler)

        await client.write_gatt_char(CHAR_UUID, bytes.fromhex(PAYLOADS["output_on"]), True)
        # or explicitly setting a mode will enable indications

        await asyncio.sleep(0.5)
        # just to make sure that the first "send payload" message doesn't come too early

        await client.write_gatt_char(CHAR_UUID, bytes.fromhex(PAYLOADS["length"]), True)
        await client.write_gatt_char(CHAR_UUID, bytes.fromhex(PAYLOADS["trigger"]), True)
        state["laser_on_since_ts"] = time.time()
        await asyncio.sleep(0.2)

        while client.is_connected:
            start_from = "c056010000"
            for i in range(0x10000):
                if state["need_back_on"]:
                    await asyncio.sleep(0.1)
                    await client.write_gatt_char(CHAR_UUID, bytes.fromhex(PAYLOADS["length"]), True)
                    await client.write_gatt_char(CHAR_UUID, bytes.fromhex(PAYLOADS["trigger"]), True)
                    await asyncio.sleep(0.1)
                    state["need_back_on"] = False

                if time.time() - state["laser_on_since_ts"] >= PREVENT_LASER_SLEEP:
                    state["laser_on_off_at"].append(hex(state["current_payload"]))
                    await asyncio.sleep(0.1)
                    state["preventing_laser_sleep"] = True
                    await client.write_gatt_char(CHAR_UUID, bytes.fromhex(PAYLOADS["length"]), True)
                    await client.write_gatt_char(CHAR_UUID, bytes.fromhex(PAYLOADS["trigger"]), True)
                    state["laser_on_since_ts"] = time.time()
                    await asyncio.sleep(0.1)
                    state["preventing_laser_sleep"] = False
                    with open(LOGFILE, "w") as fp:
                        json.dump(state, fp, default=convert_sets_to_lists, indent=2)

                payload = int(start_from, 16) + i
                payload_hex = payload.to_bytes(5)
                state["current_payload"] = payload
                print(hex(payload))
                await client.write_gatt_char(CHAR_UUID, payload_hex, True)
                await asyncio.sleep(0.05)
            return


def convert_sets_to_lists(obj):
    if isinstance(obj, set):
        return list(obj)
    return obj


if __name__ == "__main__":
    state = {
        "current_payload": -1,
        "need_back_on": False,
        "turned_off_payloads": [],
        "triggered_at_payloads": [],
        "laser_on_since_ts": -1,
        "preventing_laser_sleep": False,
        "response_log": defaultdict(list),
        "laser_on_off_at": [],
    }
    asyncio.run(main())
