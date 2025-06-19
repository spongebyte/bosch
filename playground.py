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
    response, status = response_parser(data)

    if status in ["keepalive", "invalid_request"]:
        return

    print("\n", end="")
    if status:
        print(f"\tpotential status: {status.upper()}")
    if response["measure_type"]:
        print(f"\tmeasure type: {response['measure_type'].upper()}")

    data_hex = data.hex()

    print(f"\t\t{data_hex}")
    print("\t\theader\ttype\tsub\tcount\tval1\tval2\tval3")
    print(
        f"\t\t{response['header']}\t{response['type']}\t{response['subtype']}\t{response['count']}\t{response['val0']:.3f}\t{response['val1']:.3f}\t{response['val2']:.3f}"
    )


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
            for idx, mode_name in PAYLOADS_TR.items():
                print(f"{idx:2}: {mode_name}")
            user_input = await prompt_session.prompt_async("hex payload, index number, or x: ")

            if user_input.isdigit() and len(user_input) <= 2:
                chosen_mode = PAYLOADS_TR[int(user_input)]
                await client.write_gatt_char(CHAR_UUID, bytes.fromhex(PAYLOADS[chosen_mode]), True)
            elif user_input.startswith("0x"):
                try:
                    hex_input = bytes.fromhex(user_input[2:])
                    await client.write_gatt_char(CHAR_UUID, hex_input, True)
                except ValueError:
                    pass
            else:
                try:
                    hex_input = bytes.fromhex(user_input)
                    if not hex_input:
                        raise ValueError
                    await client.write_gatt_char(CHAR_UUID, hex_input, True)
                except ValueError:
                    if user_input in ["x", "."]:
                        await client.write_gatt_char(CHAR_UUID, bytes.fromhex(PAYLOADS["trigger"]), True)
                    else:
                        pass


if __name__ == "__main__":
    asyncio.run(main())
