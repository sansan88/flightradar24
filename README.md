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


# Flightradar24 KNOWLEDGE BASE
- Installation Guide [PDF download](https://www.flightradar24.com/files/Documentation%20-%20Installation%20Guide.pdf)
- T-FEED MANUAL [PDF download]()
- FR24 FEEDER STATISTICS [PDF download](https://repo-feed.flightradar24.com/fr24feed-manual.pdf)
- ADS-B ANTENNA [PDF download](https://www.flightradar24.com/files/positioning_mode-s_antenna.pdf)
- Receiver [PDF download](https://www.flightradar24.com/files/Equipment_Instruction.pdf)


# Internal Webserver
based on the [dump1090](https://github.com/SDRplay/dump1090/blob/master/README-json.md) repository. For more information checkout the readme file [here](https://github.com/SDRplay/dump1090/blob/master/README-json.md).




**Map**

`http://IP-of-Pi/dump1090/gmap.html`

**Receiver**

`http://IP-of-Pi/dump1090/data/receiver.json`

**Aircrafts**

`http://IP-of-Pi/dump1090/data/aircraft.json`

**Stats**
    
`http://IP-of-Pi/dump1090/data/stats.json`

# Config files
Config file location ADS-B:  
    
`/etc/fr24feed.ini`

**Web interfaceADS-B:**

`http://IP-of-Pi:8754`

**Log file ADS-B** 
(run the following command on your Pi to view logs. CTRL+C to stop): 
    
`journalctl -u fr24feed -f`


You can check FR24 Feeder’s status at any time by executing:

`fr24feed-status`