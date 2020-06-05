# PyCasts
PyCasts is a small, lightweight audiobook & podcast client written in python3.

![PyCasts v1.0.0 libary UI](https://i.postimg.cc/vBk9zk3g/pycasts-screen.png)

## Features
- automatic timestamp saving, letting you play wherever you left off
- speed controls
- simple & clean ui
- ttk theming (sorta)
- automatic library sorting
- vlc based; supports almost all audio formats
- small in size
- easy to use

## Installation

### Linux

1. **Install vlc**

   In ubuntu this is done by executing `sudo apt install vlc`, other package managers will likely work similarly

2. **Download PyCasts**

   - Clone the repository (Option 1):
     Run `git clone https://github.com/mocchapi/PyCasts.git`
   - Download the latest release (Option 2):
     Go to the releases tab on github (found [here](https://github.com/mocchapi/PyCasts/releases)) & download the latest one. Dont forget to unzip!


3. **Install the libraries**

   In the directory you downloaded PyCasts to, run `pip3 install -r requirements.txt`, or in versions after 1.0 `pip3 install -r requirements-linux.txt`

4. **If needed, install python3-tk**

   If using Ubuntu, run `sudo apt install python3-tk`



### Windows

1. **Install vlc**

   Download & install VLC media player from [here](https://www.videolan.org/vlc/)
 
2. **Download PyCasts**

     Go to the releases tab on github (found [here](https://github.com/mocchapi/PyCasts/releases)) & download the latest one. Dont forget to unzip!

3. **Install the libraries**

     In the directory you downloaded PyCasts to, run `pip3 install -r requirements.txt`, or in versions after 1.0 `pip3 install -r requirements-nonlinux.txt`
