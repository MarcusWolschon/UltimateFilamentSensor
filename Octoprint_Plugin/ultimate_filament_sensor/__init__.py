# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import octoprint.settings
import octoprint.util

from octoprint.events import eventManager, Events
from flask import jsonify, request

import logging
import logging.handlers
import RPi.GPIO as GPIO
import time
import sys

from . import filament_pulling_sensor
from . import filament_odometry_sensor

###########################################################
# this is the actual OctoPrint plugin
# it makes use of the 3 sensors, starts and stops them and
# gets a callback if any of them reports an alarm
###########################################################
class FilamentSensorPlugin(octoprint.plugin.StartupPlugin,
			   octoprint.plugin.SettingsPlugin,
			   octoprint.plugin.EventHandlerPlugin,
			   octoprint.plugin.TemplatePlugin,
			   octoprint.plugin.BlueprintPlugin):

	def initialize(self):
		self._logger.setLevel(logging.DEBUG)
		self._logger.info("Filament Sensor Plugin [%s] initialized..."%self._identifier)

	def on_after_startup(self):
		settings = self._settings
                self.filament_force    = filament_pulling_sensor.filament_pulling_sensor(  self,
                                                                       settings.get(["force_pin_data"]),
                                                                       settings.get(["force_pin_clk"]),
                                                                       settings.get(["force_pin_scale"]),
                                                                       settings.get(["force_pin_reference_unit"]),
                                                                       settings.get(["force_pin_max_force"]),
                                                                       settings.get(["force_pin_min_force"])
                                                                      )
                self.filament_odometry = filament_odometry_sensor.filament_odometry_sensor(self,
                                                                       settings.get(["odometry_pina"]),
                                                                       settings.get(["odometry_pinb"])
                                                                      )
		# DEBUGGING
                self.start_sensors()

	def get_settings_defaults(self):
		return dict(
			odometry_pina = 16,
			odometry_pinb = 20,
			odometry_bounce = 1,
			odometry_timeout = 5,
			odometry_invere = False,
                        force_pin_clk = 24,
                        force_pin_data = 23,
                        force_scale = 1000.0,
                        force_reference_unit = 92,
                        force_maxforce = 5.0,
                        force_minforce = -0.5,
                        weight_pin_clk = 25,
                        weight_pin_data = 8
		)
#        def get_template_vars(self):
#                # TODO more
#                return dict(
#                     odometry_pina=self._settings.get(["odometry_pina"])
#               )

        def get_template_configs(self):
                return [
                        dict(type="navbar", custom_bindings=False),
                        dict(type="settings", custom_bindings=False)
                ]

	@octoprint.plugin.BlueprintPlugin.route("/status", methods=["GET"])
	def check_status(self):
		status = "-1"
		#TODO get status from plugins
		return jsonify( status = status )
		
	def on_event(self, event, payload):
		if event == Events.PRINT_STARTED:
			self._logger.info("Printing started. Filament sensor enabled.")
			self.init_gpio()
		elif event in (Events.PRINT_DONE, Events.PRINT_FAILED, Events.PRINT_CANCELLED):
			self._logger.info("Printing stopped. Filament sensor disabaled.")
			self.stop_sensors()

	def stop_sensors(self):
		self._logger.debug("stopping filament sensors")
                self.filament_force.stop()
                self.filament_odometry.stop()

	def start_sensors(self):
		self._logger.debug("starting filament sensors")
                self.filament_force.start()
                self.filament_odometry.start()

        # called by plugins to inform us that an alarm criteria is met
        def on_sensor_alarm(self, cause):
                #TODO debugging if self._printer.is_printing() :
                self._logger.error("[%s]. Pausing print." % cause)
                self._printer.toggle_pause_print()
                self.stop_sensors()

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

__plugin_name__ = "Ultimate Filament Sensor"
__plugin_version__ = "2.0.0"
__plugin_description__ = "Use a filament sensor to pause printing when filament runs out."

#def __plugin_load__():
#	global __plugin_implementation__
__plugin_implementation__ = FilamentSensorPlugin()

