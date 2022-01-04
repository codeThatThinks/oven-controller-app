"""Temperature profile control"""

import time


class Profile:
	"""Temperature profile"""

	def __init__(self):
		"""Create a blank profile"""

		self._steps = []
		self._i = 0
		self._target = 0
		self._last_time = 0


	def add_step(self, step):
		"""Add a step to the profile"""

		self._steps.append(step)


	def points(self, initial_temp=0):
		"""Return the points of the temperature profile for plotting"""

		points = [(0, initial_temp)]
		time = 0
		target = initial_temp

		for step in self._steps:
			if isinstance(step, RampStep):
				if step.duration is not None:
					time += step.duration
				else:
					time += abs(step.target - target) / step.rate

				target = step.target

			elif isinstance(step, HoldStep):
				time += step.duration

			points.append((time, target))

		return points


	def begin(self, initial_temp):
		"""Begin following a profile at an initial temperature"""

		self._i = 0
		self._target = initial_temp
		self._last_time = time.monotonic()
		self._steps[self._i].begin(self._target)


	def update(self):
		"""Calculate a new target temperature based on where we're at in the profile"""

		current_time = time.monotonic()
		finished, self._target = self._steps[self._i].update(current_time - self._last_time, self._target)
		self._last_time = current_time

		if finished:
			self._i += 1
			if self._i < len(self._steps):
				self._steps[self._i].begin(self._target)

		return self._target


	@property
	def step(self):
		"""Return the current step number"""

		return self._i + 1


	@property
	def num_steps(self):
		"""Return the number of steps in the profile"""

		return len(self._steps)


	@property
	def step_name(self):
		"""Return the name of the current step"""

		return self._steps[self._i].name


	@property
	def finished(self):
		"""Determine if we're at the end of the profile"""

		return self._i >= len(self._steps)


	@property
	def remaining_time(self):
		"""Return the time remaining to finish the profile"""



class ProfileStep:
	"""Base class for a profile step"""

	def __init__(self, name):
		"""Class constructor"""

		self.name = name


	def begin(self, initial_target):
		"""Empty function for step initialization"""

		pass


	def update(self, time_delta, current_target):
		"""Empty function for profile calculations"""

		return True, current_target


class RampStep(ProfileStep):
	"""Ramp to a desired temperature for a specified duration or at a specified rate"""

	def __init__(self, name, target, duration=None, rate=None):
		"""Class constructor"""

		self.target = target
		self.duration = duration
		self.rate = rate
		super().__init__(name)


	def begin(self, initial_target):
		"""Initialize step"""

		if self.duration is not None:
			self.rate = (self.target - initial_target) / self.duration

		if (self.target - initial_target) < 0 and self.rate > 0:
			self.rate = -self.rate


	def update(self, time_delta, current_target):
		"""Calculate next target temperature based on ramp"""

		new_target = current_target + (self.rate * time_delta)
		if (self.rate >= 0 and new_target >= self.target) or (self.rate < 0 and new_target <= self.target):
			return True, self.target

		return False, new_target


class HoldStep(ProfileStep):
	"""Hold the current temperature for a specified duration"""

	def __init__(self, name, duration):
		"""Class constructor"""

		self.duration = duration
		self._elapsed_time = None
		super().__init__(name)


	def begin(self, initial_target):
		"""Step initialization"""

		self._elapsed_time = 0


	def update(self, time_delta, current_target):
		"""Hold the current target until duration has elapsed"""

		self._elapsed_time += time_delta
		return self._elapsed_time >= self.duration, current_target
