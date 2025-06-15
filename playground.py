# https://github.com/ketan/Bosch-GLM50C-Rangefinder/blob/main/python/main.py
# https://github.com/lz1asl/CaveSurvey/issues/150

import asyncio
import struct

from bleak import BleakClient, BleakScanner
from bleak.backends.characteristic import BleakGATTCharacteristic

with open("mac_address.txt", "r") as fp:
    DEVICE_MAC = fp.read().strip()

CHAR_UUID = "02a6c0d1-0451-4000-b000-fb3210111989"
RESPONSES = {
    "keepalive": "c011003a",
    "invalid_request": "03000a",
}
PAYLOADS = {
    "output_on": "c0550201001a",
    "trigger": "c05601001e",
    "mode_bubble": "c05502f108ac",
    "mode_distance": "c05502f101ee",
    "mode_continuous": "c05502f102a2",
}
payloads_idx_tr = {idx: payload_name for idx, payload_name in enumerate(PAYLOADS)}

mode_hunt = 0xC05502F10000


def notification_handler(char: BleakGATTCharacteristic, data: bytearray):
    if data == bytes.fromhex(RESPONSES["keepalive"]):
        return

    if data == bytes.fromhex(RESPONSES["invalid_request"]):
        print("x", end="", flush=True)
        return

    data_str = "0x " + " ".join([f"{byte:02x}" for byte in data])
    # print("   const ?  mode? count measure1    measure2    measure3    ck")
    # print("   ----- -- ----- ----- ----------- ----------- ----------- --")
    print(data_str)

    # try:
    #     cnt = struct.unpack("<H", data[5:7])[0]
    #     print(f"cnt: {cnt}")
    # except struct.error:
    #     pass

    # val = {}
    # for idx, start_pos in enumerate(range(7, 19, 4)):
    #     try:
    #         val[idx] = struct.unpack("<f", data[start_pos : start_pos + 4])[0]
    #         print(f"val {idx}: {val[idx]}")
    #     except struct.error:
    #         pass

    # print("------------------------------------------------")


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

        await client.write_gatt_char(CHAR_UUID, bytes.fromhex(PAYLOADS["output_on"]), True)
        # or explicitly setting a mode will enable indications

        while client.is_connected:
            # for idx, payload_name in payloads_idx_tr.items():
            #     print(f"{idx}\t{payload_name}")
            # try:
            #     user_input = input("idx: ")
            #     if user_input == "q":
            #         return
            #     else:
            #         user_input = int(user_input)
            #         await client.write_gatt_char(CHAR_UUID, bytes.fromhex(PAYLOADS[payloads_idx_tr[user_input]]), True)
            # except:
            #     print("")

            global mode_hunt
            await client.write_gatt_char(CHAR_UUID, mode_hunt.to_bytes(6), True)
            mode_hunt += 1
            # await asyncio.sleep(0.1)


if __name__ == "__main__":
    asyncio.run(main())
