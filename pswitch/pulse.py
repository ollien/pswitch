import subprocess
import re

# Regex used to find the index of devices in pacmd list-sinks,
# pacmd list-sources, pacmd list-source-outputs and pacmd list-sink-outputs
# It's worth nothing that this regex requires spaces, while other regexes
# require tabs. Go figure.
DEVICE_INDEX_REGEX = re.compile(r"\s\s(\s|\*)\sindex:\s(\d+)")
# Regex used to pull the device name (or description, as Pulse calls it) from
# pacmd list-sinks and pacmd list-sources.
DEVICE_DESCRIPTION_REGEX = re.compile(r"\t\tdevice.description\s=\s\"(.*)\"")


def get_sources():
    """Get all sources from Pulse Audio.

    Returns:
        Returns a list of dicts. Each dict contains the sink's index in
        Pulse Audio (with key 'pulse_index'), the source's name
        (with key 'device_name') and whether or not it's actively the
        default source (with key 'active').
    """

    pacmd_output = subprocess.check_output("pacmd list-sources", shell=True)
    return parse_pacmd_list_output(pacmd_output)


def get_sinks():
    """Get all sinks from Pulse Audio.

    Returns:
        Returns a list of dicts. Each dict contains the sink's index in
        Pulse Audio (with key 'pulse_index'), the sink's name (with key
        'device_name') and whether or not it's actively the default sink
        (with key 'active').
    """

    pacmd_output = subprocess.check_output("pacmd list-sinks", shell=True)
    return parse_pacmd_list_output(pacmd_output)


def parse_pacmd_list_output(pacmd_output):
    """Parse the output from pacmd list-sinks and pacmd list-sources.

    Args:
        pacmd_output (str): the output from either pacmd list-sinks
            or pacmd list-sources.

    Returns:
        Returns a list of dicts. Each dict contains the sink's/source's
        index in Pulse Audio (with key 'pulse_index'), the
        sink's/source's name (with key 'device_name') and whether or not
        it's actively the default source/sink (with key 'active').
    """

    raw_devices = re.split(DEVICE_INDEX_REGEX,
                           pacmd_output.decode("utf-8"))[1:]
    devices = []
    current_index = None
    is_current_active = False
    for index, item in enumerate(raw_devices):
        if index % 3 == 0:
            is_current_active = item == "*"
            continue
        elif index % 3 == 1:
            current_index = int(item)
            continue
        elif index % 3 == 2:
            device_name_match = re.search(DEVICE_DESCRIPTION_REGEX, item)
            device_name = device_name_match.groups()[0]
            device = {
                        "pulse_index": current_index,
                        "device_name": device_name,
                        "active": is_current_active
                    }
            devices.append(device)
    return devices


def get_single_sink(sink_index):
    if type(sink_index) == int:
        sink_index = str(sink_index)
    pacmd_output = subprocess.check_output("pacmd list-sinks", shell=True)
    return get_single_device_from_pacmd_output(pacmd_output, sink_index)


def get_single_source(source_index):
    """Get the details of the source with the index given by source_index

    Args:
        source_index (int): The index of the device of which the details
            should be retrieved
    Returns:
        Returns dict that contains the source's/sink's index in Pulse Audio
        (with key 'pulse_index'), the sink's/source's name (with key
        'device_name') and whether or not it's actively the default
        source (with key 'active').
    """

    if type(source_index) == int:
        source_index = str(source_index)
    pacmd_output = subprocess.check_output("pacmd list-sources", shell=True)
    return get_single_device_from_pacmd_output(pacmd_output, source_index)


def get_single_device_from_pacmd_output(pacmd_output, pulse_index):
    """Get the details of the sink/source with the index given by pulse_index

    Args:
        pacmd_output (bytes): output from pacmd list-sinks
            or pacmd list-sources
        pulse_index (int): The index of the device of which the details
            should be retrieved
    Returns:
        Returns dict that contains the source's/sink's index in Pulse Audio
        (with key 'pulse_index'), the sink's/source's name (with key
        'device_name') and whether or not it's actively the default
        sink/source (with key 'active').
    """

    single_index_regex = (r"\s\s(\s|\*)\sindex:\s{index}"
                          .format(index=pulse_index))
    decoded_output = pacmd_output.decode("utf-8")
    index_match = re.search(single_index_regex, decoded_output)
    if index_match is None:
        return None
    is_device_active = 'index_match.groups()[0] == "*"'
    # Get the index of the end of the match, and look for the device
    # name from there. re.search will find the first match, meaning
    # it will be the name of the device with the index pulse_index
    minimum_index = index_match.end(1)
    device_name = re.search(DEVICE_DESCRIPTION_REGEX,
                            decoded_output[minimum_index:]).groups()[0]
    device = {
                "pulse_index": pulse_index,
                "device_name": device_name,
                "active": is_device_active
            }
    return device


def get_sink_input_indexes():
    """Gets the indexes of all sinks.

    Returns:
        List of integers representing the indexes of the sink inputs.
    """

    pacmd_output = subprocess.check_output("pacmd list-sink-inputs",
                                           shell=True)
    return get_indexes_from_pacmd_output(pacmd_output)


def get_source_output_indexes():
    """Gets the indexes of all sources.

    Returns:
        List of integers representing the indexes of the source outputs.
    """

    pacmd_output = subprocess.check_output("pacmd list-source-outputs",
                                           shell=True)
    return get_indexes_from_pacmd_output(pacmd_output)


def get_indexes_from_pacmd_output(pacmd_output):
    """Parses output from pacmd list-source-outputs and pacmd list-sink-inputs.

    Args:
        pacmd_output (str): Otuput from pacmd list-sink-inputs or
            pacmd list-source-outputs.

    Returns:
        List of integers representing the indexes of the sink inputs or
        source outputs
    """

    index_matches = re.finditer(DEVICE_INDEX_REGEX,
                                pacmd_output.decode("utf-8"))
    return [int(index.groups()[1]) for index in index_matches]


def set_sink_input(input_index, sink_index):
    if type(input_index) == int:
        input_index = str(input_index)
    if type(sink_index) == int:
        sink_index = str(sink_index)
    subprocess.Popen(["pacmd", "move-sink-input", input_index, sink_index])


def set_source_output(output_index, source_index):
    if type(output_index) == int:
        output_index = str(output_index)
    if type(source_index) == int:
        source_index = str(source_index)
    subprocess.Popen(["pacmd", "move-source-output",
                      output_index, source_index])


def set_default_sink(sink_index):
    if type(sink_index) == int:
        sink_index = str(sink_index)
    subprocess.Popen(["pacmd", "set-default-sink", sink_index])


def set_default_source(source_index):
    if type(source_index) == int:
        source_index = str(source_index)
    subprocess.Popen(["pacmd", "set-default-source", source_index])


def switch_to_sink(sink_index):
    """Iterates through all sink inputs and moves them to the sink
    specified by sink_index.

    Args:
        sink_index (int): The index of the sink that inputs should
            be moved to.
    """

    set_default_sink(sink_index)
    inputs = get_sink_input_indexes()
    for input_index in inputs:
        set_sink_input(input_index, sink_index)


def switch_to_source(source_index):
    """Iterates through all source outputs and moves them to the source
    specified by source_index.

    Args:
        source_index (int): The index of the source that outputs should
            be moved to.
    """

    set_default_source(source_index)
    outputs = get_source_output_indexes()
    for output_index in outputs:
        set_source_output(output_index, source_index)
