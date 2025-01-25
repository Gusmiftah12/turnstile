import threading
import time


class Debouncer:
	def __init__(self, delay_seconds):
		self.delay = delay_seconds
		self.lock = threading.Lock()
		self.condition = threading.Condition(self.lock)
		self.last_call_time = None
		self._expired = False
		self._active = True

	def call(self):
		"""Returns True if call was accepted, False if debouncer is expired"""
		with self.lock:
			if not self._active:
				return False
			self.last_call_time = time.time()
			self.condition.notify_all()
			return True

	def wait(self):
		"""Blocks until debounce period passes, marks as expired"""
		with self.lock:
			while self._active:
				if self.last_call_time is None:
					self.condition.wait()
				else:
					elapsed = time.time() - self.last_call_time
					if elapsed >= self.delay:
						break
					self.condition.wait(self.delay - elapsed)
			self._expired = True
			self._active = False

	def stop(self):
		"""Force stop the debouncer"""
		with self.lock:
			self._active = False
			self.condition.notify_all()

	@property
	def active(self):
		with self.lock:
			return self._active
