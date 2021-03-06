# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import octoprint.settings
import octoprint.util

from octoprint.events import eventManager, Events
from flask import jsonify, request

import logging
import logging.handlers
import time
import sys

# for regular expression matching on gcode
import re

from . import filament_pulling_sensor
from . import filament_odometry_sensor
from . import filament_weight_sensor

###########################################################
# this is the actual OctoPrint plugin
# it makes use of the 3 sensors, starts and stops them and
# gets a callback if any of them reports an alarm
###########################################################
class FilamentSensorPlugin(octoprint.plugin.StartupPlugin,
			   octoprint.plugin.SettingsPlugin,
			   octoprint.plugin.SimpleApiPlugin,
                           octoprint.plugin.AssetPlugin,
			   octoprint.plugin.EventHandlerPlugin,
			   octoprint.plugin.TemplatePlugin):

	def initialize(self):
		self._logger.setLevel(logging.DEBUG)
		self._logger.info("Filament Sensor Plugin [%s] initialized..."%self._identifier)
                self.ALARM = ""

	def on_after_startup(self):
		settings = self._settings
                self.filament_force    = filament_pulling_sensor.filament_pulling_sensor(  self,
                                                                       settings.get(["force_pin_data"]),
                                                                       settings.get(["force_pin_clk"]),
                                                                       settings.get(["force_pin_scale"]),
                                                                       settings.get(["force_pin_reference_unit"]),
                                                                       settings.get(["force_maxforce"]),
                                                                       settings.get(["force_minforce"])
                                                                      )
                self.filament_odometry = filament_odometry_sensor.filament_odometry_sensor(self,
                                                                       settings.get(["odometry_pina"]),
                                                                       settings.get(["odometry_pinb"]),
                                                                       settings.get(["odometry_min_rpm"]),
                                                                       settings.get(["odometry_timeout"]),
                                                                       settings.get(["odometry_min_reverse"])
                                                                      )
                self.filament_weight    = filament_weight_sensor.filament_weight_sensor(  self,
                                                                       settings.get(["weight_pin_data"]),
                                                                       settings.get(["weight_pin_clk"]),
                                                                       settings.get(["weight_pin_scale"]),
                                                                       settings.get(["weight_pin_reference_unit"]),
                                                                       settings.get(["weight_minweight"])
                                                                      )
                self.filament_weight.start()

	def get_settings_defaults(self):
		return dict(
			odometry_pina = 16,
			odometry_pinb = 20,
			odometry_min_rpm = 10,
			odometry_bounce = 1,
			odometry_timeout = 5,
			odometry_min_reverse=4,
			odometry_circumfence = 0.157,
			odometry_invert = False,
                        force_pin_clk = 24,
                        force_pin_data = 23,
                        force_scale = 1000.0,
                        force_reference_unit = 92,
                        force_maxforce = 150.0,
                        force_minforce = -150.0,
                        weight_pin_clk = 15,
                        weight_pin_data = 14,
                        weight_empty = 8450000.0,
                        weight_scale = 0.000008362888542,
                        weight_minweight = -150.0,
		)

        # TemplatePlugin

        def get_template_configs(self):
                return [
                        dict(type="navbar", custom_bindings=False),
                        dict(type="settings", custom_bindings=False),
                        dict(type="sidebar", name="Filament Sensor", icon="print")
                ]

		
	def on_event(self, event, payload):
		if event == Events.PRINT_STARTED:
			self._logger.info("Printing started. Filament sensor enabled.")
			self.start_sensors()
		elif event in (Events.PRINT_DONE, Events.PRINT_FAILED, Events.PRINT_CANCELLED):
			self._logger.info("Printing stopped. Filament sensor disabaled.")
			self.stop_sensors()

        # TODO: enable the sensors only when there is any filament movement to be performed
        def on_gcode_sent(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
	        #self._logger.info("gcode=%s sent cmd=%s args=%s" % (gcode, cmd, ', '.join(args) ) )
                self.filament_movement_expected = 0
                if gcode and ( gcode == "G1" or gcode == "G0" ):
                        if gcode and gcode == "G1" and re.search("E[1-9]", cmd):
                             #self._logger.info("G1 Ex with x>0 found - filament movement expected")
                             self.filament_movement_expected = 1
			     #self._logger.info("Printing started and first G1 command happened. Filament sensor enabled.")
			     #self.start_sensors()
                        else:
                             #self._logger.info("G1 Ex with x<=0 found - NO filament movement expected")
                             self.filament_movement_expected = 0
                elif gcode and gcode == "M104":
			if "S0" in cmd :
                                 self.filament_movement_expected = 0
                                 self._logger.info("M104 S0 found - we are done printing")
			         #self.stop_sensors()
                                 return
                elif gcode and (gcode == "M105" or gcode == "G90" ):
                        #ignored
                        return
                else:
	                self._logger.info("unknown gcode=%s sent cmd=%s args=%s - NOT EXPECTING FILAMENT MOVEMENT" % (gcode, cmd, ', '.join(args) ) )
                        self.filament_movement_expected = 0

                if self.filament_movement_expected == 1 :
			self._logger.info("filament movement expected")
			#self._logger.info("Printing started and first G1 command happened. Filament sensor enabled.")
			#self.start_sensors()
                else:	
			self._logger.info("NO filament movement expected")

        def stop_sensors(self):
		self._logger.debug("stopping filament sensors")
                self.filament_force.stop()
                self.filament_odometry.stop()

	def start_sensors(self):
		self._logger.debug("starting filament sensors")
                self.ALARM = ""
                self.filament_force.start()
                self.filament_odometry.start()

        # called by plugins to inform us that an alarm criteria is met
        # it is safe to call this method multiple times
        def on_sensor_alarm(self, cause):
                self.ALARM = cause
                if self._printer.is_printing() and self.filament_movement_expected :
                   self._logger.error("[%s]. Pausing print." % cause)
                   self._printer.toggle_pause_print()
                   self.stop_sensors()
                   self.on_sensor_update()
                else :
                   self._logger.info("[%s]. NOT Pausing print because we are not printing or not expecting a filament movement." % cause)

        def on_sensor_update(self):
	    settings = self._settings
            self._plugin_manager.send_plugin_message(self._identifier, 
                     dict(
                        alarm=self.ALARM,
                        force=self.filament_force.last_reading,
                        weightraw=self.filament_weight.last_reading,
                        weight= "{:10.2f}".format( (float(self.filament_weight.last_reading) - float(settings.get(["weight_empty"]))) * float(settings.get(["weight_scale"]))),
                        weight_min=settings.get(["weight_minweight"]),
                        force_min=settings.get(["force_minforce"]),
                        force_max=settings.get(["force_maxforce"]),
                        odometry= "{:10.3f}".format( float(settings.get(["odometry_circumfence"])) * self.filament_odometry.accumulated_movement / (4.0*24.0) )
                ))

	def get_version(self):
		return self._plugin_version

	def get_update_information(self):
		return dict(
			ultimate_filament_sensor=dict(
				displayName="Ultimate Filament Sensor",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="Marcus Wolschon",
				repo="UltimateFilamentSensor",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/MarcusWolschon/UltimateFilamentSensor/archive/{target_version}.zip"
			)
		)
        # AssetPlugin

        def get_assets(self):
            return {
                "js": ["js/filament_sensor.js"]
            }

        # SimpleApiPlugin

        def on_api_get(self, request):
	    settings = self._settings
            return jsonify(dict(
                alarm=self.ALARM,
                weightraw=self.filament_weight.last_reading,
                weight=(self.filament_weight.last_reading - float(settings.get(["weight_empty"]))) * float(settings.get(["weight_scale"])),
                force=self.filament_force.last_reading,
                force_min=settings.get(["force_minforce"]),
                force_max=settings.get(["force_maxforce"]),
                odometry= float(settings.get(["odometry_circumfence"])) * self.filament_odometry.accumulated_movement / 24.0
            ))

__plugin_name__ = "Ultimate Filament Sensor"
__plugin_version__ = "2.0.0"
__plugin_description__ = "Use a filament sensor to pause printing when filament runs out."

def __plugin_load__():
   global __plugin_implementation__
   __plugin_implementation__ = FilamentSensorPlugin()
   global __plugin_hooks__
   __plugin_hooks__ = {
         "octoprint.comm.protocol.gcode.sent": __plugin_implementation__.on_gcode_sent
    }
