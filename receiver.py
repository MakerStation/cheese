#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import tornado.web
import tornado.ioloop
import os

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)

UPLOAD_FOLDER = '/Users/giulio.cesare/Workarea/MakerStation/cheese/uploads'

class Receiver(tornado.web.RequestHandler):

	def post (self):
		files = self.request.files
		for fileKey in files:
			for fileData in files[fileKey]:
				file = open(os.path.join(UPLOAD_FOLDER, fileData['filename']), 'wb')
				file.write(fileData['body'])
		self.write("uploaded")


def main():
	tornado.options.parse_command_line()

	application = tornado.web.Application([(r"/submit", Receiver)])
	application.listen(options.port)

	tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
	main()
