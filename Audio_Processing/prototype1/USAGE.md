# Instructions for testing

### 1. Follow the instructions in the Readme to setup a .venv with all required packages

After packages are installed, all the warnings for module imports should dissapear. and you should be able to run the program with the run button.
If you don't have a run button, you might not have python set up correctly. Check if its installed and check if you have the Python vscode extension enabled.

You can also use:
```bash
python memsv2.py COM5 --delay 1.5
```
Your port might not be COM5, and 1.5 provides the desired time before the recieved audio is played back.

### 2. Plug in the microcontroller with INMP441 Digital Mic. 
Make sure none of the jumper cables are loose
### 3. On your computer, Go to Settings > Bluetooth and Devices > Add Device. 
You should see a device named ESP32_Audio_Link. Click Connect. ESP32_Audio_Link should show up as Not Connected in Devices.
### 4. Go to Bluetooth and Devices > View More Devices > More Bluetooth Settings > COM PORTS. Record the "Outgoing" of ESP32_Audio_Link.
### 5. Run the python script with your COM port!

# Troubleshooting

Firs of all, these instructions have been tested only on Windows because thats the only OS I have installed. If you are using a different OS these instructions might be different so just figure it out or ask AI what to do

### If any of the cables come lose, reconnect them according to the following:  
![Pinout Labels](https://m.media-amazon.com/images/I/71CKqXDmOkL._AC_SX466_.jpg)

VDD->3V3  
GND->GND  
L/R->GND  
WS->GIOP 15  
SCK->GIOP 14  
SD->GIOP 32  


### ModuleNotFoundError
Make sure all packages are installed and your virtual environment is active.
### Cannot open Port
Make sure the ESP32 is on. Try resetting it by clicking the button labelled "EN". Make sure you are using the right port
### [Errno 2] No such file or directory
Make sure you are in the prototype1 folder in terminal. If you are in /sparcs, run
```bash
cd Audio_Processing/prototype1
```
then try again
### I am still seing module missing yellow squiggles
You might still be able to run the code but of you are still seeing no module, your Python interpreter might not be using .venv. Try <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>P</kbd> and search for Python: Select Interpreter. Pick .venv
### Can't hear anything and seeing buffered: 0s underruns: 0
This means that nothing is being sent on the port. Check if you are using the right port, the microcontroller is still on (red LED lit up) and on bluetooth whenever you run the script, ESP32_Audio_Link should show as connected. Maybe try removing and re-adding the device in bluetooth settings. You should always start the python script after the esp32 has been turned on, and has been connected in your computer's bluetooth settings and it has been assigned a Port.

