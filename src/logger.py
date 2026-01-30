class Logger(object):

	def __init__(self):
		pass

	def start(self, msg: str):
		print(msg + "...", end="", flush=True)

	def finish_ok(self, msg: str):
		print(f"\r{msg}: \u2705")

	def finish_error(self, msg: str):
		print(f"\r{msg}: \u274C")
