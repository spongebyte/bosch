# https://github.com/ketan/Bosch-GLM50C-Rangefinder/blob/main/python/main.py
# https://github.com/lz1asl/CaveSurvey/issues/150

import asyncio
import struct

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from prompt_toolkit import PromptSession

from device_specs import (
    CHAR_UUID,
    DEVICE_MAC,
    PAYLOADS,
    PAYLOADS_TR,
    RESPONSES,
    TIMEOUT,
)


def notification_handler(char: BleakGATTCharacteristic, data: bytearray):
    data_str = "".join(f"{byte:02x}" for byte in data)
    if data_str in RESPONSES["noise"]:
        # print(f"{data_str}\t{RESPONSES['noise'][data_str]}")
        return

    try:
        data_header_hex = "".join([f"{byte:02x}" for byte in data[:3]])
    except IndexError:
        data_header_hex = -1

    try:
        data_mode_hex = "".join([f"{byte:02x}" for byte in data[3:5]])
    except IndexError:
        data_mode_hex = -1

    try:
        data_count = struct.unpack("<H", data[5:7])[0]
    except struct.error:
        data_count = -1

    val = {}
    for idx, start_pos in enumerate(range(7, 19, 4)):
        try:
            val[idx] = struct.unpack("<f", data[start_pos : start_pos + 4])[0]
        except struct.error:
            val[idx] = -1

    data_hex = "".join([f"{byte:02x}" for byte in data])

    print()
    if measure_type := RESPONSES["measures"].get(data_mode_hex):
        print(f"\t\t\tthis was a {measure_type} measurement")
    print(f"\t\t\traw response: {data_hex}")
    print("\t\t\theader\tmode\tcount\tval1\tval2\tval3")
    print(
        f"\t\t\t{data_header_hex}\t{data_mode_hex}\t{data_count}\t{val.get(0):.3f}\t{val.get(1):.3f}\t{val.get(2):.3f}"
    )

    if measure_type == "wall_area":
        state["delayed_measure_requested"] = True


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

        while client.is_connected:
            if state["delayed_measure_requested"]:
                print("delayed_measure_requested")
                await client.write_gatt_char(CHAR_UUID, bytes.fromhex(PAYLOADS["indirect_bottom"]), True)
                await client.write_gatt_char(CHAR_UUID, bytes.fromhex(PAYLOADS["trigger"]), True)
                await asyncio.sleep(3)
                await client.write_gatt_char(CHAR_UUID, bytes.fromhex(PAYLOADS["trigger"]), True)
                await asyncio.sleep(1)
                await client.write_gatt_char(CHAR_UUID, bytes.fromhex(PAYLOADS["wall_area"]), True)
                await client.write_gatt_char(CHAR_UUID, bytes.fromhex(PAYLOADS["trigger"]), True)
                state["delayed_measure_requested"] = False
            await asyncio.sleep(0.1)


if __name__ == "__main__":
    state = {"delayed_measure_requested": False}
    asyncio.run(main())
