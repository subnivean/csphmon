#!/bin/bash

# Take a picture with the Raspi Camera. Make sure to turn on the overhead light first!

raspistill -o foo.jpg -t 1 \
   && ~/github/Dropbox-Uploader/dropbox_uploader.sh upload \
        foo.jpg \
        bar_$(echo $(date --iso-8601=seconds)|cut -d'-' -f1-3).jpg \
   && rm -f foo.jpg
