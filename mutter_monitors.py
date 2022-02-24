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
            if mode[6].get("is-current", False):
                print(f'{connector} \t [*] {mode[0]}')
            else:
                print(f'{connector} \t [{mode_index}] {mode[0]}')
        print()

def get_monitor_dict(connectors, connected_monitors):
    mon_dict = {}
    for monitor_index, connector in enumerate(connectors):
        mon_dict[monitor_index] = {connector: []}
        for mode_index, mode in enumerate(connected_monitors[monitor_index][1]):
            mon_dict[monitor_index][connector].append(mode)
    return mon_dict


def print_usage():
    print(f'Usage: ./{__file__.split("/")[-1]} DP-1 1 HDMI-A-0 5 2.0')
    print('this would cause DP-1 to assume mode index 1, HDMI-A-0 to assume mode index 5,')
    print('all listed monitors would be assigned 200% scaling,')
    print('any undeclared monitors will retain their mode, but be assigned the new scaling.')
    print()


if __name__ == '__main__':
    print()


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
    if len(sys.argv) < 4:
        monitor_modes = get_monitor_modes(connectors)
        print_usage()
        exit()


    # test that we have the correct number of arguments, requires odd number
    args = sys.argv[1:]
    if len(args) % 2 == 0:
        # even number of args were passed
        print_usage()
        exit()

    # test whether scale arg is valid, always expected to be last argument.
    scale = dbus.Double(sys.argv[-1])
    if scale not in [dbus.Double(1.0), dbus.Double(2.0)]:
        print('last argument is for scale, epected either 1.0 or 2.0')
        print_usage()
        exit()

    # monitor mode monitor mode
    user_monitor_modes = args[0:-1]

    # populate user give monitor mode pairs into a dict.
    # if a user declares a monitor multiple times in args, the last given value will be used.
    user_monitor_dict = {}
    # zip(*[iter(user_monitor_modes)]*2) just iters through by two items at a time
    for monitor, mode in zip(*[iter(user_monitor_modes)]*2):
        user_monitor_dict[monitor] = int(mode)


    # we have args. parse the monitor configs.
    monitors = get_monitor_dict(connectors, connected_monitors)

    # here, we should check that the monitor names are valid
    # get a list of valid monitor names
    valid_monitors = []
    for key, value in monitors.items():
        for k, v in value.items():
            valid_monitors.append(str(k))

    # get a list of invalid monitors
    invalid_monitors = []
    for i in user_monitor_dict.keys():
        if i not in valid_monitors:
            invalid_monitors.append(i)

    # if there's any invalid monitors, print their names and exit.
    if invalid_monitors:
        for i in invalid_monitors:
            print(f'{i} is not a valid monitor name')

        print(f'valid monitor names are {valid_monitors}')
        print('exiting without attempting any changes.')
        exit()


    # this could probably be consolidated
    updated_connected_monitors = dbus.Array([])
    for monitor_data in connected_monitors:
        current_mon = monitor_data[0][0]
        if current_mon not in user_monitor_dict.keys():
            # Undeclared monitors will try to retain their settings.
            # get the current mode of the undeclared monitor
            for mode_ind, mode in enumerate(monitor_data[1]):
                if mode[6].get("is-current", False):
                    user_monitor_dict[str(current_mon)] = mode_ind

        current_mon_index = connected_monitors.index(monitor_data)
        connector = connectors[current_mon_index]
        prof_index = user_monitor_dict[current_mon]
        prof_description = monitor_data[1][prof_index][0]
        this_mon_conf = dbus.Array([connector, prof_description, dbus.Array({})])
        updated_connected_monitors.append(this_mon_conf)
        print(f'setting {current_mon} to {prof_description}')


    monitor_config = dbus.Array({})
    for logical_monitor in logical_monitors:
        x, y, _scale, transform, primary, monitors, props = logical_monitor

        # if this is set, the config will be written to disk.
        persistent = dbus.UInt32(1)

        # make sure we have the right index for the monitor
        indices = [i[0] for i in updated_connected_monitors]
        index = indices.index(monitors[0][0])

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


    print(f'monitor_config: {monitor_config}')

    ## Set the config :D
    # all args are types
    # uua(iiduba(ssa{sv}))a{sv}
    interface.ApplyMonitorsConfig(serial, persistent, monitor_config, {})

