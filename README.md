

Purpose:

3D printing filament sensor meassuring serveral aspects to pause prints before they fail.
- Pause print by observing a rotary encoder meassuring filament movement (lack of movement or wrong direction).
- Also pause by ovserving a load cell meassuring extruder pulling force on the filament (too much or sudden loss of force).
- Also observe another load cell meassuring how much weight of filament is left on the spool and warn if it's not enough.

License: AGPL 3.0

Status: WORK IN PROGRESS - unfinished (software stable, documentation in progress, hardware being cleaned up for release)

# Attribution:

This plugin is based on https://github.com/MoonshineSG/OctoPrint-Filament (AGPL 3.0 license)
The Hx711 code is based on https://github.com/tatobari/hx711py/ (Apache 2.0 license)
Licenses are deemed compatible: http://www.apache.org/licenses/GPL-compatibility.html

# Hardware:

The hardware is currently being developed here:
http://marcuswolschon.blogspot.de/2016/06/ultimaker-ii-filament-sensor-and-remote.html

# Installation:
```
 /home/pi/oprint/bin/pip install --upgrade pip
 /home/pi/oprint/bin/pip install numpy
 sudo chmod a+rw /dev/gpiomem
 /home/pi/oprint/local/bin/python setup.py install && sudo /etc/init.d/octoprint restart && tail -f /home/pi/.octoprint/logs/octoprint.log
```
alternative for development (no reinstall on every change of the source code):
```
 /home/pi/oprint/local/bin/python setup.py develop && sudo /etc/init.d/octoprint restart && tail -f /home/pi/.octoprint/logs/octoprint.log
```

Settings are in the Octoprint Settings menu.
Pins are in BCM numbering.
- odometry_pina - first pins for the rotary encoder, meassuring filament movement.
- odometry_pinb - second pins for the rotary encoder, meassuring filament movement.
- odometry_min_rpm - the filament wheel must have turned this many times before the odometry sensor will ever generate an alarm
- odometry_min_reverse - the filament wheel must have turned this many in reverse times before the odometry sensor will pause the print
- odometry_timeout - if no movement is detected for this many seconds, pause the print
- odometry_circumfence - circumfence of the filament wheel on the rotary encoder in meter
- center pin of the rotary encoder is connected to GND, pina and pinb are pulled up by the Raspberry Pi
- odometry_bound - time in milliseconds to debounce the odometry pins
- odometry_inverse - inverse the detected direction of the rotary encoder. Reverse movement is a cause to pause the print. ("False" or "1")
- force_pin_clk - CLK pin of the Hx711 board for the load cell meassuring the filament pulling force
- force_pin_data - DATA pin of the Hx711 board for the load cell meassuring the filament pulling force
- force_maxforce - exceeding this value (after scale and unit are applied) is considered excessive force and pauses the print
- force_minforce - less then this value (after scale and unit are applied) is considered a (sudden) loss of pulling force and pauses the print
- weight_pin_clk - CLK pin of the Hx711 board for the load cell meassuring the (remaining) weight of the filament spool
- weight_pin_data - DATA pin of the Hx711 board for the load cell meassuring the (remaining) weight of the filament spool

# API
(work in progress)
An API is available to check the filament sensor status via a GET method to `/plugin/filament/status` which returns a JSON

Note: Needs RPi.GPIO version greater than 0.6.0 to allow access to GPIO for non root and `chmod a+rw /dev/gpiomem`.
This requires a fairly up to date system.

