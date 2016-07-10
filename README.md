

Purpose:

3D printing filament sensor meassuring serveral aspects to pause prints before they fail.
- Pause print by observing a rotary encoder meassuring filament movement (lack of movement or wrong direction).
- Also pause by ovserving a load cell meassuring extruder pulling force on the filament (too much or sudden loss of force).
- Also observe another load cell meassuring how much weight of filament is left on the spool and warn if it's not enough.

License: AGPL 3.0

Status: WORK IN PROGRESS - unfinished

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
 sudo /home/pi/oprint/local/bin/python setup.py install && sudo /etc/init.d/octoprint restart && tail -f /home/pi/.octoprint/logs/octoprint.log
```
alternative for development (no reinstall on every change of the source code):
```
 sudo /home/pi/oprint/local/bin/python setup.py develop && sudo /etc/init.d/octoprint restart && tail -f /home/pi/.octoprint/logs/octoprint.log
```

Then add the following needs to be added to the config.yaml:

```
plugins:
...
  ultimate_filament_sensor:
     odometry_pina : 16
     odometry_pinb : 20
     odometry_bounce : 1
     odometry_timeout : 5
     odometry_invere : False
     force_pin_clk : 24
     force_pin_data : 23
     force_scale : 1000
     force_reference_unit : 92
     force_maxforce : 5.0
     force_minforce : -0.5
     weight_pin_clk : 25
     weight_pin_data : 8
     weight_scale : 1000
     weight_reference_unit : 92
```
(work in progress)
Pins are in BCM numbering.
- odometry_pina - first pins for the rotary encoder, meassuring filament movement.
- odometry_pinb - second pins for the rotary encoder, meassuring filament movement.
- center pin of the rotary encoder is connected to GND, pina and pinb are pulled up by the Raspberry Pi
- odometry_bound - time in milliseconds to debounce the odometry pins
- odometry_inverse - inverse the detected direction of the rotary encoder. Reverse movement is a cause to pause the print. ("False" or "1")
- force_pin_clk - CLK pin of the Hx711 board for the load cell meassuring the filament pulling force
- force_pin_data - DATA pin of the Hx711 board for the load cell meassuring the filament pulling force
- force_scale - 
- force_reference_unit - 
- force_maxforce - exceeding this value (after scale and unit are applied) is considered excessive force and pauses the print
- force_minforce - less then this value (after scale and unit are applied) is considered a (sudden) loss of pulling force and pauses the print
- weight_pin_clk - CLK pin of the Hx711 board for the load cell meassuring the (remaining) weight of the filament spool
- weight_pin_data - DATA pin of the Hx711 board for the load cell meassuring the (remaining) weight of the filament spool
- weight_scale - 
- weight_reference_unit - 

# API
(work in progress)
An API is available to check the filament sensor status via a GET method to `/plugin/filament/status` which returns a JSON

- `{status: "-1"}` if the sensor is not setup
- `{status: "0"}` if the sensor is OFF (filament not present)
- `{status: "1"}` if the sensor is ON (filament present)

The status 0/1 depends on the type of sensor, and it might be reversed if using a normally closed switch.

A build using an optical switch can be found at http://www.thingiverse.com/thing:1646220

Note: Needs RPi.GPIO version greater than 0.6.0 to allow access to GPIO for non root and `chmod a+rw /dev/gpiomem`.
This requires a fairly up to date system.

