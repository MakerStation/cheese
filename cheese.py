#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
import subprocess
import os, shutil
import keen


CAMERA_TYPE = 'Canon'
LOCAL_FOLDER = '/home/pi/cheese'
PHOTO_FOLDER = '/media/photo'
PHOTO_EXTENSIONS = ['cr2', 'jpg']
S3_BUCKET = "timelapse"


keen.project_id = ''
keen.write_key  = ''


def log (message):
	print datetime.utcnow(), message


def resetUsb (cameraType):
	log(">>> reset USB")
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
	log("<<< reset USB")


def turnCameraOn ():
	pass


def takePhoto (filename):
	log(">>> take photo")
	command = ["gphoto2", "--force-overwrite", "--capture-image-and-download", "--filename=%s.%%C" % filename]
	result = subprocess.check_output(command)
	log("<<< take photo")


def movePictures (filename):
	import traceback

	log(">>> move pictures")
	for extension in PHOTO_EXTENSIONS:
		log("-- extension: %s" % extension)
		localFile = "%s/%s.%s" % (LOCAL_FOLDER, filename, extension)
		log("-- local file: %s" % localFile)
		targetFile = "%s/%s.%s" % (PHOTO_FOLDER, filename, extension)
		log("-- target file: %s" % targetFile)

		try:
			log("-> copying ...")
			shutil.copy(localFile, targetFile)
			log("<- copying - DONE")
		except Exception as e:
			log("exception: %s", str(e))
			pass

		if os.path.isfile(targetFile):
			log("-> removing local file ...")
			os.remove(localFile)
			log("<- removing local file - DONE")
		else:
			raise Exception("something went wrong copying the file")
	log("<<< move pictures")


def sendThumbnailToS3 (filename):
	from boto.s3.connection import S3Connection
	from boto.s3.key import Key
	
	file = "%s/%s.%s" % (LOCAL_FOLDER, filename, "jpg")
	
	connection = S3Connection()
	bucket = connection.get_bucket(S3_BUCKET)
	snapshot = Key(bucket)
	snapshot.key = "%s.jpg" % filename
	snapshot.set_contents_from_filename(file)


def sendThumbnailViaHttpPost (filename):
	pass


def sendThumbnail (filename):
	log(">>> send thumbnail")
	sendThumbnailViaHttpPost(filename)
	log("<<< send thumbnail")


def connectGPRS ():
	log(">>> connect GPRS")
	process = subprocess.Popen(["sudo", "sakis3g", "connect", "USBMODEM=\"12d1:1001\"", "APN=\"ibox.tim.it\""], stdout=subprocess.PIPE)
	(output, err) = process.communicate()
	exit_code = process.wait()

	if exit_code != 0:
		raise Exception("something went wrong setting up GPRS connection")
	log("<<< connect GPRS")


def disconnectGPRS ():
	log(">>> disconnect GPRS")
	process = subprocess.Popen(["sudo", "sakis3g", "disconnect"], stdout=subprocess.PIPE)
	(output, err) = process.communicate()
	exit_code = process.wait()

	if exit_code != 0:
		raise Exception("something went wrong closing the GPRS connection")
	log("<<< disconnect GPRS")


def readLineFromSerialPort ():
	#	http://www.texnological.blogspot.it/2014/03/raspberry-pi-read-data-from-usb-serial.html
	return "Ore 14:55:23 Volts 13.50 Temp. 22.00"


def collectStats (filename):
	log(">>> collect stats")
	statInfo = readLineFromSerialPort()

	temperature = 10.5
	batteryLevel = 95
	dateTime = "2015-05-03_144844"
	
	rawSize = 20449214
	jpgSize = 3629065
	
	stats = {
		"environment": [ {
			"temperature": temperature,
			"batteryLevel": batteryLevel,
			"dateTime": dateTime
		} ],
		"image": [ {
			"name":    filename,
			"rawSize": rawSize,
			"jpgSize": jpgSize
		} ]
	}
	log("<<< collect stats")
	
	return stats


def sendStats (stats):
#	https://github.com/keenlabs/KeenClient-Python

#	from keen.client import KeenClient
#	client = KeenClient(project_id="xxxx", write_key="yyyy")
#	keen.add_event("sign_ups", {"username": "lloyd", "referred_by": "harry"})
	log(">>> send stats")
	keen.add_events(stats)
	log("<<< send stats")


def signalShuttingDown ():
	log(">>> signal shutting down")
	pass
	log("<<< signal shutting down")


def shutdown ():
	log(">>> shutting down")
	os.system('sudo shutdown now -h')
	log("<<< shutting down")


def cheese (filename):
#	turnCameraOn()
	takePhoto(filename)
	movePictures(filename)
	connectGPRS()
	sendThumbnail(filename)
	sendStats(collectStats(filename))
	disconnectGPRS()
	signalShuttingDown()
	shutdown()


def main ():
	now = datetime.now()
	filename = now.strftime('%Y-%m-%d_%H%M%S')

	resetUsb(CAMERA_TYPE)
	cheese (filename)
	resetUsb(CAMERA_TYPE)


if __name__ == "__main__":
	main()
