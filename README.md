# Inky Resource Monitor

This Python retrieves system statistics and then displays it on a Inky Phat made 
by [Pimoroni](https://github.com/pimoroni/inky). The tools uses Python 3.7, the
Inky, Pillow, gpustat and some default Python libraries to achieve this. 

You can run this on your Raspberry Pi as an standalone (local), or run it
in a server-display mode with your PC and Raspberry Pi respectively.

## Required arguments 
The following argument must be used:

````  --mode {local,server,display} ````

Specify whether you want to run this program as either, a local instance on a 
Raspberry Pi (Zero), as a server on your PC or as only a display for a Rpi.
## Optional arguments
This argument can be used if you wish: 

````[--refreshrate REFRESHRATE]````

The refreshrate in seconds, if it is lower than the time it takes to refresh the screen it will
just work as fast as possible. i.e. 60

## Optional for local, Required for Server

If you wish to use server and display mode, you must specify the following two arguments for the server:
	
```` [--ssh_adress SSH_ADRESS] ````

Please specify the adress of the raspberry pi if you use server mode, and ensure
that you have copied your public ssh to the RPi. Or alteratively type your password.
An example is: "Karel@192.168.1.2" if the username and ip on the pi are "Karel" and 192.168.1.1 respectively
```` [--path PATH] ````

Please specify the path of the monitor.py on the Raspberry Pi if you use it as display:
i.e. /home/Karel/inky_resource_monitor
## Optional for the Server
If you have an Nvidia GPU you can use the following on both gpu and display:

```` [--gpu GPU] ````

If this is true, the server script will try to monitor gpu resources and
the display will try to display them. False by default, enable it using True.

## Example 
To run it in server and display mode:
On the pc with a nvidia GPU:
```` 
python3 monitor.py --mode=server --ssh_adress=pi@192.168.1.100 --gpu=True
````
And then on the Raspberry Pi:
````
python3 monitor.py --mode=display --gpu=True
````

Please see the license in the license file.
