import time
import thread
import logging
import logging.handlers
from . import hx711

class filament_pulling_sensor:
    def __init__(self, plugin, pin_DATA, pin_SCK, gain=128):
        self._logger = plugin._logger
        self._plugin = plugin
        self.sensor = hx711.HX711(pin_DATA, pin_SCK, gain)
        self.sensor.set_scale(1000)
        self.sensor.set_reference_unit(92)
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
           force = self.sensor.get_weight(1) 
           self._logger.info("Filament Sensor Plugin - pulling force [%s]"%force)  
           #TODO: always triggers if force >= 100.0 :
           #    self._plugin.on_sensor_alarm("excessive filament pulling force [%s > 5.0] detected" % force)
        time.sleep(0.5)   
        self._logger.info("Filament Sensor Plugin - pulling force sensor - looper stopped")  
