To do:

Ideas:
* Necessary: delay setting: to emulate e.g. 4s delay (like on the Disto X2), a distinct mode with laser will be enabled, e.g. distance (no angle, just distance). User will trigger a measurement on the Bosch LRF. The ESP32 will catch the response and reliably see that it's only a distance: that will be the trigger for a 4s delayed shot: the ESP32 willenable distance+angle and make sure laser is on, sleep 4s, take the measurement. After measurement, the ESP32 will switch back to distance-only mode. This way we can mostly use the default Bosch LRF buttons for common operations.
* Middle prio: calibration should be able to be performed. Completely separate from Topodroid, or using Topodroid's way + Topodroid corrections?

Not very important:
* Enable/disable laser (or just... take a measurement? that will toggle the laser).
* Figure out if there is a better way than "bruteforce" in order to access all modes.
* Possibly figure out how to configure front/camera mount/back setting.
* Possibly figure out how to configure sub-modes (probably not very important).
