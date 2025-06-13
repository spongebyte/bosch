# https://github.com/ketan/Bosch-GLM50C-Rangefinder/blob/main/python/main.py
# https://github.com/lz1asl/CaveSurvey/issues/150

import asyncio
import struct

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic

with open("mac_address.txt", "r") as fp:
    DEVICE_MAC = fp.read().strip()

CHAR_UUID = "02a6c0d1-0451-4000-b000-fb3210111989"
PAYLOADS = {
    "keepalive": "c011003a",
    "output_on": "c0550201001a",
    "angle_mode": "c05502f108ac",
    "distance_mode": "c05502f101ee",
    "trigger": "c05601001e",
}


def payload(_payload):
    return bytes.fromhex(PAYLOADS[_payload])


def notification_handler(char: BleakGATTCharacteristic, data: bytearray):
    if data == payload("keepalive"):
        return

    data_str = "0x " + " ".join([f"{byte:02x}" for byte in data])
    print(data_str)

    val = {}
    for idx, start_pos in enumerate(range(7, 19, 4)):
        try:
            val[idx] = str(round(struct.unpack("<f", data[start_pos : start_pos + 4])[0] * 1000))
            print(f"val {idx}: {val[idx]}")
        except struct.error:
            pass

    print("------------------------------------------------")


async def main():
    print("starting scan...")
    device = await BleakScanner.find_device_by_address(DEVICE_MAC, timeout=5, cb=dict(use_bdaddr=True))
    if device is None:
        print(f"could not find device with address {DEVICE_MAC}")
        return

    print("connecting to device...")
    async with BleakClient(device) as client:
        print("connected")
        await client.start_notify(CHAR_UUID, notification_handler)

        await client.write_gatt_char(CHAR_UUID, payload("output_on"), True)
        # or explicitly setting a mode will enable indications
        # await client.write_gatt_char(CHAR_UUID, payload("distance_mode"), True)
        # await client.write_gatt_char(CHAR_UUID, payload("angle_mode"), True)

        while client.is_connected:
            user_input = input("adx? ")
            match user_input:
                case "a":
                    await client.write_gatt_char(CHAR_UUID, payload("angle_mode"), True)
                case "d":
                    await client.write_gatt_char(CHAR_UUID, payload("distance_mode"), True)
                case "x":
                    await client.write_gatt_char(CHAR_UUID, payload("trigger"), True)

            # await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
