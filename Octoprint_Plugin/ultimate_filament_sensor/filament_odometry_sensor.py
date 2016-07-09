import time
import thread
import logging
import logging.handlers
import RPi.GPIO as GPIO

class filament_odometry_sensor:
    def __init__(self, plugin, pin_A, pin_B):
        self._logger = plugin._logger
        self._plugin = plugin
        self.looper = None
        self.PINA_FILAMENT = pin_A
        self.PINB_FILAMENT = pin_B
        self.BOUNCE = 1
        self.TIMEOUT = 5
        self._logger.info("Running RPi.GPIO version '{0}'...".format(GPIO.VERSION))
        if GPIO.VERSION < "0.6":
           raise Exception("RPi.GPIO must be greater than 0.6")
        GPIO.setmode(GPIO.BCM)
        #GPIO.setwarnings(False)
        self._logger.info("RPi.GPIO set up for BCM mode")
        self._logger.info("Filament Sensor Plugin setup to use GPIO BCM [%s] and BCM [%s] for rotary encoder..." % ( pin_A, pin_B ))

    def start(self):
        self._logger.info("Filament Sensor Plugin - pulling odometry sensor - starting")  
        GPIO.setup(self.PINA_FILAMENT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.PINB_FILAMENT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.last_position = 9
        self.last_meassurement = time.clock()
        if self.PINA_FILAMENT != -1:
           GPIO.add_event_detect(self.PINA_FILAMENT, GPIO.BOTH, callback=self.on_gpio_event, bouncetime=self.BOUNCE)
        if self.PINB_FILAMENT != -1:
           GPIO.add_event_detect(self.PINB_FILAMENT, GPIO.BOTH, callback=self.on_gpio_event, bouncetime=self.BOUNCE)
        self.stop_looper = 0
        self.looper = thread.start_new_thread(self.on_loop, () );

    def stop(self):
        self._logger.info("Filament Sensor Plugin - pulling odometry sensor - stopping")  
        self.stop_looper = 1
        if self.looper is None and self.looper.isAlive() :
           self.looper.join()
        try:
             GPIO.remove_event_detect(self.PINA_FILAMENT)
        except:
             pass
        try:
             GPIO.remove_event_detect(self.PINB_FILAMENT)
        except:
             pass

    def on_loop(self):
        self._logger.info("Filament Sensor Plugin - pulling odometry sensor - looper started")  
        while self.stop_looper == 0  :
           now = time.clock()
           difference = (self.TIMEOUT + self.last_meassurement) - now
           if difference < 0 :
              self._logger.error("Filament Sensor Plugin - pulling odometry sensor - TIMEOUT DETECTED! NO FILAMENT MOVEMENT")  
              self._plugin.on_sensor_alarm("no filament movement detected within [%s]ms" % self.TIMEOUT)
              return
           time.sleep(difference)   
        self._logger.info("Filament Sensor Plugin - pulling odometry sensor - looper stopped")  

    # the value of one of the GPIO pins for the
    # rotary encoder changed.
    # Calculate how much the filament has moved
    # Pause the print if it has moved in reverse
    def on_gpio_event(self, channel):
           stateA = GPIO.input(self.PINA_FILAMENT)
           stateB = GPIO.input(self.PINB_FILAMENT)

           # convert grey code to binary
           msb = stateA
           lsb = stateA ^ stateB
           position = (msb <<1) + lsb


           self._logger.debug("Detected event on GPIO [%s] inputs: [%s]-[%s] position: [%s]? !"%(channel, stateA, stateB, position))

           # we have no last position => can't calculate and movement
           if self.last_position == 9 :
              self.last_position = position
              return

           # calculate movement. Handle rollover from 3 to 0
           movement = position - self.last_position
           if movement < -2 :
              movement = 4 + movement

           self.last_position = position
           self.last_meassurement = time.clock()

           if movement < 0 :
              self._logger.warn("Reverse filament movement detected.")
              if self._printer.is_printing() :
                 self._plugin.on_sensor_alarm("reverse movement detected")

