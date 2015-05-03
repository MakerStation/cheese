# cheese

tool to take and process pictures with a DSLR camera, using a Raspberry PI.

This tools has been created to support the creation of a timelapse video that should last more than 16 months.


## usbreset.c

This module was copied from the (dwiel/gphoto2-timelapse)[https://github.com/dwiel/gphoto2-timelapse/blob/master/usbreset.c] project 

To compile it, just run

'''
	cc usbreset.c -o usbreset
'''


## rc.cheese
Instructions to start the script on Raspberry boot also taken from the gphoto2-timelapse project

There is also an rc script which you can use to start the timelapse script automatically whenever the computer (raspberry pi) is turned on.  To setup this feature run the following commands:

sudo ln ./rc.cheese /etc/init.d/rc.cheese
cd /etc/init.d/
sudo update-rc.d rc.cheese defaults
