# ! /usr/bin/env python3

from . import pulse
import sys


# Print menu and get the index of the Pulse Audio device selected
def print_menu_and_get_device(device_type):
    """Print menu for pswitch based on the device_type.

    Args:
        device_type (str): must be "sink" or "source".

    Returns:
        Returns the index of the sink/source that was selected.
    """

    devices = None
    if device_type == "sink":
        devices = pulse.get_sinks()
        print("Available Pulse Audio sinks:")
    elif device_type == "source":
        devices = pulse.get_sources()
        print("Available Pulse Audio sources:")
    else:
        raise ValueError("device_type must be either sink or source")
    for index, device in enumerate(devices):
        print("\t{index}: {active_indicator}{name}".format(
            index=index,
            active_indicator="(active default) " if device["active"] else "",
            name=device["device_name"]))
    valid_input = False
    selection = None
    while not valid_input:
        selection = input("? ")
        valid_input = is_int(selection) and 0 <= int(selection) < len(devices)
    selection = int(selection)
    return devices[selection]


def is_int(n):
    try:
        int(n)
        return True
    except ValueError:
        return False


# Returns true if arg is "o", "output", "i", or "input"
def check_type_arg_validity(arg):
    """Checks if cli argument is either o, output, i, or input.

    Args:
        arg (str): cli argument to check validity of.

    Returns:
        bool
    """

    return arg.lower() in ("o", "output", "i", "input")


def main():
    """Main function for pswitch. Runs if __name__ == __main__. Is also default
    command line entry point in setup.py.
    """

    # Check if command is pulse-switcher.py i[nput] or o[utput]
    if len(sys.argv) == 2 and check_type_arg_validity(sys.argv[1]):
        if sys.argv[1].lower() in ("o", "output"):
            sink_index = print_menu_and_get_index("sink")
            pulse.switch_to_sink(sink_index)
        elif sys.argv[1].lower() in ("i", "input"):
            source_index = print_menu_and_get_index("source")
            pulse.switch_to_source(source_index)
    # Check if command is pulse-switcher.py i[nput] or o[utput] n
    elif (len(sys.argv) == 3 and is_int(sys.argv[2])
          and check_type_arg_validity(sys.argv[1])):
        if sys.argv[1].lower() in ("o", "output"):
            sink_name = pulse.get_single_sink(sys.argv[2])["device_name"]
            print("Switching to sink \"{}\"...".format(sink_name))
            pulse.switch_to_sink(int(sys.argv[2]))
        elif sys.argv[1].lower() in ("i", "input"):
            source_name = pulse.get_single_source(sys.argv[2])["device_name"]
            print("Switched to source \"{}\"...".format(source_name))
            pulse.switch_to_source(int(sys.argv[2]))
    else:
        print((
            "Usage: pswitch type [index]\n"
            "Where:\n"
            "    type is i[nput] or o[utput]\n"
            "    index is a pulse audio sink index or source index"))


if __name__ == "__main__":
    main()
