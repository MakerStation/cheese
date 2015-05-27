#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from datetime import datetime, timedelta
import subprocess
import os, shutil
import keen
import requests
import serial
import time
import re
import glob
import sys

CAMERA_ID = '001'
CAMERA_TYPE = 'Canon'
LOCAL_FOLDER = '/home/pi/cheese'
PHOTO_FOLDER = '/media/photo'
RAW_EXTENSION = 'cr2'
JPG_EXTENSION = 'jpg'
S3_BUCKET = "timelapse"

# POST_URL = ''
# keen.project_id = ''
# keen.write_key  = ''

POST_URL = "http://www.3pix.it/sistema/uploadfiles.asp?des=public/timelapse/test"
keen.project_id = '5544fbb946f9a7243e52688e'
keen.write_key  = '2b4658243ca3a0235b94b9d1b2be71abd32aee181ed55c75c1a14ba6287299f55de05d85a16fa1d9c310f4e61130be392360c8dda126caf0f66815a24d45ca12a52fa4c76ac9ac64776c729005a8ce35a042c343e2aae7181d799696623f7f2df466ae4b5e8a0ef6fb50c73cc439337e'


def log (message):
#	print datetime.utcnow(), message
	pass


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


def signalOnPin (pin, message):
	log(">>> %s" % message)
	command = ["gpio", "export", str(pin), "out"]
	result = subprocess.check_output(command)
	command = ["gpio", "-g", "write", str(pin), "1"]
	result = subprocess.check_output(command)
	time.sleep(1)
	command = ["gpio", "-g", "write", str(pin), "0"]
	result = subprocess.check_output(command)
	log("<<< %s" % message)
	

def turnCameraOn ():
	signalOnPin(23, "turning camera on")
	time.sleep(4)


def takePhoto (filename):
	log(">>> take photo")
	command = ["gphoto2", "--force-overwrite", "--capture-image-and-download", "--filename=%s.%%C" % filename]
	result = subprocess.check_output(command)
	log("<<< take photo")


def movePicture (filename):
	import traceback

	log(">>> move pictures")
	for extension in [RAW_EXTENSION]:
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
			log("exception: %s" % str(e))
			pass

		if os.path.isfile(targetFile):
			log("-> removing local file ...")
			os.remove(localFile)
			log("<- removing local file - DONE")
		else:
			raise Exception("something went wrong copying the file")
	log("<<< move pictures")


def resizeThumbnail (filename):
	log(">>> resize thumbnail")
	imageFile = "%s.%s" % (filename, JPG_EXTENSION)
	command = ["convert", imageFile, "-resize", "10%%", imageFile]
	result = subprocess.check_output(command)
	log("<<< resize thumbnail")

def sendThumbnailViaHttpPost (filename):
	log(">>> sendThumbnailViaHttpPost - %s" % filename)
	files = {'Filedata': (filename, open(filename, 'rb'), 'image/jpeg')}
	headers = {
		'Accept-Encoding': 'gzip, deflate',
		'Accept': '*/*',
		'Accept-Language': 'en-us'
	}

	request = requests.Request('POST', POST_URL, files=files, headers=headers)
	preparedRequest = request.prepare()

	session = requests.Session()
	response = session.send(preparedRequest)
	log("<<< sendThumbnailViaHttpPost - %s" % response.status_code)

	return response


def sendThumbnails ():
	log(">>> send thumbnail")
	for file in glob.glob("*.%s" % JPG_EXTENSION):
		try:
			response = sendThumbnailViaHttpPost(file)
			if response.status_code == 200:
				log("--- removing thumbnail file %s" % file)
				os.remove(file)
		except:
			log("error uploading file")
			pass
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
	process = subprocess.Popen(["./usbDevice", "Prolific"], stdout=subprocess.PIPE)
	(output, err) = process.communicate()
	exit_code = process.wait()
	
	device = output.rstrip()
	log("serial connector device: %s" % device)
	data = serial.Serial(device, 9600).readline()
	log("serial data: %s" % data)
	
	return data


def convertDiskSpace (value):
	return (value.f_bavail * value.f_frsize) / 1024 / 1024


def collectStats (filename):
	log(">>> collect stats")
	now = datetime.now()

	statInfo = readLineFromSerialPort()
	match = re.search(r"[^\d]*(\d*):(\d*):(\d*)\s*[^\d]*([\d\.]*)[^\d]*([\d\.]*)", statInfo)
	
	hours = int(match.group(1))
	minutes = int(match.group(2))
	seconds = int(match.group(3))
	batteryLevel = float(match.group(4))
	temperature = float(match.group(5))

	time = now.strftime('%Y-%m-%d') + "T" + "%02d:%02d:%02d" % (hours, minutes, seconds) + ".000Z"
	raspberryTime = now.strftime('%Y-%m-%dT%H:%M:%S.000Z')

	rawSize = os.path.getsize("%s/%s.%s" % (PHOTO_FOLDER, filename, RAW_EXTENSION))
	
	bootAvailableSpace = convertDiskSpace(os.statvfs('/'))
	photoAvailableSpace = convertDiskSpace(os.statvfs(PHOTO_FOLDER))
	
	stats = {
		"environment": [ {
			"camera":       CAMERA_ID,
			"temperature":  temperature,
			"batteryLevel": batteryLevel,
			"time": time
		} ],
		"image": [ {
			"camera":   CAMERA_ID,
			"name":     filename,
			"rawSize":  rawSize
		} ],
		"raspberry": [ {
			"camera":   CAMERA_ID,
			"boot":     bootAvailableSpace,
			"photo":    photoAvailableSpace,
			"dateTime": raspberryTime
		}]
	}
	log("<<< collect stats")
	
	return stats


def sendStats (stats):
	log(">>> send stats")
	keen.add_events(stats)
	log("<<< send stats")


def signalShuttingDown ():
	signalOnPin(18, "signal shutting down")


def shutdown ():
	log(">>> shutting down")
	os.system('sudo shutdown now -h')
	log("<<< shutting down")


def cheese (filename):
	turnCameraOn()
#	resetUsb(CAMERA_TYPE)
	takePhoto(filename)
	movePicture(filename)
	resizeThumbnail(filename)
	connectGPRS()
	sendThumbnails()
	sendStats(collectStats(filename))
	disconnectGPRS()


def main ():
	now = datetime.now()
	filename = now.strftime('%Y-%m-%d_%H%M%S')
	log("Filename: %s" % filename)

	try:
		cheese (filename)
	finally:
		signalShuttingDown()
		shutdown()
		pass


if __name__ == "__main__":
#	log("readline: %s" % readLineFromSerialPort())
	main()
