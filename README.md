# Flightradar24 Aircraft Tracker
Track aircraft with Raspberry Pi 4 and display new airplanes on a 32x32 LED Matrix

## Hardware Requirements

### Raspberry Pi Set
Complete set available at [Galaxus.ch](https://www.galaxus.ch/de/s1/product/raspberry-pi-4-model-b-entwicklungsboard-kit-13280963?supplier=406802)

- [Raspberry Pi 4 8GB Model B](https://www.galaxus.ch/de/s1/product/raspberry-pi-4-8g-model-b-entwicklungsboard-kit-13276941)
- [OKdo Raspberry Pi 4 Model B Case](https://www.galaxus.ch/de/s1/product/okdo-raspberry-pi-4-model-b-gehaeuse-entwicklungsboard-zubehoer-11268337)
- [Official Raspberry Pi 4 Power Adapter USB-C](https://www.galaxus.ch/de/s1/product/raspberry-pi-official-raspberry-pi-4-power-adapter-usb-c-schwarz-entwicklungsboard-zubehoer-11268330?supplier=406802)
- [16GB MicroSD Card with NOOBS](https://www.galaxus.ch/de/s1/product/raspberry-pi-16gb-microsd-karte-mit-noobs-microsd-16-gb-speicherkarte-6050625?supplier=406802)

### ADS-B Receiver
- [Nooelec NESDR SMArt v4 Bundle](https://www.amazon.de/dp/B01GDN1T4S/ref=pe_27091401_487024491_TE_item) - Premium RTL-SDR with aluminum case, 0.5PPM TCXO, SMA input & 3 antennas

### LED Display
- [Adafruit 32x32 RGB LED Matrix Panel - 4mm pitch](https://www.berrybase.ch/adafruit-32x32-rgb-led-matrix-panel-4mm-raster)
- [Adafruit RGB Matrix HAT + RTC for Raspberry Pi](https://www.amazon.de/dp/B00SK69C6E/ref=pe_27091401_487027711_TE_SCE_dp_i1)

## Installation

### 1. Operating System
Flash Raspberry Pi OS using Raspberry Pi Imager:
- **Image:** Raspberry Pi OS Lite (Bookworm, 64-bit, without Desktop)

### 2. Install Flightradar24 Feeder

```bash
sudo bash -c "$(wget -O - https://repo-feed.flightradar24.com/install_fr24_rpi.sh)"
sudo systemctl enable fr24feed
sudo systemctl restart fr24feed
```

**Configuration & Monitoring:**
- Config file: `/etc/fr24feed.ini`
- Web interface: `http://IP-of-Pi:8754`
- Check status: `fr24feed-status`
- View logs: `journalctl -u fr24feed -f`

### 3. Install FlightAware (dump1090-fa)

```bash
wget https://www.flightaware.com/adsb/piaware/files/packages/pool/piaware/f/flightaware-apt-repository/flightaware-apt-repository_1.2_all.deb
sudo dpkg -i flightaware-apt-repository_1.2_all.deb
sudo apt update
sudo apt install piaware dump1090-fa
sudo piaware-config allow-auto-updates yes
sudo piaware-config allow-manual-updates yes
sudo apt full-upgrade
sudo reboot
```

**Access:**
- Map: `http://IP-of-Pi:8080/`
- Aircraft data: `http://IP-of-Pi:8080/data/aircraft.json`

### 4. Install RGB Matrix Display

#### System Update
```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

#### Install Adafruit RGB Matrix Driver
```bash
curl https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/main/rgb-matrix.sh >rgb-matrix.sh
sudo bash rgb-matrix.sh
```

#### Clone and Build rpi-rgb-led-matrix
```bash
git clone https://github.com/hzeller/rpi-rgb-led-matrix.git ~/rpi-rgb-led-matrix
cd ~/rpi-rgb-led-matrix
make build-python
```

#### Install Python Dependencies
```bash
sudo apt install -y python3-pip python3-dev python3-pillow build-essential
cd ~/Flightradar/rpi-rgb-led-matrix/bindings/python
sudo python3 -m pip install --break-system-packages .
```

#### Copy Font Folder (no more used)
```bash
cp -r ~/rpi-rgb-led-matrix/fonts ~/Flightradar/fonts
```

#### Test the Display
```bash
python3 rgbtext.py --top="Top Line Text" --center="Center Line Text" --bottom="Bottom Line Text"
```

### 5. Setup Aircraft Tracking Script

Create the following files in your project directory based on github repo:
- `fetch_aircraft_data.py`
- `rgbtext.py`

**Configuration values for `fetch_aircraft_data.py`:**
- API URL: `http://IP-of-Pi:8080/data/aircraft.json`
- DB folder: `/usr/share/skyaware/html/db`

### 6. Create System Service

Create service file:
```bash
sudo nano /lib/systemd/system/fetch_aircraft_data.service
```

Use the contents from `fetch_aircraft_data.service` in this repository.

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable fetch_aircraft_data.service
sudo reboot
```

## Maintenance

### Update Aircraft Database
```bash
git clone https://github.com/flightaware/dump1090.git
sudo cp -r dump1090/public_html/db /usr/share/skyaware/html/db
```

## Alternative Setup: Using dump1090-mutability

If you prefer using dump1090-mutability instead of dump1090-fa:

### Switching from dump1090-mutability to dump1090-fa

1. Remove dump1090-mutability:
```bash
sudo apt purge dump1090-mutability
```

2. Install dump1090-fa (follow step 3 above)

3. Update Flightradar24 configuration:
```bash
sudo nano /etc/fr24feed.ini
```

Change receiver settings:
```ini
receiver="avr-tcp"
host="127.0.0.1:30002"
```

4. Restart services:
```bash
sudo systemctl restart fr24feed
sudo systemctl restart dump1090-fa
sudo reboot
```

### Configuration Files

**dump1090-fa config:** `/etc/default/dump1090-fa`
```bash
sudo nano /etc/default/dump1090-fa
sudo systemctl restart dump1090-fa
```

**Webserver config:** `/etc/lighttpd/conf-available/89-skyaware.conf`

### Data Endpoints

**dump1090-mutability:**
- Map: `http://IP-of-Pi/dump1090/gmap.html`
- Data: `http://IP-of-Pi/dump1090/data/aircraft.json`
- API URL config: `http://IP-of-Pi/dump1090/data/aircraft.json`
- DB folder config: `/usr/share/dump1090-mutability/html/db`

**dump1090-fa:**
- Map: `http://IP-of-Pi:8080/`
- Data: `http://IP-of-Pi:8080/data/aircraft.json`
- API URL config: `http://IP-of-Pi:8080/data/aircraft.json`
- DB folder config: `/usr/share/skyaware/html/db`

## Additional Resources

### Official Documentation
- [Flightradar24: Build Your Own ADS-B Receiver](https://www.flightradar24.com/build-your-own)
- [Adafruit RGB Matrix HAT Assembly](https://learn.adafruit.com/adafruit-rgb-matrix-plus-real-time-clock-hat-for-raspberry-pi/assembly)
- [Adafruit RGB Matrix HAT - Driving Matrices](https://learn.adafruit.com/adafruit-rgb-matrix-plus-real-time-clock-hat-for-raspberry-pi/driving-matrices)
- [dump1090 JSON Format](https://github.com/SDRplay/dump1090/blob/master/README-json.md)

### Flightradar24 Knowledge Base
- [Installation Guide (PDF)](https://www.flightradar24.com/files/Documentation%20-%20Installation%20Guide.pdf)
- [FR24 Feeder Manual (PDF)](https://repo-feed.flightradar24.com/fr24feed-manual.pdf)
- [ADS-B Antenna Positioning (PDF)](https://www.flightradar24.com/files/positioning_mode-s_antenna.pdf)
- [Receiver Equipment Instructions (PDF)](https://www.flightradar24.com/files/Equipment_Instruction.pdf)

### Additional Services
- [ADS-B Database](https://www.adsbdb.com/)
