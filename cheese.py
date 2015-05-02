#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
import subprocess
#from subprocess import Popen, PIPE

import os
#import piggyphoto


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


def turnOnCamera ():
	pass


def takePhoto ():
	now = datetime.now()
	dateformat = now.strftime('%Y-%m-%d_%H%M%S')
	filename = "%s.%%C" % dateformat
	
	log("date format: %s" % dateformat)
	log("file name: %s" % filename)
#	"--set-config", "capturetarget=0", 
	command = ["gphoto2", "--force-overwrite", "--capture-image-and-download", "--filename=%s" % filename]
	
	result = subprocess.check_output(command)
#	process = subprocess.Popen(command, stdout=subprocess.PIPE)
#	(output, err) = process.communicate()
#	exit_code = process.wait()
	log(result)
	

# context = gp.Context()
# camera = gp.Camera()
# camera.init(context)
# text = camera.get_summary(context)
# print('Summary')
# print('=======')
# print(str(text))
# camera.exit(context)
#

resetUsb(CAMERA_TYPE)
turnOnCamera()
takePhoto()
resetUsb(CAMERA_TYPE)


#camera = piggyphoto.camera()
#print camera.abilities
#C.capture_preview('preview.jpg')
#C.capture_image('image.jpg')