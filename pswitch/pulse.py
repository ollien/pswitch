import subprocess
import re


def get_sources():
    pacmd_output = subprocess.check_output("pacmd list-sources", shell=True)
    return parse_pacmd_list_output(pacmd_output)


def get_sinks():
    pacmd_output  = subprocess.check_output("pacmd list-sinks", shell=True)
    return parse_pacmd_list_output(pacmd_output)


# Will parse output from pacmd list-sinks and pacmd list-sources
def parse_pacmd_list_output(pacmd_output):
    raw_devices = re.split(r"\s\s(\s|\*)\sindex:\s(\d+)",
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
            # pacmd mixes tabs and spaces in its output. Go figure.
            device_name_match = re.search(r"\t\tdevice.description\s=\s\"(.*)\"", item)
            device_name = device_name_match.groups()[0]
            device = {
                        "pulse_index": current_index,
                        "device_name": device_name,
                        "active": is_current_active
                    }
            devices.append(device)
    return devices

def get_sink_input_indexes():
    pacmd_output = subprocess.check_output("pacmd list-sink-inputs", shell=True)
    return get_indexes_from_pacmd_output(pacmd_output)

def get_source_output_indexes():
    pacmd_output = subprocess.check_output("pacmd list-source-outputs", shell=True)
    return get_indexes_from_pacmd_output(pacmd_output)

# Will parse output from pacmd list-source-outputs and pacmd list-sink-outputs
def get_indexes_from_pacmd_output(pacmd_output):
    index_matches = re.finditer(r"\s{4}index:\s(\d+)", pacmd_output.decode("utf-8"))
    return [int(index.groups()[0]) for index in index_matches]

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
    subprocess.Popen(["pacmd", "move-source-output", output_index, source_index])

def set_default_sink(sink_index):
    if type(sink_index) == int:
        sink_index = str(sink_index)
    subprocess.Popen(["pacmd", "set-default-sink", sink_index])

def set_default_source(source_index):
    if type(source_index) == int:
        source_index = str(source_index)
    subprocess.Popen(["pacmd", "set-default-source", source_index])

def switch_to_sink(sink_index):
    set_default_sink(sink_index)
    inputs = get_sink_input_indexes()
    for input_index in inputs:
        set_sink_input(input_index, sink_index)

def switch_to_source(source_index):
    set_default_source(source_index)
    outputs = get_source_output_indexes()
    for output_index in outputs:
        set_source_output(output_index, source_index)
