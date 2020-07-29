
# AM43 Blind Drive Motor MQTT Controller

## Description
The AM43 by is a cheap generic Bluetooth enabled motor for opening and closing blinds. It is normally controlled by buttons on the device or through an Android or iOS app.
I is available under many brands, such as:

 - https://www.amazon.co.uk/BENEXMART-Motorized-Tranditional-Automation-Support/dp/B07TTMQT87
 - https://www.aliexpress.com/i/33044164435.html
 - https://www.ebay.com/c/12039030936

This program instead can be run on any device supporting Bluetooth LE (such as a Raspberry Pi 3 or 4) and communicates over MQTT for control and monitoring of the device.

## Background and License
Licensed under the GPLv3.

## Requirements

 - Docker compose
 - An MQTT server/broker.

For one time setup you also require:

 - Python 3 and pip

## Setup 
### New device
To connect a new device one time setup must be performed:

 1. Install the device in place as per the manufacturer instructions and turn it on.
 2.On the host machine, install the python requirements with `pip3 install -r requirements`
 2. Run `python3 onetimesetup.py`. This will detect the available nearby devices, and guide you through setting up the device, such as blind limits.

### Config File
To start the server a config file `vars.env` must be filled on, by copying and completing the template `vars.env.eg`. The fields are as follows:

|Variable|Description  |
|--|--|
|BLIND_MAC|The MAC address of the blind controller, obtained in the one time setup step above.|
|DEVICE_NAME|A human readable name that will form the MQTT topic used.|
|MQTT_USERNAME|The username of your local mqtt server|
|MQTT_PASSWORD|The password for your local mqtt server|
|MQTT_ADDRESS|The address of your local mqtt server. Note even if this is the same machine use the absolute IP not localhost, as docker point localhost inside itself, not to the host machine|
|MQTT_PORT|The port of your local mqtt server (typically 1883)|

## Running
Run a `docker-compose build` followed by `docker-compose up -d` to run and register the service to always restart. Use docker compose to control and monitor the app (https://docs.docker.com/compose/)

Create copied of `vars.env` and add further services to the `docker-compose.yml` to manage multiple devices.

## MQTT Interface

Once running the following subtopics are available:

- `DEVICE_NAME/bat`: Subscribe for the current battery fill percentage of the blind controller.
-  `DEVICE_NAME/pos` : Subscribe for the current position of the blind as a percentage of closure.
 - `DEVICE_NAME/ctrl`: Publish an integer between  0 and 100 to open/close the blind to that percentage. Publish here also pushes an update of `/bat` and `/pos`, and a null message will update without chaning the blind position

Note that the position in `/pos` returned after `/ctrl` is written will not reflect the final position published to control as the blind will still be adjusting. Post a null message to `/ctrl` after a short delay to ensure the correct battery level and position are posted.



