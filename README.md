# mutter_monitors
Sets monitor mode, works around some scaling issues that are present with xrandr. Supports one or multiple monitors (not tested with 3 or more).

# Display all connections

`python3 mutter_monitors.py`

The mode with the asterisk is currently selected.

```

HDMI-A-0 	 [*] 1920x1080@74.972503662109375
HDMI-A-0 	 [1] 1920x1080@60
HDMI-A-0 	 [2] 1920x1080@50
HDMI-A-0 	 [3] 1920x1080@59.940200805664062
HDMI-A-0 	 [4] 1680x1050@59.883251190185547
HDMI-A-0 	 [5] 1280x1024@60.019741058349609
HDMI-A-0 	 [6] 1440x900@59.901458740234375
HDMI-A-0 	 [7] 1280x800@59.9095458984375
HDMI-A-0 	 [8] 1152x864@75
HDMI-A-0 	 [9] 1280x720@60
HDMI-A-0 	 [10] 1280x720@50
HDMI-A-0 	 [11] 1280x720@59.940200805664062
HDMI-A-0 	 [12] 1024x768@70.069358825683594
HDMI-A-0 	 [13] 1024x768@60.003841400146484
HDMI-A-0 	 [14] 800x600@60.316539764404297
HDMI-A-0 	 [15] 800x600@56.25
HDMI-A-0 	 [16] 720x576@50

HDMI-A-1 	 [0] 1680x1050@59.954250335693359
HDMI-A-1 	 [*] 1920x1080@60
HDMI-A-1 	 [2] 1920x1080@50
HDMI-A-1 	 [3] 1920x1080@59.940200805664062
HDMI-A-1 	 [4] 1280x1024@75.024673461914062
HDMI-A-1 	 [5] 1280x1024@60.019741058349609
HDMI-A-1 	 [6] 1440x900@59.954250335693359
HDMI-A-1 	 [7] 1280x800@59.954250335693359
HDMI-A-1 	 [8] 1152x864@75
HDMI-A-1 	 [9] 1280x720@60
HDMI-A-1 	 [10] 1280x720@50
HDMI-A-1 	 [11] 1280x720@59.940200805664062
HDMI-A-1 	 [12] 1024x768@75.028579711914062
HDMI-A-1 	 [13] 1024x768@60.003841400146484
HDMI-A-1 	 [14] 800x600@75
HDMI-A-1 	 [15] 800x600@60.316539764404297
HDMI-A-1 	 [16] 720x576@50


```

# Set a named monitor to a mode, set global scaling.

`python3 mutter_monitors.py HDMI-A-0 8 1.0`

Scaling is a required argument. It expects 1.0 or 2.0. 

HDMI-A-0 mode will be changed to 1152x864@75.

HDMI-A-1 mode will be retained.

All monitors will be assigned 100% scaling.

This should retain whatever layout you had previously (extend/mirror/single).


# Set multiple monitor modes at once.

`python3 mutter_monitors.py HDMI-A-1 2 HDMI-A-0 16 2.0`

Order of monitors doesn't matter, but it expects the format Monitor Mode Monitor Mode ... scale_factor

HDMI-A-0 mode will be changed to 720x576@50

HDMI-A-1 mode will be changed to 1920x1080@50

All monitors will be assigned 200% scaling.

This should retain whatever layout you had previously (extend/mirror/single).



# Automation on Plug/Unplug

Use [udev rules](https://wiki.archlinux.org/title/Udev#Execute_when_HDMI_cable_is_plugged_in_or_unplugged).


# If you find any bugs or have feature requests, please don't hesitate to open an issue.



