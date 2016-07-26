# -*- coding:utf-8 -*-
import datetime
import time
import sys
import os
import trace

stdout = sys.stdout
sys.stdout = open(os.devnull, "w")

logout = open("log.txt", "w")

datetime_format = "%Y-%m-%d %H:%M:%S"

def to_gbk(s):
	return s.decode("utf-8").encode("gbk")

def to_utf8(s):
	return s.decode("gbk").encode("utf-8")

def format_input(fun):
	def wrapper(self, format, *argv, **kwargs):
		msg = self._format_output(format, *argv, **kwargs)
		fun(self, msg)
	return wrapper

def print_to_stdout(*argv):
	msgs = []
	for s in argv:
		msgs.append(to_gbk(s))
	print >> stdout, datetime.datetime.fromtimestamp(time.time()).strftime(datetime_format), ", ".join(map(str, msgs))
	#print >> logout, datetime.datetime.fromtimestamp(time.time()).strftime(datetime_format), ", ".join(map(str, argv))

class Logger(object):
	"""
	"""
	logger_cache = {}
	busy_count = 0

	def __init__(self, tag = "", name = ""):
		"""
		"""

	def _format_output(self, format, *argv):
		"""
		"""
		msg = format
		try:
			if argv and "%" in format:
				msg = format % argv
			else:
				msg = format
		except:
			print_to_stdout("-----Log 格式出错--------")
			print_to_stdout(format)
			print_to_stdout(str(argv))
			print_to_stdout("-------------")
		return msg

	@format_input
	def info(self, msg):
		"""
		"""
		print_to_stdout("INFO: " + msg)

	@format_input
	def debug(self, msg):
		"""
		"""
		print_to_stdout("DEBUG: " + msg)

	@format_input
	def warning(self, msg):
		"""
		"""
		print_to_stdout("WARNING: " + msg)
		return

	@format_input
	def error(self, msg):
		"""
		"""
		print_to_stdout("ERROR: " + msg)
		return

	def log_file(self, msg):
		#print >> logout, msg,
		pass

logger = Logger()