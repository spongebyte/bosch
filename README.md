<<<<<<< Updated upstream
To do:

Ideas:
* Necessary: delay setting: to emulate e.g. 4s delay (like on the Disto X2), a distinct mode with laser will be enabled, e.g. distance (no angle, just distance). User will trigger a measurement on the Bosch LRF. The ESP32 will catch the response and reliably see that it's only a distance: that will be the trigger for a 4s delayed shot: the ESP32 will enable distance+angle and make sure laser is on, sleep 4s, take the measurement. After measurement, the ESP32 will switch back to distance-only mode. This way we can mostly use the default Bosch LRF buttons for common operations.
* Following the previous "mode hijacking" philosophy, other modes could be used to trigger special modes: calibration, delay setting.
* Avoid companion app. Avoid LCD screen. Keep things minimal. A simple small/discrete RGB LED could suffice: standby in distance mode (G), doing stuff (R), data present (blinking with number of shots in queue?).
* Middle prio: calibration should be able to be performed. Completely separate from Topodroid, or using Topodroid's way + Topodroid corrections?

Not very important:
* Enable/disable laser (or just... take a measurement? that will toggle the laser).
* Figure out if there is a better way than "bruteforce" in order to access all modes.
* Possibly figure out how to configure front/camera mount/back setting.
* Possibly figure out how to configure sub-modes (probably not very important).
=======
* Plenty of "reboot" payload codes. No idea what they're supposed to do.
* For some reason, some modes can be reahced from different payload codes. Not sure why.
* Some menus can be accessed, so I guess that there might be a way to key in buttons or input data (e.g. digits). Would be dope to store digit variables to control delayed shots.
* Mode "discovery" was done doing this:
    - From the few codes I had (length, level), I could see that they were in the form `c05502f1....`.
    - I scripted sending all codes from `0000` to `ffff`.
    - Through a mix of triggering a few measures at every `..ff` or by listening to responses (unreliable as the device doesn't always report data when changing modes...), I was able to detect which ranges caused a mode change.
    - Slower and more manual check in affected ranges let me figure out the exact payloads.
* Measure "discovery" was done doing this:
    - Sending a trigger signal a few times within each mode.
* DIY delayed mode:
    - `playground_delay.py` implements this.
    - Enable `wall_area` mode on the device.
    - Press the trigger button to enable the laser.
    - Press the trigger button to take a shot.
    - The script hijacks the device and takes a distance/clino shot after a 3s delay.
    - It then gets back to the previous mode.
>>>>>>> Stashed changes
