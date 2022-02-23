#!/usr/bin/python3

# this script is a modified version of 
# https://askubuntu.com/questions/1035718/how-change-display-scale-from-the-command-line-in-ubuntu-18-04-xorg

# best docs for mutter dbus monitor management is in the source code for the api which is here
# https://github.com/GNOME/mutter/blob/b5f99bd12ebc483e682e39c8126a1b51772bc67d/data/dbus-interfaces/org.gnome.Mutter.DisplayConfig.xml

import dbus
import sys

def get_monitor_modes(connectors):
    # This will print all supported modes of each connected monitor,
    # that way you can hard code you own display name and mode preferences
    for monitor_index, connector in enumerate(connectors):
        for mode_index, mode in enumerate(connected_monitors[monitor_index][1]):
            # connector is  a dbus.String
            # mode[0] is a dbus.Struct
            print(f'[{monitor_index}] {connector} \t [{mode_index}] {mode[0]}')


def get_monitor_dict(connectors, connected_monitors):
    mon_dict = {}
    for monitor_index, connector in enumerate(connectors):
        mon_dict[monitor_index] = {connector: []}
        for mode_index, mode in enumerate(connected_monitors[monitor_index][1]):
            mon_dict[monitor_index][connector].append(mode)
    return mon_dict

def get_monitor_conf(monitors, args, connectors):
    updated_connected_monitors = dbus.Array([])
    offset = 0
    for monitor_index, mode_index in enumerate(args):
        connector = connectors[monitor_index]
        desired_mode = monitors[monitor_index][dbus.String(connectors[monitor_index])][mode_index][0]
        this_mon_conf = dbus.Array([connector, desired_mode, dbus.Array({})])
        updated_connected_monitors.append(this_mon_conf) 
    return updated_connected_monitors


def print_usage():
        print(f'Usage: ./{__file__.split("/")[-1]} 2 0 5 2.0')
        print('this initiate the following changes:')
        print('monitor index 0 will assume its  mode 2,')
        print('monitor index 1 will assume its  mode 0,')
        print('monitor index 2 will assume its  mode 5.')
        print('all monitors would have 200% scaling.')
        print()


if __name__ == '__main__':
    print()

    # get user input
    args = [int(i) for i in sys.argv[1:-1]]
    scale = dbus.Double(sys.argv[-1])
    if scale not in [dbus.Double(1.0), dbus.Double(2.0)]:
        print('last argument is for scale, expected either 1.0 or 2.0')
        print_usage()
        exit()


    # set up the environment
    namespace = "org.gnome.Mutter.DisplayConfig"
    dbus_path = "/org/gnome/Mutter/DisplayConfig"
    session_bus = dbus.SessionBus()
    obj = session_bus.get_object(namespace, dbus_path)
    interface = dbus.Interface(obj, dbus_interface=namespace)

    current_state = interface.GetCurrentState()
    serial = current_state[0]
    connected_monitors = current_state[1]
    logical_monitors = current_state[2]

    connectors = [i[0][0] for i in connected_monitors]

    # if the user doesn't pass any args, just print their possibile configs and quit.
    if len(args) < 2:
        monitor_modes = get_monitor_modes(connectors)
        print_usage()
        exit()

    # we have args. parse the monitor configs.
    monitors = get_monitor_dict(connectors, connected_monitors)

    # display what profiles we plan on applying to each monitor
    for monitor_index, mode_index in enumerate(args):
        print(f'setting {connectors[monitor_index]} to ', end = '')
        print(f'{monitors[monitor_index][connectors[monitor_index]][mode_index][0]}')

    # get the dbus properties of the monitors we're updating
    updated_connected_monitors = get_monitor_conf(monitors, args, connectors)

    monitor_config = dbus.Array({})
    for index, logical_monitor in enumerate(logical_monitors):
        x, y, _scale, transform, primary, monitors, props = logical_monitor

        # if this is set, the config will be written to disk.
        persistent = dbus.UInt32(1)

        # uua(iiduba(ssa{sv}))a{sv}
        config = dbus.Struct(
                [
                    x, 
                    y, 
                    scale, 
                    transform, 
                    primary, 
                    dbus.Array([
                        dbus.Struct(updated_connected_monitors[index])
                    ])
                ]
        )

        monitor_config.append(config)

    ## Set the config :D
    # all args are types
    # uua(iiduba(ssa{sv}))a{sv}
    interface.ApplyMonitorsConfig(serial, persistent, monitor_config, {})

