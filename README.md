# flightradar24
Track Aircrafts with Raspberry Pi 4 and show new Airplanes on 32x32 LED Display

## Setup

**Raspberry Pi Set [Buy at Galaxus.ch](https://www.galaxus.ch/de/s1/product/raspberry-pi-4-model-b-entwicklungsboard-kit-13280963?supplier=406802):**
- Raspberry Pi 4 8G Model B [Buy at Galaxus.ch](https://www.galaxus.ch/de/s1/product/raspberry-pi-4-8g-model-b-entwicklungsboard-kit-13276941)
- OKdo Raspberry Pi 4 Model B Gehäuse [Buy at Galaxus.ch](https://www.galaxus.ch/de/s1/product/okdo-raspberry-pi-4-model-b-gehaeuse-entwicklungsboard-zubehoer-11268337)
- Raspberry Pi Official Raspberry Pi 4 Power Adapter USB-C Schwarz [Buy at Galaxus.ch](https://www.galaxus.ch/de/s1/product/raspberry-pi-official-raspberry-pi-4-power-adapter-usb-c-schwarz-entwicklungsboard-zubehoer-11268330?supplier=406802)
- Raspberry Pi 16GB MicroSD Karte mit Noobs [Buy at Galaxus.ch](https://www.galaxus.ch/de/s1/product/raspberry-pi-16gb-microsd-karte-mit-noobs-microsd-16-gb-speicherkarte-6050625?supplier=406802)

**Tracker:**
- Nooelec NESDR SMArt v4 Bündel - Premium RTL-SDR mit Aluminiumgehäuse, 0,5PPM TCXO, SMA Input & 3 Antennen. RTL2832U & R820T2-basierte Software Defined Radio [Buy at amazon.de](https://www.amazon.de/dp/B01GDN1T4S/ref=pe_27091401_487024491_TE_item)

**Display:**
- Adafruit 32x32 RGB LED Matrix Panel - 4mm Raster [Buy at berrybase.ch](https://www.berrybase.ch/adafruit-32x32-rgb-led-matrix-panel-4mm-raster)
- Adafruit RGB Matrix HAT + RTC für Raspberry Pi – Mini-Set  [Buy at amazon.de](https://www.amazon.de/dp/B00SK69C6E/ref=pe_27091401_487027711_TE_SCE_dp_i1)


## Tutorials
Good and straight forward tutorial for Raspberry Pi / Flightradar 24 
- Build your own ADS-B receiver [Flightradar24 Article](https://www.flightradar24.com/build-your-own)
- Adafruit Assembly [Docs](https://learn.adafruit.com/adafruit-rgb-matrix-plus-real-time-clock-hat-for-raspberry-pi/assembly)
- Adafruit Driving Matrices [Docs](https://learn.adafruit.com/adafruit-rgb-matrix-plus-real-time-clock-hat-for-raspberry-pi/driving-matrices)


# Flightradar24 Knowledge Base
- Installation Guide [PDF download](https://www.flightradar24.com/files/Documentation%20-%20Installation%20Guide.pdf)
- T-FEED MANUAL [PDF download]()
- FR24 FEEDER STATISTICS [PDF download](https://repo-feed.flightradar24.com/fr24feed-manual.pdf)
- ADS-B ANTENNA [PDF download](https://www.flightradar24.com/files/positioning_mode-s_antenna.pdf)
- Receiver [PDF download](https://www.flightradar24.com/files/Equipment_Instruction.pdf)

# Flightradar24 config files
Config file location ADS-B:  
    
`/etc/fr24feed.ini`

**Web interfaceADS-B:**

`http://IP-of-Pi:8754`

**Log file ADS-B** 
(run the following command on your Pi to view logs. CTRL+C to stop): 
    
`journalctl -u fr24feed -f`


You can check FR24 Feeder’s status at any time by executing:

`fr24feed-status`

# Flightradar Installtion Script

`sudo bash -c "$(wget -O - https://repo-feed.flightradar24.com/install_fr24_rpi.sh)"
sudo systemctl enable fr24feed
sudo systemctl restart fr24feed`


# dump1090
based on the [dump1090](https://github.com/SDRplay/dump1090/blob/master/README-json.md) repository. For more information checkout the readme file [here](https://github.com/SDRplay/dump1090/blob/master/README-json.md).

## Map
you find the Map here: `http://IP-of-Pi/dump1090/gmap.html`

## dump1090-fa Data
the Data for the Map is located here:

- `http://IP-of-Pi/dump1090/data/receiver.json`

- `http://IP-of-Pi/dump1090/data/aircraft.json`
  
- `http://IP-of-Pi/dump1090/data/stats.json`

# dump1090-fa
Another dataset you can use is the dump1090-fa Flightaware. To change from Dump1090 to dump1090-fa, please follow this steps (from this [Blog](https://forum.flightradar24.com/forum/radar-forums/flightradar24-feeding-data-to-flightradar24/221972-how-to-correctly-replace-dump1090-mutability-with-dump1090-fa)). 

This does NOT install PiAware - but only the dump1090-fa. If you wanna install PiAware, please follow this [Guide](https://www.flightaware.com/adsb/piaware/install).

## Installation Guide from Blog above.
1. Remove Dump1090 and it's config files: 

    `sudo apt purge dump1090-mutability`

2. Download Flightaware

    `wget https://www.flightaware.com/adsb/piaware/files/packages/pool/piaware/f/flightaware-apt-repository/flightaware-apt-repository_1.2_all.deb`

3. Unpack FLightaware and Install packages

    `sudo dpkg -i flightaware-apt-repository_1.2_all.deb`

    `sudo apt update`

    `sudo apt install dump1090-fa`

4. Change config files

    `sudo nano /etc/fr24feed.ini`

    Change from: 

    `receiver="dvb-t"`

    to 
    `receiver="avr-tcp"`

    add host: `host="127.0.0.1:30002"`

5. Reboot you Raspberry Pi

    `sudo reboot`

6. Change config file of dump1090-fa if needed:

    `sudo nano /etc/default/dump1090-fa`

    Restart if needed: `sudo systemctl restart dump1090-fa`

7. Change webserver config file if needed:
    `nano /etc/lighttpd/conf-available/89-skyaware.conf `


## Map
you find the Map here: `http://IP-of-Pi:8080/`

## dump1090-fa Data
the Data for the Map is located here:

`http://IP-of-Pi:8080/data/aircraft.json`


`http://IP-of-Pi:30005/dump1090-fa/data/aircraft.json`

# Fetch Aircraft Data script config values
based on the dum1090 variant you use, there is a different configuration needed.

## dump1090
- `api_url = "http://IP-of-Pi/dump1090/data/aircraft.json"`
- `db_folder = "/usr/share/dump1090-mutability/html/db"`

## dump1090-fa
- `api_url = "http://IP-of-Pi:8080/data/aircraft.json"`
- `db_folder = "/usr/share/skyaware/html/db"`


# Setup a Service
- Create a service file
`sudo nano /lib/systemd/system/fetch_aircraft_data.service`

- File see: "fetch_aircraft_data.service"

- call to reload deamon 
    
    `sudo systemctl daemon-reload`
- enable service with: 

    `sudo systemctl enable fetch_aircraft_data.service`

- Reboot pi `sudo reboot`

# Additional Service
https://www.adsbdb.com/

# Install RGB Matrix

https://learn.adafruit.com/adafruit-rgb-matrix-plus-real-time-clock-hat-for-raspberry-pi/driving-matrices
## Install Script: 
https://learn.adafruit.com/adafruit-rgb-matrix-plus-real-time-clock-hat-for-raspberry-pi/install-using-script

`curl https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/main/rgb-matrix.sh >rgb-matrix.sh
sudo bash rgb-matrix.sh`

Copy rgbtext.py file to user/pi/home 
Copy font folder to /home/pi

Using the Python Library

Some Python examples are included in the rpi-rgb-led-matrix/bindings/python/samples directory. 


 TO TEST (in rpi-rgb-led-matrix/bindings/python/samples): 
 sudo python3 runtext.py -m=adafruit-hat --led-rows=32 --led-cols=64 --led-slowdown-gpio=4

 or directly with the runtext.py
 python3 rgbtext.py --top="Top Line Text" --center="Center Line Text" --bottom="Bottom Line Text"


 klar
hier die Schritte 1-4 als reines Markdown (wie README)

⸻

1) System aktualisieren

sudo apt update
sudo apt full-upgrade -y
sudo reboot

2) rpi-rgb-led-matrix klonen

git clone https://github.com/hzeller/rpi-rgb-led-matrix.git ~/Flightradar/rpi-rgb-led-matrix

3) C++ Library bauen

cd ~/Flightradar/rpi-rgb-led-matrix
make build-python

4) Python Bindings installieren

sudo apt install -y python3-pip python3-dev python3-pillow build-essential

cd ~/Flightradar/rpi-rgb-led-matrix/bindings/python
sudo python3 -m pip install --break-system-packages .

