#!/usr/bin/env python3
from shutil import rmtree

to_remove = ["./__pycache__", "./results", "./logs"]

for i in to_remove:
	try:
		rmtree(i)
	except FileNotFoundError:
		pass
