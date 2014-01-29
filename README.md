Real Time Data
==============

Introduction
------------

Provided with the data from a Conveyor machine that included timestamp,
total weight moved and the status, this application displays the following:

- Last time when a status from the Conveyor Machine was received.
- Time elapsed since last reset.
- Weight that the machine has moved since the last reset.
- Weight move rate in lbs per second.
- Last status received from the machine.
- A graph marking the data received in the last minute, including reset.

A reset is provided to start the counting again. This actions is streamed to 
all clients looking at the web application.

Instructions for Running the Application
----------------------------------------

The web application runs on Google App Engine. You can go to the 
[downloads page](https://developers.google.com/appengine/downloads) to get
a copy of the latest SDK and instructions on how to get it working locally.
The file app.yaml is provided for using it with the dev_appserver.py script.
The incoming data simulator can be run with:
```bash
python mock_data.py
```

Entering Data
-------------

In order to integrate with the system for entering data, a HTTP POST request
has to be made to /opened containing the following HTTP parameters:
- **timestamp**: The timestamp of the machine (number of seconds since Jan 1st 
1970 at 00:00:00 UTC)
- **current_total_weight**: A double that indicates the total weight read on 
the machine.
- **status**: A string informing of the current status of the machine.

Interface
---------

A screen capture of the interface can be found under the screen_shot folder.
