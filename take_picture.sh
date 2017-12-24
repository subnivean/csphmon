#!/bin/bash

# Take a picture with the Raspi Camera. Make sure to turn on the overhead light first!

filename=bar_$(echo $(date --iso-8601=seconds)|cut -d'-' -f1-3).jpg

#raspistill --ISO 3200 --shutter 8000000 -o foo.jpg -t 1 --exposure verylong --awb incandescent
raspistill -o foo.jpg -t 1 

/home/pi/github/Dropbox-Uploader/dropbox_uploader.sh upload foo.jpg $filename

rm -f foo.jpg
