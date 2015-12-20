# raspi-doorguard
Project for having a raspberry Pi watching the state of the entrance door. Backend organized with python and django.

A simple reed-relay magnetic switch checks the status of the door. 
Raspberry Pi is configured as a DHCP-server, which checks in the local LAN, if an authorized mobile-phone is present, 
if not, the alarm is triggered (can be either a siren or just sending an email). 
