#!/usr/bin/env python3
from shutil import rmtree
from os import remove

to_remove = ["./debug.log", "./__pycache__", "./results", "./logs"]

for i in to_remove:
	try:
		rmtree(i)
	except FileNotFoundError:
		pass
	except NotADirectoryError:
		remove(i)