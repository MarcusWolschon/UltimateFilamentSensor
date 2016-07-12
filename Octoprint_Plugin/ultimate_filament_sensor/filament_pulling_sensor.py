import time
import thread
import logging
import logging.handlers
from . import hx711

class filament_pulling_sensor:
    def __init__(self, plugin, pin_DATA, pin_SCK, scale=1000, reference_unit=92, max=5.0, min=-1.0, gain=128):
        self._logger = plugin._logger
        self._plugin = plugin
        self._logger.debug("Filament Sensor Plugin - pulling force sensor - DATA pin: %s"  % pin_DATA)  
        self._logger.debug("Filament Sensor Plugin - pulling force sensor - SCK  pin: %s"  % pin_SCK)  
        self._logger.debug("Filament Sensor Plugin - pulling force sensor - scale: %s"  % scale)  
        self._logger.debug("Filament Sensor Plugin - pulling force sensor - reference_unit: %s"  % reference_unit)  
        self._logger.debug("Filament Sensor Plugin - pulling force sensor - min: %s"  % min)  
        self._logger.debug("Filament Sensor Plugin - pulling force sensor - max: %s"  % max)  

        if scale == None : scale = 1000
        if reference_unit == None : reference_unit = 92

        self.max = max
        self.last_reading = -1
        self.min = min
        self.sensor = hx711.HX711(pin_DATA, pin_SCK, gain)
        self.sensor.set_scale(scale)
        self.sensor.set_reference_unit(reference_unit)
        self.sensor.power_down()
        self.looper = None

    def start(self):
        self._logger.info("Filament Sensor Plugin - pulling force sensor - starting")  
        self.sensor.power_up()
        self.sensor.tare()
        self.stop_looper = 0
        self.looper = thread.start_new_thread(self.on_loop, () );

    def stop(self):
        self._logger.info("Filament Sensor Plugin - pulling force sensor - stopping")  
        self.stop_looper = 1
        if self.looper is None and self.looper.isAlive() :
           self.looper.join()
        self.sensor.power_down()

    def on_loop(self):
        self._logger.info("Filament Sensor Plugin - pulling force sensor - looper started")  
        while self.stop_looper == 0  :
           self.last_reading = self.sensor.get_weight(1) 
           self._logger.info("Filament Sensor Plugin - pulling force [%s]"%force)  
           #TODO: always triggers if self.last_reading >= self.max :
           #    self._plugin.on_sensor_alarm("excessive filament pulling force [%s > %s] detected" % (force, self.max))
           #TODO: always triggers if self.last_reading < self.min :
           #    self._plugin.on_sensor_alarm("loss of filament pulling force [%s < %s] detected" % (force, self.min))
           time.sleep(0.5)  # sleep 0.5 seconds  
        self._logger.info("Filament Sensor Plugin - pulling force sensor - looper stopped")  
