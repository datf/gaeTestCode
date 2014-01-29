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
The incoming data simulator can be run with ```bash
python mock_data.py
```
