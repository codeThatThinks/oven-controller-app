"""Buzzer soft PWM process"""

import multiprocessing
import time

import gpio


QUEUE_SIZE = 16

class Buzzer:
	"""Buzzer soft-PWM"""

	def __init__(self, pin, freq):
		"""Class constructor"""

		self.pin = pin
		self.freq = freq

		gpio.setup(pin, gpio.OUT)

		self.queue = multiprocessing.Queue(QUEUE_SIZE)
		self.process = multiprocessing.Process(target=self._process, args=(pin, freq, self.queue,))
		self.process.start()


	def beep(duration):
		"""Add a beep to the buzzer queue"""

		self.queue.put(duration)


	def pause(duration):
		"""Add a pause to the buzzer queue"""

		self.queue.put(-duration)


	def cleanup(self):
		"""Cleanup"""

		self.queue.close()
		self.process.terminate()
		gpio.cleanup(self.pin)


	def _process(self, pin, freq, queue):
		"""Buzzer process"""

		beep_delay = 1 / freq / 2

		while(True):
			duration = queue.get()

			if duration > 0:
				# beep
				start_time = time.time()

				while(time.time() < (start_time + duration)):
					gpio.write(pin, gpio.HIGH)
					time.sleep(beep_delay)
					gpio.write(pin, gpio.LOW)
					time.sleep(beep_delay)

			elif duration < 0:
				# pause
				time.sleep(-duration)
