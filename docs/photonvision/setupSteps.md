[Follow base instructions](https://docs.photonvision.org/en/latest/docs/installation/sw_install/raspberry-pi.html) for flashing the SD Card.

[Update the config.txt file to work with the ov9281 camera](https://docs.photonvision.org/en/latest/docs/hardware/picamconfig.html#updating-config-txt). The camera doesn't work by default without doing this, it'll just look like its unplugged. You'll need to comment out the cameraAutoDetect=1 line, and uncomment the dtoverlay=ov9281 line.

Discsonnect power from other raspberry pi's to ensure we're only configuring the one new device. Otherwise, there's a chance you'll pull up the wrong UI.

Put the SD card into the raspberry pi, power it on, and leave it on long enough to boot. The first boot might take a few minutes, as it's expanding the filesystem to fill the whole SD card. If you loose power during the operation, you may corrupt the card. Not the end of the world, but you'll have to reflash and start over.

Once booted, The main UI can be accessed in a browser at `http://photonvision.local:5800`. 

Change the following settings:

 * Set the team number to 1736 - this makes sure we will connect to the roboRIO and NT
 * Set a static IP address - It can work without this, but it'll help reduce time to connect
 * Change the ?? mdns responder name ?? to be specific to the camera - this makes the web address unique, so we don't have two coprocessors trying to serve a website at "photonvision.local"
 * Upload `hardwareConfig.json` in this same folder. - this just tells photonvision about the led's. 

Save and reboot and access the camera again via the web interface. Note the address will have changed to whatever you set the mdns address to. ex: `http://leftcam.local:5800`


Verify you can see the camera itself.

Go to the calibration tab, and calibrate the cameras. Use an 8x8 1" checkerboard. 

Configure the vision settings (see below) for the pipeline.

Make sure the Camera name is correct - this is what the code uses to reference which camera we're talking about (IE, the camera's name must be _exactly_ "LEFT_CAM", because that's what's in code).

Overall Settings:
Left Cam:
 * IP Address - `10.17.36.13`
 * mdns Name - `leftcam`
 * Camera name - `LEFT_CAM`

Right Cam:
 * IP Address - `10.17.36.12`
 * mdns Name - `rightcam`
 * Camera name - `RIGHT_CAM`

Spare Cam:
 * IP Address - `10.17.36.11`
 * mdns Name - `sparecam`
 * Camera name - `SPARE_CAM`

Common Vision Settings:
 * Aurco pipeline
 * 640x480 resolution
 * 3D mode
 * Lowest-possible exposure (minimize blur)
 * Just enough gain to make apriltags show up reliably at half-field distance
 * TBD.... other optimization for apriltag settings?