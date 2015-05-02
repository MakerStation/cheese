#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
import subprocess
import os


CAMERA_TYPE = 'Canon'

def log (message):
	print datetime.utcnow(), message

def resetUsb (cameraType):
	import os

	log('reset usb')

	process = subprocess.Popen(["lsusb"], stdout=subprocess.PIPE)
	(output, err) = process.communicate()
	exit_code = process.wait()

	for line in output.split('\n') :
#		log('line: %s' % line)

		if cameraType in line:
#			log('- line: %s' % line)
#			log('- line fragments: %s - %s' % (line[4:7], line[15:18]))

			process = subprocess.Popen(["./usbreset", "/dev/bus/usb/%s/%s" % (line[4:7], line[15:18])], stdout=subprocess.PIPE)
			(output, err) = process.communicate()
			exit_code = process.wait()

			if exit_code != 0:
				print err


resetUsb(CAMERA_TYPE)
