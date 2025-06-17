* Plenty of "reboot" payload codes. No idea what they're supposed to do.
* For some reason, some modes can be reached from different payload codes. Not sure why.
* Some menus can be accessed, so I guess that there might be a way to key in buttons or input data (e.g. digits). Would be dope to store digit variables to control delayed shots.
* Mode "discovery" was done doing this:
    - From the few codes I had (length, level), I could see that they were in the form `c05502f1....`.
    - I scripted sending all codes from `0000` to `ffff`.
    - Through a mix of triggering a few measures at every `..ff` or by listening to responses (unreliable as the device doesn't always report data when changing modes...), I was able to detect which ranges caused a mode change.
    - Slower and more manual check in affected ranges let me figure out the exact payloads.
    - There might be modes that I haven't caught.
* Measure "discovery" was done doing this:
    - Sending a trigger signal a few times within each mode.
* DIY delayed mode:
    - `playground_delay.py` implements this.
    - Select the "wall area" mode on the device.
    - Press the trigger button to enable the laser.
    - Press the trigger button to take a shot.
    - The script hijacks the device and takes a distance/clino shot after a 3s delay.
    - It then gets back to the previous mode.
