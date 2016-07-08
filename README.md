# t3-guard 
A project for having a raspberry Pi watching a VW T3 camping bus against burglars.

Installation

## Django-Server

Install everthing in requirements.txt

```
sudo pip install -r requirements.txt
```

Then you will need to set up django local database for this project

```
./manage.py migrate
./manage.py loaddata initial_data.json
./manage.py createsuperuser
```
You can set any superuser name and password, but is is recommended to use the username ``admin`` with password ``admin`` so the autologin-middleware works. Userwise adapt middleware.py

## System setup

### DHCP
Need a dhcp-server to be configured to write if a new client connects
It is recommended to set-up and configure dnsmasqd and hostapd to work as an accesspoint. 
Add following line to ``/etc/dnsmasq.conf``:

```
dhcp-script=/home/pi/t3-guard/dhcp-status.sh
```
adapt the path to where your local installation lies. 

### Systemd setup
need to run checker.sh (as root) and server.sh at autostart


### Mopidy
Install Mopidy:
https://docs.mopidy.com/en/latest/installation/debian/#debian-install


### Upnp
Install upmpdcli
https://www.lesbonscomptes.com/upmpdcli/downloads.html
