"""Oven Controller app entrypoint"""

import logging
import multiprocessing
import sys
import time
import control, gui


logger = logging.getLogger(__name__)


if __name__ == "__main__":
	# run the entire app for real
	logging.basicConfig(level=logging.DEBUG)

	with multiprocessing.Manager() as manager:
		exit = manager.Event()

		# - check if eeprom is mounted
		# - read eeprom contents
		# - validate eeprom data
		# - parse eeprom data

		# - read cli arguments
		# - merge cli arguments and eeprom settings
		# - set global app settings

		p_control = multiprocessing.Process(target=control.main, args=(exit))
		p_control.start()

		p_gui = multiprocessing.Process(target=gui.main, args=(exit, sys.argv))
		p_gui.start()

		# if enabled, spawn web ui process

		# if any process exits, shutdown other processes
		while(True):
			if not p_control.is_alive() or not p_gui.is_alive():
				logger.info("Detected one or more processes has exited. Shutting down remaining processes...")
				exit.set()
				break

			time.sleep(0.1)

		p_control.join()
		p_gui.join()

	sys.exit(0)
