## Inky Resource Monitor

This Python retrieves system statistics and then displays it on a Inky Phat made 
by [Pimoroni](https://github.com/pimoroni/inky). The tools uses Python 3.7, the
Inky, Pillow, gpustat and some default Python libraries to achieve this. 

The following arguments can be used:
*  --mode {local,server,display} 

Specify whether you want to run this program as either, a local instance on a 
Raspberry Pi (Zero), as a server on your PC or as a pure display on a Rpi.
	
* [--ssh_adress SSH_ADRESS] 

Please specify the adress of the raspberry pi if you use server mode, and ensure
that you have copied your public ssh to the RPi. Or alteratively type your password.
An example is: "Karel@192.168.1.2" if the username and ip on the pi are "Karel" and 192.168.1.1 respectively
* [--path PATH] 

Please specify the path of the monitor.py on the Raspberry Pi if you use it as display:
i.e. /home/Karel/inky_resource_monitor

[--refreshrate REFRESHRATE]

The refreshrate in seconds, if it is lower than the time it takes to refresh the screen it will
just work as fast as possible. i.e. 60

 [--gpu GPU]

If this is true, the server script will try to monitor gpu resources and
the display will try to display them. False by default, enable it using True.

Please see the license in the license file.
