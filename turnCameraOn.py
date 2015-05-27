#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import subprocess
import os
import time
from datetime import datetime

def log (message):
	print datetime.utcnow(), message

def turnCameraOn ():
	log(">>> turning camera on")
	command = ["gpio", "export", "23", "out"]
	result = subprocess.check_output(command)
	command = ["gpio", "-g", "write", "23", "1"]
	result = subprocess.check_output(command)
	time.sleep(1)
	command = ["gpio", "-g", "write", "23", "0"]
	result = subprocess.check_output(command)
	log("<<< turning camera on")


def main ():
	turnCameraOn()


if __name__ == "__main__":
	main()
