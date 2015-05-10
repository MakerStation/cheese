#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import subprocess
import os
import time
from datetime import datetime

def log (message):
	print datetime.utcnow(), message

def signalShuttingDown ():
	log(">>> signal shutting down")
	command = ["gpio", "export", "18", "out"]
	result = subprocess.check_output(command)
	command = ["gpio", "-g", "write", "18", "1"]
	result = subprocess.check_output(command)
	time.sleep(1)
	command = ["gpio", "-g", "write", "18", "0"]
	result = subprocess.check_output(command)
	log("<<< signal shutting down")


def shutdown ():
	log(">>> shutting down")
	os.system('sudo shutdown now -h')
	log("<<< shutting down")

def main ():
	signalShuttingDown()
	shutdown()


if __name__ == "__main__":
	main()
