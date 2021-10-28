# Morse Simulator Installation Guide

This guide contains a currently working method to install Morse Simulator and bypass the various conflicts.

# Table of contents
1. [Requirements](#requirements)
2. [Installing & activating the correct python version](#python)
3. [Installing Blender 2.79b](#blender)
4. [Installing Morse](#morse)

## Requirements <a name="requirements"></a>

-  Use Ubuntu 20.4 LTS
-  An installed version of git:\
`sudo apt install git`
-  An installed version of cmake:\
`sudo apt-get install cmake`



## Installing & activating the correct python version <a name="python"></a>

For this we'll use pyenv, if you allready have it installed skip to downloading & activating the version.

### Install dependencies
Enter this command into a terminal:
```
sudo apt-get update; sudo apt-get install --no-install-recommends make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev python-dev python3-numpy
```
### Installing Pyenv:
Clone pyenv to your computer\
``` 
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
```
Add pyenv to Path (you can copy this entire block into your terminal):
```
# the sed invocation inserts the lines at the start of the file
# after any initial comment lines
sed -Ei -e '/^([^#]|$)/ {a \
export PYENV_ROOT="$HOME/.pyenv"
a \
export PATH="$PYENV_ROOT/bin:$PATH"
a \
' -e ':a' -e '$!{n;ba};}' ~/.profile
echo 'eval "$(pyenv init --path)"' >>~/.profile

echo 'eval "$(pyenv init -)"' >> ~/.bashrc
```
Restart your session, you might even need to log out and back in.

### Download Python 3.5.3:
```
pyenv install 3.5.3
```
Activate the python version globally
```
pyenv global 3.5.3
```
Check if everything worked by checking the version like this:
```
python3 --version
#>>> Python 3.5.3
```

## Installing Blender 2.79b <a name="blender"></a>
Download **blender-2.79b-linux-glibc219-x86_64.tar.bz2** from https://download.blender.org/release/Blender2.79/

Extract it and add the blender version to your path by:
```
echo 'export PATH="{PATH OF YOUR EXTRACTED FOLDER HERE}:$PATH'>>~/.bashrc
```
Replace {PATH OF YOUR EXTRACTED FOLDER HERE} with for example **/home/Max-Mustermann/Documents/blender-2.79b-linux-glibc219-x86_64**\
Type `blender` into the terminal and make sure Blender 2.79b opens up

## Installing Morse <a name="morse"></a>
Download the 1.4Stable Branch from github as a .zip
https://github.com/morse-simulator/morse/releases/latest \
Unzip the folder and create a new terminal inside (The command line should read something like: **user@device:~/Documents/morse-1.4_STABLE$**) \
After that enter:
```
mkdir build && cd build 
```
and:
```
cmake ..
```
finally:
```
sudo make install
```
Now add Morse to your path with:
```
echo 'export PATH="usr/local/bin:$PATH'>>~/.bashrc
```
That should be it, now you can check if everything worked by entering:
```
morse check
``` 
It should say : **Your environment is correctly setup to run MORSE.**

Now you no longer need python 3.5.3 as your system interpreter. You can switch back using `pyenv global system`
