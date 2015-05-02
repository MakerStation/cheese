#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
import subprocess
import os, shutil

CAMERA_TYPE = 'Canon'
LOCAL_FOLDER = '/home/pi/cheese'
PHOTO_FOLDER = '/mnt/photo'
PHOTO_EXTENSIONS = ['cr2', 'jpg']

def log (message):
	print datetime.utcnow(), message


def resetUsb (cameraType):
	process = subprocess.Popen(["lsusb"], stdout=subprocess.PIPE)
	(output, err) = process.communicate()
	exit_code = process.wait()

	for line in output.split('\n') :
		if cameraType in line:
			process = subprocess.Popen(["./usbreset", "/dev/bus/usb/%s/%s" % (line[4:7], line[15:18])], stdout=subprocess.PIPE)
			(output, err) = process.communicate()
			exit_code = process.wait()

			if exit_code != 0:
				print err


def turnOnCamera ():
	pass


def takePhoto (filename):
	command = ["gphoto2", "--force-overwrite", "--capture-image-and-download", "--filename=%s.%%C" % filename]
	result = subprocess.check_output(command)


def movePictures (filename):
	for extension in PHOTO_EXTENSIONS:
		localFile = "%s/%s.%s" % (LOCAL_FOLDER, filename, extension)
		targetFile = "%s/%s.%s" % (PHOTO_FOLDER, filename, extension)

		try:
			shutil.move(localFile, targetFile)
		except:
			if not os.path.isfile(targetFile):
				raise Exception("something went wrong copying the file")
		
		os.remove(localFile)


def cheese ():
	now = datetime.now()
	filename = now.strftime('%Y-%m-%d_%H%M%S')

	resetUsb(CAMERA_TYPE)
	turnOnCamera()
	takePhoto(filename)
	movePictures(filename)

	resetUsb(CAMERA_TYPE)


cheese ()