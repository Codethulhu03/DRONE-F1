# XU4 installation guide

This short guide describes how to set up an odroid XU4 board with Ubuntu until able to connect via ssh over WiFi to a created user

# Table of contents
1. [Getting started](#introduction)
2. [Operating system](#os)
3. [Connection](#connection)
4. [User creation](#user)

## Getting started <a name="introduction"></a>

To set up the XU4 four things are needed:
- HDMI display
- USB Keyboard
- USB WiFi adapter 
    - Drivers might need to be installed, depending on the adapter
    - e.g. D-Link DWA 131 adapters work out of the box
- microSD card (>4GB) to flash the OS to

## Operating system <a name="os"></a>

Download the newest ubuntu-xx.xx.x-x.xx-minimal-odroid-xu4-xxxxxxxx.img.xz file from the [odroid wiki](https://wiki.odroid.com/odroid-xu4/odroid-xu4).  
Flash the image to the microSD card (on windows use [balenaEtcher](https://www.balena.io/etcher/) others like [Rufus](https://rufus.ie) might not work).  
Insert the microSD card into the slot on the XU4 and set the boot switch to the microSD postition (in the direction of the HDMI port).  
Make sure the other devices mentioned above are connected correctly and power up the XU4.  
After some loading time (up to a few minutes) you should be greeted by a login message.  
Login using the default credentials (user: `root`, password: `odroid`)  

## Connection <a name="connection"></a>

Use `network-manager` to connect to a wifi network  
First check whether the device is detected:  
    `$ nmcli dev status`  
Scan the area for access points:  
    `$ nmcli dev wifi list`  
Connect to your access point:  
    `$ nmcli dev wifi connect <network-ssid> -a`  
Finally get your IP adress (for ssh):  
    `$ ip a`

## User creation <a name="User"></a>

Creating a user only involves two commands:  
`$ sudo useradd -s /bin/bash -d /home/<dirname> -m -G sudo <username>`  
where `<dirname>` is the home directory name and `<username>` the name used for the ssh connection.  
`$ sudo passwd <username>`  
