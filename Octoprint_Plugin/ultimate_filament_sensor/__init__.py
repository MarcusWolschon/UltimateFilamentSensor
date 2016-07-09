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


class FilamentSensorPlugin(octoprint.plugin.StartupPlugin,
			   octoprint.plugin.SettingsPlugin,
			   octoprint.plugin.EventHandlerPlugin,
			   octoprint.plugin.TemplatePlugin,
			   octoprint.plugin.BlueprintPlugin):

	def initialize(self):
		self._logger.setLevel(logging.DEBUG)
		self._logger.info("Filament Sensor Plugin [%s] initialized..."%self._identifier)

	def on_after_startup(self):
		self.PINA_FILAMENT = self._settings.get(["pinA"])
		self.PINB_FILAMENT = self._settings.get(["pinB"])
		self.BOUNCE = self._settings.get_int(["bounce"])
                # TODO: config params for pins
                self.filament_force = filament_pulling_sensor.filament_pulling_sensor(self, 23, 24)
                self.filament_odometry = filament_odometry_sensor.filament_odometry_sensor(self, self.PINA_FILAMENT, self.PINB_FILAMENT)
		
		# DEBUGGING
                self.start_sensors()

	def get_settings_defaults(self):
		return dict(
			pinA = -1,
			pinB = -1,
			bounce = 1
		)

        def get_template_configs(self):
                return [
                        dict(type="navbar", custom_bindings=False),
                        dict(type="settings", custom_bindings=False)
                ]

	@octoprint.plugin.BlueprintPlugin.route("/status", methods=["GET"])
	def check_status(self):
		status = "-1"
		#TODO if self.PINA_FILAMENT != -1 and self.PINB_FILAMENT != -1 :
	        #		status = "1" if GPIO.input(self.PINA_FILAMENT) or GPIO.input(self.PINB_FILAMENT) else "0"
		return jsonify( status = status )
		
	def on_event(self, event, payload):
		if event == Events.PRINT_STARTED:
			self._logger.info("Printing started. Filament sensor enabled.")
			self.init_gpio()
		elif event in (Events.PRINT_DONE, Events.PRINT_FAILED, Events.PRINT_CANCELLED):
			self._logger.info("Printing stopped. Filament sensor disbaled.")
			self.stop_sensors()
			try:
				GPIO.remove_event_detect(self.PINA_FILAMENT)
				GPIO.remove_event_detect(self.PINB_FILAMENT)
			except:
				pass

	def stop_sensors(self):
		self._logger.debug("tearing down GPIO pins for rotary endoder")
                self.filament_force.stop()
                self.filament_odometry.stop()

	def start_sensors(self):
		self._logger.debug("initializing GPIO pins for rotary endoder")
                self.filament_force.start()
                self.filament_odometry.start()

        # called by plugins to inform us that an alarm criteria is met
        def on_sensor_alarm(self, cause):
                self._logger.error("[%s]. Pausing print." % cause)
                self._printer.toggle_pause_print()
                self.stop_sensors()

	def get_version(self):
		return self._plugin_version

	def get_update_information(self):
		return dict(
			ultimate_filament_sensor=dict(
				displayName="Filament Sensor",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="Marcus Wolschon",
				repo="OctoPrint-Filament",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/TODO_MoonshineSG/OctoPrint-Filament/archive/{target_version}.zip"
			)
		)

__plugin_name__ = "Ultimate Filament Sensor"
__plugin_version__ = "2.0.0"
__plugin_description__ = "Use a filament sensor to pause printing when filament runs out."

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = FilamentSensorPlugin()

