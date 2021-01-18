# csphmon
Crawl Space Pump House Monitoring and Control

Running on an RPi3 Model B with Raspbian OS

Clone into `/home/pi/pythaw`.

Note that you must copy `secrets_example.py` to `secrets.py` and modify
with actual data.

Invoked from `rc.local` as follows (TMP36 sensor):
```
cd /home/pi/pythaw && ./tmp36.py &
```

or this (DS18B20 sensor):
```
cd /home/pi/pythaw && ./ds18b20.py &
```
